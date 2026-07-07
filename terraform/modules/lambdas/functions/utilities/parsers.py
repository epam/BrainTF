import os
import re
from typing import Dict


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
    cleaned_text = re.sub(
        r"(timings[\s\S]+?detected.*)",
        "",
        input_text,
        flags=re.MULTILINE
    )

    # Step 2: Remove blocks starting with 'More Information' and ending at the first empty line
    cleaned_text = re.sub(
        r" {2}More Information[\s\S]*?─+\n",
        "",
        cleaned_text,
        flags=re.MULTILINE
    )

    # Step 3: Replace long horizontal lines with '───' pattern_long_lines = r"─{10,}"
    # Matches 10 or more consecutive '─' characters
    cleaned_text = re.sub(
        r"─{10,}",  # Matches 10 or more consecutive '─' characters
        "───",
        cleaned_text
    )

    # Strip leading and trailing whitespace
    return cleaned_text.strip()


def clean_text_for_trivy(input_text: str) -> str:
    """
    Cleans Trivy output by removing summary sections before findings.

    Args:
        input_text (str): The input text containing Trivy sections.

    Returns:
        str: The cleaned text with Trivy summary headers removed.
    """

    # Remove top-level Trivy report summary table and its legend section.
    cleaned_text = re.sub(
        r"(?m)^\s*Report Summary\r?\n(?:\r?\n)?"
        r"(?:\s*[┌├│└][^\r\n]*\r?\n)+"
        r"\s*Legend:\r?\n"
        r"(?:\s*-\s*'[^']+':[^\r\n]*\r?\n)+\s*",
        "",
        input_text,
    )

    # Remove per-target Trivy summary headers before each finding section.
    cleaned_text = re.sub(
        r"(?m)^\s*(?:\.|[A-Za-z0-9_./-]+) \(terraform\)\r?\n"
        r"=+\r?\n"
        r"Tests: \d+ \(SUCCESSES: \d+, FAILURES: \d+\)\r?\n"
        r"Failures: \d+ \([^)]+\)\r?\n+",
        "",
        cleaned_text
    )

    # Replace long horizontal lines with '───' pattern_long_lines = r"─{10,}"
    # Matches 10 or more consecutive '─' characters
    cleaned_text = re.sub(
        r"─{10,}",  # Matches 10 or more consecutive '─' characters
        "───",
        cleaned_text
    )

    cleaned_text = re.sub(
        r"^\s*═{10,}\r?\n?",
        "",
        cleaned_text,
        flags=re.MULTILINE,
    )

    return cleaned_text.strip()


def extract_blocks_working_directory(text: str) -> list[tuple[str, str]]:
    """
    Extract blocks of tool output keyed by the working directory being analyzed.

    The parser scans the combined log text for supported tool run markers and
    returns each matched working directory together with the error block that
    follows it.

    Args:
        text: The input text containing analysis logs and working directory paths.

    Returns:
        A list of tuples where each tuple contains a working directory path as the
        first element and the preceding block of content as the second element.
    """

    # Find all occurrences of the pattern and their preceding content
    matches = re.finditer(
        r"Running (?:TFLint|Terraform|Checkov|TFSec|Trivy) (?:analysis|validate|init) in directory: (\S+)\n(.*?)"
        r"(?=\n+Running (?:TFLint|Terraform|Checkov|TFSec|Trivy)|$)",
        # noqa:
        text, flags=re.DOTALL)

    # Create a list with the path as key and content as value
    result = [(match.group(1), match.group(2).strip()) for match in matches]

    return result


def replace_relative_paths_to_absolute_in_errors_terraform(working_directory: str, errors_data: str) -> str:
    """
    Replaces relative file paths in Terraform error messages with absolute paths.

    This function modifies error messages by substituting relative paths with
    absolute paths based on the provided working directory. This makes the error
    messages more understandable and allows for easier identification of file
    locations.

    Args:
        working_directory (str): The absolute path to the working directory. This
            is used as the base path to convert relative paths in the error
            messages into absolute paths.
        errors_data (str): The error messages string in which relative paths are to
            be replaced by absolute paths.

    Returns:
        str: A string containing the modified error messages where relative paths
        have been replaced with absolute paths.
    """
    result: str = re.sub(
        r"(\s{2}on\s)(.*?)(\sline\s.*)",
        lambda match: f"{match.group(1)}{os.path.join(working_directory, match.group(2))}{match.group(3)}",
        errors_data
    )

    return result


def replace_relative_paths_to_absolute_in_errors_tfsec(working_directory: str, errors_data: str) -> str:
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


def replace_relative_paths_to_absolute_in_errors_checkov(working_directory: str, errors_data: str) -> str:
    """Replace relative file paths with absolute paths in Checkov error output.

    Converts relative paths in File: and Calling File: lines to absolute paths
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


def replace_relative_paths_to_absolute_in_errors_trivy(working_directory: str, errors_data: str) -> str:
    """Replace relative Trivy file paths with absolute paths."""

    def _replace_path(match: re.Match[str]) -> str:
        return f"{match.group(1)}{match.group(2)}{os.path.join(working_directory, match.group(3))}{match.group(4)}"

    result = re.sub(
        r"(^|\n)(\s*)([A-Za-z0-9_./-]+\.(?:tf|tfvars))(\s+\([^)]+\))",
        _replace_path,
        errors_data,
        flags=re.MULTILINE,
    )

    result = re.sub(
        r"(^|\n)(\s*)([A-Za-z0-9_./-]+\.(?:tf|tfvars))(:\d+(?:-\d+)?)",
        _replace_path,
        result,
        flags=re.MULTILINE,
    )

    return result


def get_paths_from_errors_checkov(errors_data: str) -> list:
    matches = re.findall(r'^\s*(?:Calling )?File:\s+(.+?):\d+-?\d*\n',
                         errors_data,
                         flags=re.MULTILINE)
    # Return the list of unique matches
    return list({os.path.dirname(match) for match in matches if match})


def get_paths_from_errors_tfsec(errors_data: str) -> list:
    matches = re.findall(r"\n {2}(.+):\d+-?\d+\n",
                         errors_data,
                         re.MULTILINE)
    # Return the list of unique matches
    return list({os.path.dirname(match) for match in matches if match})


def get_paths_from_errors_trivy(errors_data: str) -> list:
    """Extract unique Terraform directories from Trivy findings."""

    matches = re.findall(
        r"^\s*([A-Za-z0-9_./-]+\.(?:tf|tfvars))(?::\d+(?:-\d+)?)?$",
        errors_data,
        flags=re.MULTILINE,
    )

    return list({os.path.dirname(match) for match in matches if match})


def get_paths_from_errors_tflint(text: str) -> list:
    """
    Extracts strings between 'on ' and ' line' from the given text
    and returns them as a list.

    Args:
        text (str): The input text.

    Returns:
        list: A list of strings found between 'on ' and ' line'.
    """

    matches = re.findall(r"on (.*?) line \d",
                         text)  # Find all matches

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
