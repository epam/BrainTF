import textwrap
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
from utilities.messages import AI_RESPONSE_MESSAGE, LIST_FILES_MESSAGE
from utilities.parsers import parse_hcl_blocks
from utilities.vcs import (FAILURE, SUCCESS, add_award_to_note,
                           check_files_exist_in_repo, commit_files_to_branch,
                           post_comment, post_help_message)


def handle_ai_response_message(event: Dict[str, Any]) -> None:
    """Process an AI response and upload extracted HCL blocks to S3.

    The function reads the AI response from event metadata, extracts HCL blocks,
    and replaces the current artifacts for the associated merge or pull request
    when blocks are found.

    Args:
        event: Event payload containing metadata with ``ai_response`` and
            ``merge_or_pull_req_id``.

    Raises:
        InvalidEventMetadata: If the merge or pull request ID is missing.
    """
    response_message = event.get('metadata', {}).get('ai_response')
    if not response_message:
        logger.debug("No AI response message found in event metadata.")
        return
    filenames_with_hcl_blocks: dict[str, str] = parse_hcl_blocks(response_message)
    if filenames_with_hcl_blocks:
        logger.debug(f"Extracted HCL blocks from AI response: {filenames_with_hcl_blocks}.")
        pull_number = event.get('metadata', {}).get('merge_or_pull_req_id')
        if not pull_number:
            raise InvalidEventMetadata("Pull/Merge request ID not found in the event metadata.")
        path_to_artifacts = f"{config.path_to_artifacts}/{pull_number}/"
        delete_files_from_s3(config.artifacts_bucket, path_to_artifacts)
        logger.debug(
            f"Uploading generated files to S3 bucket '{config.artifacts_bucket}' "
            f"for pull/merge request #{pull_number}."
        )
        upload_files_to_s3(config.artifacts_bucket, pull_number, filenames_with_hcl_blocks)


def handle_help_command(event: Dict[str, Any]) -> None:
    """Handle the ``help`` bot command.

    Args:
        event: Event payload for the current comment or webhook update.
    """
    logger.info('Processing help command...')
    post_help_message(event)


def handle_comment_commands(event: Dict[str, Any]) -> None:
    """Dispatch a comment to the matching bot handler.

    Args:
        event: Event payload containing ``comment_text`` in metadata.
    """
    comment_context, *rest_comment = event.get('metadata', {}).get('comment_text', '_').split()
    logger.debug(f"Parsed comment context: {comment_context}")
    if comment_context == 'bot':
        logger.info('Bot context found in the comment.')
        handle_bot_commands(event, rest_comment)

    elif comment_context == 'help' and not rest_comment:

        logger.info('Help context found in the comment.')
        add_award_to_note(event, SUCCESS)
        handle_help_command(event)

    else:
        logger.info('No actionable context found in the comment.')


def handle_list_command(event: Dict[str, Any]) -> None:
    """Handle the ``list`` bot command.

    Args:
        event: Event payload used to locate the current artifact directory.
    """
    logger.info('Processing list command...')
    merge_request_id = event.get('metadata', {}).get('merge_or_pull_req_id')
    path_to_mr_artifacts = f"{config.path_to_artifacts}/{merge_request_id}/"
    file_names = get_file_names_from_s3_directory(config.artifacts_bucket, path_to_mr_artifacts)
    if file_names:
        files_list = '\n\n'.join(f"`{file_name}`" for file_name in file_names)
    else:
        files_list = '`..`'

    logger.debug(f"Prepared artifact file list: {files_list}.")
    post_comment(event, LIST_FILES_MESSAGE.format(files_list=files_list))


def handle_bot_commands(event: Dict[str, Any], rest_comment: List[str]) -> None:
    """Route a parsed bot command to the appropriate handler.

    Args:
        event: Event payload carrying comment and request metadata.
        rest_comment: Comment tokens after the leading ``bot`` keyword.
    """
    logger.info('Processing bot commands...')
    logger.debug(f"Parsed command arguments: {rest_comment}.")
    if rest_comment:
        command: str = rest_comment[0]
        rest_comment: List[str] = rest_comment[1:]

        if command == 'approve' and rest_comment:
            logger.info('Approve context found in the comment.')
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


def handle_prompt_command(event: Dict[str, Any], rest_comment: List[str]) -> None:
    """Handle the ``prompt`` bot command.

    Args:
        event: Event payload used to load context and persist the AI response.
        rest_comment: Prompt tokens after the command keyword.
    """
    logger.info('Processing prompt command...')
    prompt = ' '.join(rest_comment)
    user_message = {'content': prompt, 'role': 'user'}
    messages_for_ai = get_context_memory_window(event) + [user_message]

    logger.debug(f"Messages prepared for sending to AI: {messages_for_ai}.")
    response = generate_response_ai(messages_for_ai)

    logger.info(f"Received AI response >\n{response}")

    event.setdefault("metadata", {}).update({"prompt": prompt, "ai_response": response["message"].strip()})

    ai_response_message_to_ui = AI_RESPONSE_MESSAGE.format(ai_response=response["message"],
                                                           total_tokens=response["tokens"]["total_tokens"],
                                                           prompt_tokens=response["tokens"]["prompt_tokens"],
                                                           completion_tokens=response["tokens"]["completion_tokens"])
    post_comment(event, ai_response_message_to_ui)
    handle_ai_response_message(event)
    create_context_memory_window(event)


