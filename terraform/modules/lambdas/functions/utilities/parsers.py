import os
import re
from typing import Dict, List


def remove_no_issues_checkov_blocks(text):
    """
    Remove blocks that contain both:
    1. "Running Checkov analysis in directory: <path>"
    2. "No issues were found during Checkov analysis in the directory: <path>."

    The <path> can vary but should match between both lines.
    """

    # Pattern explanation:
    # - .*? matches any characters (non-greedy)
    # - \s* matches optional whitespace/newlines
    # - ([^\s\n]+) captures the directory path (non-whitespace characters)
    # - (?=\.) positive lookahead to ensure the path ends with a period in the second line

    # Remove the matched blocks
    cleaned_text = re.sub(
        r'Running (?:Checkov|TFSec) analysis in directory: ([^\s]+)\s*.*?\s*No issues were found '
        r'during (?:Checkov|TFSec) analysis in the directory: \1\.',
        '',
        text,
        flags=re.DOTALL
    )

    # Clean up any extra whitespace left behind
    cleaned_text = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_text)

    return cleaned_text.strip()


def extract_blocks_ending_with_working_directory(text: str, tool_name: str) -> list[tuple[str, str]]:
    """
    Extracts blocks of content from a given text that end with a working directory
    based on specific tool analysis or the general format.

    This function parses the input `text` to extract blocks of text followed by
    working directory paths. Depending on the value of `tool_name`, it applies patterns
    specifically for 'Checkov' or 'TFSec' or uses a generic pattern when the tool name
    doesn't match these specific cases.

    Args:
        text: The input text containing analysis logs and working directory paths.
        tool_name: The name of the tool ("Checkov" or "TFSec") that determines the
            parsing approach.

    Returns:
        A list of tuples where each tuple contains a working directory path as the
        first element and the preceding block of content as the second element.
    """
    if tool_name.lower() == 'checkov' or tool_name.lower() == 'tfsec':
        # Find all occurrences of the pattern and their preceding content
        matches = re.findall(
            r"Running (?:Checkov|TFSec) analysis in directory: (\S+)\n(.*?)(?=\n+Running (?:Checkov|TFSec)|$)",  # noqa:
            text, flags=re.DOTALL)
        # Create a list with the path as key and content as value
        result = [(match[0], match[1].strip()) for match in matches]

    else:
        matches = re.findall(r'(.*?)\nWorking Directory: (.+?)(?=\n|$)', text, flags=re.DOTALL)  # noqa:
        result = [(match[1], match[0].strip()) for match in matches]

    return result


def replace_relative_paths_to_absolute_in_errors_terraform(errors_data: str, working_directory: str) -> str:
    # Replace paths after two spaces and before line numbers
    result = re.sub(
        r"(\s{2}on\s{1})(.*?)(\sline\s.*)",
        lambda match: f"{match.group(1)}{os.path.join(working_directory, match.group(2))}{match.group(3)}",
        errors_data
    )

    return result


def replace_relative_paths_to_absolute_in_errors_tfsec(errors_data: str, working_directory: str) -> str:
    """Replace relative file paths with absolute paths in TFSec error output.

    Takes TFSec error output text and replaces all relative file paths with absolute paths
    by prepending the working directory. Handles both regular file paths and "via" references.

    Args:
        errors_data: String containing the TFSec error output with relative paths
        working_directory: Base directory path to prepend to make paths absolute

    Returns:
        String with all relative paths replaced with absolute paths
    """
    # Replace paths after two spaces and before line numbers
    result = re.sub(
        r"(\n {2})(.+?)(:\d+-?\d*\n)",
        lambda match: f"{match.group(1)}{os.path.join(working_directory, match.group(2))}{match.group(3)}",
        errors_data
    )

    # Replace paths in "via" lines
    result = re.sub(
        r"( {3}via {1})(.+?)(:\d+-?\d+ {1})",  # noqa:
        lambda match: f"{match.group(1)}{os.path.join(working_directory, match.group(2))}{match.group(3)}",
        result
    )

    return result


