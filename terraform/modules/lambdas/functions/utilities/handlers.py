from typing import Any, Dict, List

from config import config
from utilities.ai.chat_completions import generate_response_ai
from utilities.ai.context import (create_context_memory_window,
                                  get_context_memory_window)
from utilities.aws import (delete_files_from_s3,
                           get_all_files_from_s3_directory,
                           get_file_names_from_s3_directory,
                           get_particular_files_from_s3_directory,
                           upload_files_to_s3)
from utilities.exceptions import InvalidEventMetadata
from utilities.logger import logger
from utilities.messages import (AI_RESPONSE_MESSAGE, HELP_MESSAGE,
                                LIST_FILES_MESSAGE)
from utilities.parsers import parse_hcl_blocks
from utilities.vcs import (FAILURE, SUCCESS, add_award_to_note,
                           check_files_exist_in_repo, commit_files_to_branch,
                           post_comment)


def handle_ai_response_message(event: Dict[str, Any]) -> None:
    """
    Handles the AI-generated response message, identifies HCL blocks, and processes them according
    to the associated pull/merge request.

    This function extracts the AI response message from the event metadata and processes it to locate
    HCL blocks. If valid HCL blocks are found, it performs associated operations like deleting old
    files from S3 and uploading new ones for the pull/merge request. Additionally, it logs relevant
    information for debugging purposes.

    Args:
        event (Dict[str, Any]): The event containing metadata, which includes the AI response message
            and merge/pull request ID.

    Raises:
        InvalidEventMetadata: If the required pull/merge request ID is not found in the event metadata.
    """
    response_message = event.get('metadata').get('ai_response')
    if not response_message:
        logger.debug("No response message from AI found in the event metadata.")
        return
    filenames_with_hcl_blocks: Dict[str, str] = parse_hcl_blocks(response_message)
    if filenames_with_hcl_blocks:
        logger.info(f"Found HCL blocks in the response: {filenames_with_hcl_blocks}")
        pull_number = event.get('metadata').get('merge_or_pull_req_id')
        if not pull_number:
            raise InvalidEventMetadata("Pull/Merge request ID not found in the event metadata.")
        path_to_artifacts = f"{config.path_to_artifacts}/{pull_number}/"
        delete_files_from_s3(config.artifacts_bucket, path_to_artifacts)
        logger.info(f"Uploading files to S3 bucket '{config.artifacts_bucket}' for PR #{pull_number}")
        upload_files_to_s3(config.artifacts_bucket, pull_number, filenames_with_hcl_blocks)


def handle_help_command(event: Dict[str, Any]):
    """Handle the 'help' bot command."""
    logger.info('Processing help command...')
    post_comment(event, HELP_MESSAGE)


def handle_comment_commands(event: Dict[str, Any]):
    comment_context, *rest_comment = event.get('metadata', {}).get('comment_text', '_').split()
    logger.info(f'Comment context --->  {comment_context}')
    if comment_context == 'bot':
        logger.info('Bot context found in the comment.')
        handle_bot_commands(event, rest_comment)

    elif comment_context == 'help' and not rest_comment:

        logger.info('Help context found in the comment.')
        add_award_to_note(event, SUCCESS)
        handle_help_command(event)

    else:
        logger.info('No actionable context found in the comment.')


def handle_list_command(event: Dict[str, Any]):
    """Handle the 'list' bot command."""
    logger.info('Processing list command...')
    merge_request_id = event.get('metadata').get('merge_or_pull_req_id')
    path_to_mr_artifacts = f"{config.path_to_artifacts}/{merge_request_id}/"
    file_names = get_file_names_from_s3_directory(config.artifacts_bucket, path_to_mr_artifacts)
    if file_names:
        files_list = '\n\n'.join(f"`{file_name}`" for file_name in file_names)
    else:
        files_list = '`..`'

    logger.info(f'Listing rest_comment: {files_list}')
    post_comment(event, LIST_FILES_MESSAGE.format(files_list=files_list))


