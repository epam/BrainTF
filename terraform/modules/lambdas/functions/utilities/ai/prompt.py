from typing import Any, Dict

from config import config
from utilities.logger import logger
from utilities.parsers import (
    clean_text_for_tfsec, extract_blocks_ending_with_working_directory,
    get_paths_from_errors_tflint, get_paths_from_errors_checkov,
    get_paths_from_errors_tfsec, remove_no_issues_dir_blocks_checkov_tfsec,
    replace_relative_paths_to_absolute_in_errors_checkov,
    replace_relative_paths_to_absolute_in_errors_terraform,
    replace_relative_paths_to_absolute_in_errors_tfsec)
from utilities.vcs import get_all_tf_files_from_paths_list


def _process_checkov_or_tfsec_errors(errors: str, working_directory: str, tool_name_lower: str) -> tuple[str, list]:
    if tool_name_lower == 'checkov':
        errors = replace_relative_paths_to_absolute_in_errors_checkov(working_directory, errors)
        paths_to_files = get_paths_from_errors_checkov(errors)
        return errors, paths_to_files
    elif tool_name_lower == 'tfsec':
        errors = clean_text_for_tfsec(errors)
        errors = replace_relative_paths_to_absolute_in_errors_tfsec(working_directory, errors)
        paths_to_files = get_paths_from_errors_tfsec(errors)
        return errors, paths_to_files
    elif tool_name_lower == 'terraform':
        errors = replace_relative_paths_to_absolute_in_errors_terraform(working_directory, errors)
        paths_to_files = [working_directory]

        return errors, paths_to_files
    else:
        return '', []



def _process_other_tool_errors(errors: str, working_directory: str) -> list:
    paths_to_files = get_paths_from_errors_tflint(errors)
    if not paths_to_files:
        paths_to_files = [working_directory]

    logger.info(f"File paths ---> \n{paths_to_files}")
    return paths_to_files


def make_prompt_block_with_errors_and_files(event,
                                            errors_data: str) -> str:
    prompt_block = """"""
    guide_block = """"""
    tool_name_lower = event.get('metadata').get('tool_name').lower()
    is_checkov_or_tfsec = tool_name_lower in ['checkov', 'tfsec', 'terraform']

    if is_checkov_or_tfsec:
        errors_data = remove_no_issues_dir_blocks_checkov_tfsec(errors_data)

        if config.rag_enabled:
            pass
            # guide_block = extract_all_guides_secutils(errors_data, tool_name)

    extracted_blocks: list = extract_blocks_ending_with_working_directory(errors_data, tool_name_lower)

    for working_directory, errors in extracted_blocks:
        logger.info(f"Working directory ---> \n{working_directory}")
        files_block = """"""

        if is_checkov_or_tfsec:
            errors, paths_to_files = _process_checkov_or_tfsec_errors(errors, working_directory, tool_name_lower)
        else:
            paths_to_files = _process_other_tool_errors(errors, working_directory)

        files_and_content = get_all_tf_files_from_paths_list(event, paths_to_files)

        for file_path, file_content in files_and_content:
            files_block += f"File content on: {file_path}\n\n```hcl\n{file_content}\n```\n"

        prompt_block += errors + "\n\n" + guide_block + "\n\n" + files_block + "\n"

    logger.debug(f"Prompt block ---> \n{prompt_block}")
    return prompt_block


def prepare_user_prompt_message(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Prepares a user prompt message based on the provided event data. This includes processing
    errors and generating the formatted prompt content to be used in subsequent operations.

    Args:
        event (Dict[str, Any]): The event data containing metadata, errors, and other necessary
            context required to construct the user prompt.

    Returns:
        Dict[str, str]: A dictionary containing the role and the generated prompt content.
    """
    errors_text: str = event.get('metadata', {}).get('log_file_content', '')
    prompt: str = make_prompt_block_with_errors_and_files(event, errors_text).strip()
    event.get("metadata").update({"prompt": prompt})

    return {'role': 'user', 'content': prompt}