def replace_relative_paths_to_absolute_in_errors_checkov(
        errors_data: str,
        working_directory: str
) -> str:
    """Replace relative file paths with absolute paths in Checkov error output.

    Converts relative paths in "File:" and "Calling File:" lines to absolute paths
    by joining them with the working directory.

    Args:
        errors_data: String containing Checkov error messages with relative paths.
        working_directory: Base directory to resolve absolute paths from.

    Returns:
        Modified error data with absolute paths replacing relative paths.

    """
    return re.sub(
        r"(^\s*(?:Calling )?File:\s+)(.+?)(:\d+-?\d*\n)",
        lambda match: f"{match.group(1)}{os.path.join(working_directory, match.group(2).lstrip('/'))}{match.group(3)}",
        errors_data,
        flags=re.MULTILINE
    )


def get_paths_from_errors_checkov(errors_data: str) -> List[str]:
    # ReGex pattern to match only `File: ` paths and exclude `Calling File: `

    # Find all matches
    matches = re.findall(r'^\s*(?:Calling )?File:\s+(.+?):\d+-?\d*\n',
                         errors_data,
                         re.MULTILINE)

    matches = list(set(matches))
    paths_to_tf_files = []
    for match in matches:
        directory = os.path.dirname(match)

        paths_to_tf_files.append(directory)
    return paths_to_tf_files


def get_paths_from_errors_tfsec(errors_data: str) -> List[str]:
    # Find all matches
    matches = re.findall(r"\n {2}(.+):\d+-?\d+\n", errors_data, re.MULTILINE)

    unique_matches = list(set(matches))

    paths_to_tf_files = []

    for match in unique_matches:
        directory = os.path.dirname(match)
        paths_to_tf_files.append(directory)

    return paths_to_tf_files


def clean_text_for_tfsec(input_text):
    """
    Cleans the input text by:
    1. Removing sections between 'timings' and 'detected'.
    2. Removing blocks starting with 'More Information' and ending at the first empty line.
    3. Replacing long horizontal lines with '---'.

    Args:
        input_text (str): The input text containing all sections.

    Returns:
        str: The cleaned text with the unwanted sections removed and horizontal lines replaced.
    """
    # Step 1: Remove the section between 'timings' and 'detected'
    pattern_timings_to_detected = r"(timings[\s\S]+?detected.*)"
    cleaned_text = re.sub(pattern_timings_to_detected, "", input_text, flags=re.MULTILINE)

    # Step 2: Remove blocks starting with 'More Information' and ending at the first empty line
    pattern_more_information = r" {2}More Information[\s\S]*?─+\n"
    cleaned_text = re.sub(pattern_more_information, "", cleaned_text, flags=re.MULTILINE)

    # Step 3: Replace long horizontal lines with '───'
    pattern_long_lines = r"─{10,}"  # Matches 10 or more consecutive '─' characters
    cleaned_text = re.sub(pattern_long_lines, "───", cleaned_text)

    # Strip leading and trailing whitespace
    return cleaned_text.strip()


def extract_strings_between_on_and_line(text: str) -> List[str]:
    """
    Extracts strings between 'on ' and h' line' from the given text
    and returns them as a list.

    Args:
        text (str): The input text.

    Returns:
        list: A list of strings found between 'on ' and ' line'.
    """
    # Use a regular expression to find all matches between 'on ' and ' line'
    pattern = r'on (.*?) line \d'
    matches = re.findall(pattern, text)  # Find all matches

    # Return the list of unique matches
    return list({os.path.dirname(match) for match in matches if match})


def parse_hcl_blocks(text: str) -> Dict[str, str]:
    """
    Parses a response containing file content delimited by HCL extracted_blocks
    and returns a dictionary with filenames as keys and HCL content as values.

    Args:
        text (str): The raw response containing file content.

    Returns:
        dict: A dictionary where keys are filenames and values are HCL content.
    """
    # Regular expression to match the start and end markers and extract HCL content
    file_pattern = re.compile(
        r"Corrected file `(.+?)`.*?```hcl(.*?)```",
        re.DOTALL
    )

    files: Dict[str, str] = {}

    # Find all matches in the response
    for match in file_pattern.finditer(text):
        filename: str = match.group(1).strip()  # Extract the filename
        hcl_content: str = match.group(2).strip() + '\n'  # Extract the HCL content
        files[filename] = hcl_content  # Store in the dictionary

    return files