def handle_bot_commands(event: Dict[str, Any], rest_comment: List[str]) -> None:
    """
    Processes bot commands extracted from a comment and delegates actions to appropriate handlers
    based on the command type. Updates the corresponding note or feedback mechanism depending on
    the command execution result.

    Args:
        event (Dict[str, Any]): Event data carrying context and metadata for the bot's operation, including
            details of the triggering interaction or note.
        rest_comment (List[str]): Remaining parts of the user comment after extracting the command, typically a list
            where the first element is the command type, and subsequent elements may provide additional arguments.
    """
    logger.info('Processing bot commands...')

    if rest_comment:
        command: str = rest_comment[0]
        rest_comment: List[str] = rest_comment[1:]

        if command == 'approve' and rest_comment:
            logger.info('Approve context found in the comment.')
            logger.info(f'Rest comment ---> {rest_comment}')
            handle_approve_command(event, rest_comment)

        elif command == 'list':
            logger.info('List context found in the comment.')
            add_award_to_note(event, SUCCESS)
            handle_list_command(event)

        elif command == 'prompt' and rest_comment:
            logger.info('Prompt context found in the comment.')
            add_award_to_note(event, SUCCESS)
            handle_prompt_command(event, rest_comment)
        else:
            logger.info(f'Unknown bot command: {command}')
            add_award_to_note(event, FAILURE)
    else:
        logger.info('No specific bot command provided.')
        add_award_to_note(event, FAILURE)


def handle_prompt_command(event: Dict[str, Any], rest_comment: List[str]):
    """Handle the 'prompt' bot command."""
    logger.info('Processing prompt command...')
    prompt = ' '.join(rest_comment)
    user_message = {'content': prompt, 'role': 'user'}
    messages_for_ai = get_context_memory_window(event) + [user_message]

    logger.info(f"Messages to AI ---> {messages_for_ai}")
    response = generate_response_ai(messages_for_ai)

    logger.info(f"Response from AI ---> {response}")

    event.get("metadata").update({"prompt": prompt})
    event.get("metadata").update({"ai_response": response["message"].strip()})

    ai_response_message_to_ui = AI_RESPONSE_MESSAGE.format(ai_response=response["message"],
                                                           total_tokens=response["tokens"]["total_tokens"],
                                                           prompt_tokens=response["tokens"]["prompt_tokens"],
                                                           completion_tokens=response["tokens"]["completion_tokens"])
    post_comment(event, ai_response_message_to_ui)
    handle_ai_response_message(event)
    create_context_memory_window(event)


def handle_approve_command(event: Dict[str, Any], rest_comment: List[str]):
    """Handle the 'approve' bot command."""
    logger.info('Processing approve command...')
    if rest_comment[0] in {'*', 'all'}:
        logger.info('Approving all rest_comment...')
        add_award_to_note(event, SUCCESS)

        merge_or_pull_req_id = event.get('metadata').get('merge_or_pull_req_id')
        path_to_files_for_approval = f"{config.path_to_artifacts}/{merge_or_pull_req_id}/"
        file_names_with_content = get_all_files_from_s3_directory(config.artifacts_bucket, path_to_files_for_approval)

        logger.debug(f"Files with its content ---> {file_names_with_content}")

        if file_names_with_content:
            logger.info('Committing all corrected files...')

            # Check if files exist in VCS repository
            files_to_check = [file_key for file_key, _ in file_names_with_content]

            if not check_files_exist_in_repo(event, files_to_check):
                logger.warning('Some files do not exist in the repository')
                add_award_to_note(event, FAILURE)
                post_comment(event, 'Some files do not exist in the repository')
            # post_comment(event, 'All files exist in the repository. Committing changes...')

            commit_files_to_branch(event, file_names_with_content, 'Test commit from AI Handler Lambda')
            delete_files_from_s3(config.artifacts_bucket, path_to_files_for_approval)
    else:
        logger.info('Approving specific rest_comment...')
        merge_or_pull_req_id = event.get('metadata').get('merge_or_pull_req_id')
        path_to_files_for_approval = f"{config.path_to_artifacts}/{merge_or_pull_req_id}/"
        fixed_files = get_file_names_from_s3_directory(config.artifacts_bucket, path_to_files_for_approval)

        wrong_files = [file_name for file_name in rest_comment if file_name not in fixed_files]
        #
        if wrong_files:
            logger.warning(f'Invalid rest_comment specified: {wrong_files}')
            # add_award_to_note(event, 'rotating_light')
            post_comment(event, f'Invalid rest_comment: {wrong_files}')
        else:
            add_award_to_note(event, SUCCESS)
            logger.info(f"Fixed files ---> {fixed_files}")
            files_names_with_content = get_particular_files_from_s3_directory(config.artifacts_bucket,
                                                                              path_to_files_for_approval, rest_comment)
            logger.info(f"Files with its content ---> {files_names_with_content}")
            commit_files_to_branch(event, files_names_with_content, 'Test commit from AI Handler Lambda')
            delete_files_from_s3(config.artifacts_bucket, path_to_files_for_approval)
