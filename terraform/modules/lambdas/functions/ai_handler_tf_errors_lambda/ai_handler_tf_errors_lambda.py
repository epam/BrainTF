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
    Processes an incoming S3 event by extracting relevant details, fetching file content
    and metadata from the specified S3 bucket, and appending derived metadata to the event.

    This function assumes the event follows an AWS S3 trigger structure, processes the
    first record, and interacts with external systems to fetch S3 content and repository
    details. On successful completion, the function returns the modified event with added
    metadata, or raises an exception if processing fails.

    Args:
        event (Dict[str, Any]): The S3 event data containing information about the
            triggered event. Expected to include a list of 'Records' with
            details on the bucket and object.

    Returns:
        Dict[str, Any]: The modified event with additional metadata derived from the
        processed S3 object and its associated repository details.

    Raises:
        ValueError: When the event is missing required 'Records' entries or the structure
            is invalid.
        Exception: Propagates downstream errors from S3 access or metadata processing
            after logging them.
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

        log_file_content_with_metadata: Dict[str, Any] | None = get_file_content_with_metadata_from_s3(s3_bucket,
                                                                                                       s3_key)
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
        logger.error(f"Error occurred while processing the S3 event: {error}.")
        raise error


def lambda_handler(event: dict[str, dict], context: Any) -> Dict[str, Any]:  # noqa:
    """
    Handles an incoming Lambda event, processes input data, generates an AI response, and updates the output
    with results.

    The function orchestrates multiple operations, including event processing, AI response generation, logging,
    and data updating. It ensures all essential steps are covered for handling AI-driven tasks, while also
    providing error logging and raising exceptions in case of failures.

    Args:
        event (dict[str, dict]): The event dictionary containing the necessary metadata and payload information
            required for processing. It should include details such as the input message, metadata, and relevant
            context for generating the AI response.
        context (Any): Lambda context object that provides runtime information of the Lambda function being invoked,
            such as function name, memory allocation, and remaining execution time.

    Returns:
        Dict[str, Any]: A response dictionary containing the updated event information, including the AI-generated
            response message and any additional metadata or tokens related to the output.

    Raises:
        Exception: Any exception raised during processing or handling of the Lambda function will be logged and
            re-raised for further investigation.
    """
    try:
        process_s3_event(event)

        user_message: Dict = prepare_user_prompt_message(event)
        user_prompt: List = [user_message]
        generated_response: Dict[str, Any] = generate_response_ai(user_prompt)
        message: str = generated_response.get("message", "").strip()
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

        logger.info('Successfully invoked.')


    except Exception as error:
        logger.error(f"Error occurred while invoking the Lambda function: {error}.")
        raise error
