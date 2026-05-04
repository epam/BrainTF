from typing import Any, Dict, List

from config import config
from utilities.ai.chat_completions import generate_response_ai
from utilities.ai.context import create_context_memory_window
from utilities.ai.prompt import prepare_user_prompt_message
from utilities.aws import get_file_content_with_metadata_from_s3
from utilities.handlers import handle_ai_response_message
from utilities.logger import logger
from utilities.messages import AI_RESPONSE_MESSAGE
from utilities.vcs import post_comment


def process_s3_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processes an S3 event to extract relevant information, enrich it with metadata,
    and return the updated event data.

    The function extracts the S3 bucket name and object key from the event, retrieves
    the file content and metadata from the S3 object, and then constructs additional
    metadata information based on the content and system configuration. The enriched
    event data is returned for further use.

    Args:
        event (Dict[str, Any]): The event object containing details about the S3 event,
            typically following the AWS S3 event notification format.

    Returns:
        Dict[str, Any]The enriched event dictionary with additional metadata.
    """
    try:
        # Extract S3 bucket and object key from the event
        records = event.get('Records')
        if not isinstance(records, list) or not records:
            raise ValueError("S3 event is missing Records entries.")
        event_record: Dict[str, Any] = records[0]
        s3_bucket: str = event_record.get('s3', {}).get('bucket', {}).get('name')
        s3_key: str = event_record.get('s3', {}).get('object', {}).get('key')

        logger.info(f"Processing S3 event for bucket '{s3_bucket}' and key '{s3_key}'...")

        log_file_content_with_metadata: Dict[str, Any] = get_file_content_with_metadata_from_s3(s3_bucket, s3_key)

        log_file_content: str = log_file_content_with_metadata.get('content')

        file_metadata: Dict[str, str] = log_file_content_with_metadata.get('metadata')

        base_repo_owner: str = file_metadata.get('base_repo_owner')
        base_repo_name: str = file_metadata.get('base_repo_name')

        metadata: Dict[str, Any] = {}

        metadata.update({
            'repo_id_or_name': f"{base_repo_owner}/{base_repo_name}" if config.vcs_provider == 'gitlab' else base_repo_name,
            'source_branch': file_metadata.get('head_branch_name'),
            'log_file_content': (log_file_content or '').strip(),
            'prompt': '',
            'ai_response': '',
            'merge_or_pull_req_id': int(file_metadata.get('pull_num')),
            'commit_short_sha': file_metadata.get('commit_sha').strip()[:8],
            'tool_name': file_metadata.get('tool_name')
        })

        event.setdefault('metadata', {}).update(metadata)

        return event

    except Exception as error:
        logger.error(f"Error occurred while processing the S3 event: {str(error)}")
        raise error


def lambda_handler(event: dict[str, dict], context: Any) -> Dict[str, Any]:  # noqa:
    """AWS Lambda function handler."""

    try:
        process_s3_event(event)

        user_message: Dict = prepare_user_prompt_message(event)
        user_prompt: List = [user_message]

        generated_response: Dict[str, Any] = generate_response_ai(user_prompt)
        message: str = generated_response.get("message", "").strip()
        logger.info(f"Message to UI --->\n{message}")
        event.get("metadata").update({"ai_response": message})

        tool_name = event.get("metadata").get("tool_name")

        message = AI_RESPONSE_MESSAGE.format(tool_name=tool_name,
                                             ai_response=generated_response["message"],
                                             total_tokens=generated_response["tokens"]["total_tokens"],
                                             prompt_tokens=generated_response["tokens"]["prompt_tokens"],
                                             completion_tokens=generated_response["tokens"]["completion_tokens"])

        post_comment(event, message)

        handle_ai_response_message(event)
        create_context_memory_window(event)

        logger.info('Successfully invoked')


    except Exception as error:
        logger.error(f"Error occurred while invoking the Lambda function: {str(error)}")
        raise error
