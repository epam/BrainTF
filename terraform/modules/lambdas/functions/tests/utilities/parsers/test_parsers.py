import re
from collections import Counter
from typing import Callable

from utilities.parsers import extract_blocks_ending_with_working_directory


def validate_extracted_blocks(result, expected_text):
    """Helper function to validate the common structure and content of extracted blocks."""
    assert isinstance(result, list), "Result should be a list"
    assert len(result) == 3, "Extracted result should have exactly 3 items"
    for item in result:
        assert isinstance(item, tuple), "Each item in the result should be a tuple"
        for value in item:
            assert isinstance(value, str), "Each value in a tuple should be a string"
    assert result == expected_text, "Extracted result does not match the expected output"


def validate_replaced_relative_paths(function: Callable[[str, str], str], blocks_to_replace: list[tuple[str]],
                                     expected: list[str]):
    for index, item in enumerate(blocks_to_replace):
        result = function(*item)
        assert result is not None, "Result should not be None"
        assert isinstance(result, str), "Result should be a string"
        assert result == expected[index]
        assert result is not None, "Result should not be None"
        assert result.strip() != '', "Result should not be empty"


def validate_extracted_paths(result, expected_paths):
    assert isinstance(result, list), "Result should be a list"
    assert len(result) == len(expected_paths), "Extracted paths should have the same length as expected paths"
    for path in result:
        assert bool(re.compile(r"^(\/?[\w\-\.]+\/?)+$").match(path)), "Path should be a valid Linux path"
    result_counter = Counter(result)
    expected_counter = Counter(expected_paths)

    assert result_counter == expected_counter, "Extracted paths do not match the expected output"


def test_extract_blocks_ending_with_working_directory_normal_flow_tflint(log_file_text_tflint,
                                                                         expected_workdir_errors_blocks_tflint):
    result = extract_blocks_ending_with_working_directory(*log_file_text_tflint)
    validate_extracted_blocks(result, expected_workdir_errors_blocks_tflint)


def test_extract_blocks_ending_with_working_directory_normal_flow_no_tool_name(log_file_text_no_tool_name,
                                                                               expected_workdir_errors_blocks_tflint):
    result = extract_blocks_ending_with_working_directory(*log_file_text_no_tool_name)
    validate_extracted_blocks(result, expected_workdir_errors_blocks_tflint)


def test_extract_blocks_ending_with_working_directory_normal_flow_checkov(log_file_text_checkov,
                                                                          expected_workdir_errors_blocks_checkov):
    result = extract_blocks_ending_with_working_directory(*log_file_text_checkov)
    validate_extracted_blocks(result, expected_workdir_errors_blocks_checkov)


def test_extract_blocks_ending_with_working_directory_normal_flow_tfsec(log_file_text_tfsec,
                                                                        expected_workdir_errors_blocks_tfsec):
    result = extract_blocks_ending_with_working_directory(*log_file_text_tfsec)
    validate_extracted_blocks(result, expected_workdir_errors_blocks_tfsec)


def test_extract_blocks_ending_with_working_directory_normal_flow_terraform(log_file_text_terraform,
                                                                            expected_workdir_errors_blocks_terraform):
    result = extract_blocks_ending_with_working_directory(*log_file_text_terraform)
    validate_extracted_blocks(result, expected_workdir_errors_blocks_terraform)


def test_replace_relative_paths_to_absolute_in_errors_terraform(
        expected_workdir_errors_blocks_terraform,
        replaced_workdir_errors_blocks_terraform
):
    from utilities.parsers import \
        replace_relative_paths_to_absolute_in_errors_terraform
    validate_replaced_relative_paths(replace_relative_paths_to_absolute_in_errors_terraform,
                                     expected_workdir_errors_blocks_terraform,
                                     replaced_workdir_errors_blocks_terraform)


def test_replace_relative_paths_to_absolute_in_errors_tfsec(
        expected_workdir_errors_blocks_tfsec,
        replaced_workdir_errors_blocks_tfsec
):
    from utilities.parsers import \
        replace_relative_paths_to_absolute_in_errors_tfsec

    validate_replaced_relative_paths(replace_relative_paths_to_absolute_in_errors_tfsec,
                                     expected_workdir_errors_blocks_tfsec,
                                     replaced_workdir_errors_blocks_tfsec)


def test_replace_relative_paths_to_absolute_in_errors_checkov(
        expected_workdir_errors_blocks_checkov,
        replaced_workdir_errors_blocks_checkov
):
    from utilities.parsers import \
        replace_relative_paths_to_absolute_in_errors_checkov

    validate_replaced_relative_paths(replace_relative_paths_to_absolute_in_errors_checkov,
                                     expected_workdir_errors_blocks_checkov,
                                     replaced_workdir_errors_blocks_checkov)


def test_clean_text_for_tfsec(expected_workdir_errors_blocks_tfsec, cleaned_errors_blocks_tfsec):
    from utilities.parsers import clean_text_for_tfsec
    for index, item in enumerate(expected_workdir_errors_blocks_tfsec):
        result = clean_text_for_tfsec(item[1])
        assert isinstance(result, str), "Result should be a string"
        assert result == cleaned_errors_blocks_tfsec[index]
        assert result.startswith('') and result.endswith(''), "Result should not start or end with newlines"


def test_get_paths_from_errors_checkov(replaced_paths_one_block_checkov, extracted_paths_to_tf_files_checkov):
    from utilities.parsers import get_paths_from_errors_checkov
    result = get_paths_from_errors_checkov(replaced_paths_one_block_checkov)
    validate_extracted_paths(result, extracted_paths_to_tf_files_checkov)


def test_get_paths_from_errors_tflint(log_text_one_block_tflint, extracted_paths_to_tf_files_tflint):
    from utilities.parsers import get_paths_from_errors_tflint
    result = get_paths_from_errors_tflint(log_text_one_block_tflint)
    validate_extracted_paths(result, extracted_paths_to_tf_files_tflint)


def test_get_paths_from_errors_tfsec(replaced_paths_one_block_tfsec, extracted_paths_to_tf_files_tfsec):
    from utilities.parsers import get_paths_from_errors_tfsec
    result = get_paths_from_errors_tfsec(replaced_paths_one_block_tfsec)
    validate_extracted_paths(result, extracted_paths_to_tf_files_tfsec)


def test_remove_no_issues_dir_block_log_text_tfsec(no_issue_dir_blocks_tfsec, removed_no_issue_dir_blocks_tfsec):
    from utilities.parsers import remove_no_issues_dir_blocks_checkov_tfsec
    result = remove_no_issues_dir_blocks_checkov_tfsec(no_issue_dir_blocks_tfsec)
    assert result == removed_no_issue_dir_blocks_tfsec


def test_parse_hcl_blocks_ai_response_to_filenames_content(ai_response_with_corrected_files_hcl_blocks,
                                                           parsed_corrected_filenames_and_content_from_hcl_blocks):
    from utilities.parsers import parse_hcl_blocks
    result = parse_hcl_blocks(ai_response_with_corrected_files_hcl_blocks)
    assert isinstance(result, dict), "Result should be a dictionary"
    assert result == parsed_corrected_filenames_and_content_from_hcl_blocks