def render_approval_commit_message(approved_files: List[str], include_suffix: bool = False) -> str:
    """Render a wrapped commit message for approved AI-generated files.

    Args:
        approved_files: Approved repository paths to include in the message.
        include_suffix: Whether to append ``and others`` to the message.

    Returns:
        A wrapped commit message that fits the repository's line-width limit.
    """
    commit_message_prefix = f"AI-bot fixed issues in {'the file' if len(approved_files) == 1 else 'files'}"
    commit_message_suffix = 'and others'
    message_parts = [commit_message_prefix]
    if approved_files:
        message_parts.append(', '.join(approved_files))
    if include_suffix:
        message_parts.append(commit_message_suffix)

    message = ' '.join(message_parts)
    return textwrap.fill(message, width=72, break_long_words=False, break_on_hyphens=False)


def build_approval_commit_message(approved_files: List[str]) -> str:
    """Build a commit message for approved AI-generated file changes.

    Args:
        approved_files: Approved repository paths to include in the message.

    Returns:
        A commit message trimmed to the repository length constraints.
    """
    commit_message = render_approval_commit_message(approved_files)

    if len(commit_message) <= 1000:
        return commit_message

    selected_files: List[str] = []
    for file_name in approved_files:
        candidate_files = selected_files + [file_name]
        candidate_message = render_approval_commit_message(candidate_files, include_suffix=True)
        if len(candidate_message) <= 1000:
            selected_files.append(file_name)
        else:
            break

    return render_approval_commit_message(selected_files, include_suffix=True)


def handle_approve_command(event: Dict[str, Any], rest_comment: List[str]) -> None:
    """Handle the ``approve`` bot command.

    Args:
        event: Event payload used to resolve artifacts and commit changes.
        rest_comment: File names or approval keywords supplied by the user.
    """
    logger.info('Processing approve command...')
    if rest_comment[0] in {'*', 'all'}:
        logger.info('Approving all corrected files...')
        add_award_to_note(event, SUCCESS)

        merge_or_pull_req_id = event.get('metadata', {}).get('merge_or_pull_req_id')
        path_to_files_for_approval = f"{config.path_to_artifacts}/{merge_or_pull_req_id}/"
        file_names_with_content: list[tuple[str, str]] = get_all_files_from_s3_directory(
            config.artifacts_bucket, path_to_files_for_approval
        )

        logger.debug(f"Corrected files from S3 artifacts with its content: {file_names_with_content}")

        if file_names_with_content:
            logger.info('Committing all approved corrected files...')

            # Check if files exist in VCS repository
            files_to_check: list[str] = [file_key for file_key, _ in file_names_with_content]

            if not check_files_exist_in_repo(event, files_to_check):
                logger.warning('Some approved files do not exist in the repository.')
                add_award_to_note(event, FAILURE)
                post_comment(event, 'Some approved files do not exist in the repository')
                return

            commit_message = build_approval_commit_message(files_to_check)
            commit_files_to_branch(event, file_names_with_content, commit_message)
            delete_files_from_s3(config.artifacts_bucket, path_to_files_for_approval)
    else:
        logger.info('Approving specific rest_comment...')
        merge_or_pull_req_id = event.get('metadata', {}).get('merge_or_pull_req_id')
        path_to_files_for_approval = f"{config.path_to_artifacts}/{merge_or_pull_req_id}/"
        fixed_files: list[str] = get_file_names_from_s3_directory(config.artifacts_bucket, path_to_files_for_approval)

        wrong_files = [file_name for file_name in rest_comment if file_name not in fixed_files]
        #
        if wrong_files:
            logger.warning(f'Requested files are not available for approval: {wrong_files}.')
            # add_award_to_note(event, 'rotating_light')
            post_comment(event, f'Invalid rest_comment: {wrong_files}')
        else:
            add_award_to_note(event, SUCCESS)

            if not check_files_exist_in_repo(event, rest_comment):
                logger.warning('Some selected files do not exist in the repository.')
                add_award_to_note(event, FAILURE)
                post_comment(event, 'Some selected files do not exist in the repository.')
                return

            files_names_with_content: list[tuple[str, str]] = get_particular_files_from_s3_directory(
                config.artifacts_bucket, path_to_files_for_approval, rest_comment
            )

            commit_message = build_approval_commit_message(rest_comment)
            commit_files_to_branch(event, files_names_with_content, commit_message)
            delete_files_from_s3(config.artifacts_bucket, path_to_files_for_approval)
