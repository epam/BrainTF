import base64
from functools import lru_cache
from pathlib import PurePosixPath
from typing import Any

from gitlab import Gitlab, GitlabAuthenticationError, GitlabCreateError, GitlabGetError

from config import config
from utilities.logger import logger
from utilities.messages import HELP_MESSAGE


@lru_cache(maxsize=2)
def _get_gitlab_client(vcs_api_token: str) -> Gitlab:
    """Gets a cached GitLab client instance configured with the provided API token.

    This function creates and authenticates a GitLab client using the provided API token.
    It also performs a lightweight health check by verifying the client version to ensure
    the session is valid before caching the client instance. If any authentication or
    verification step fails, an exception will be raised, and the client object will
    not be cached.

    Args:
        vcs_api_token (str): The GitLab API token used for authentication.

    Returns:
        Gitlab: An authenticated GitLab client instance.

    Raises:
        Exception: If the GitLab client authentication or version verification fails.
    """

    client = Gitlab(
        url=config.vcs_api_endpoint,
        private_token=vcs_api_token,
    )

    # Authenticate token
    client.auth()
    # Perform a lightweight health check before caching
    try:

        client.version()  # verifies the token and session
    except Exception as e:
        # Do NOT cache a failed session, let the exception propagate
        logger.error(f"GitLab client verification failed: {e}.")
        raise

    return client  # gets cached only if everything above succeeds


def add_award_to_note_gitlab(
        event: dict[str, Any],
        reaction: str
) -> dict[str, Any]:
    """Adds an award emoji reaction to a specific note on a GitLab merge request.

    This function interacts with the GitLab API to add a specific reaction
    (award emoji) to a comment (note) on a merge request. It requires valid
    configuration and authentication tokens to function properly. The GitLab
    project, merge request, and note are identified using the metadata from
    the input event.

    Args:
        event (dict[str, Any]): A dictionary containing metadata necessary to perform
            the action.
            Expected keys include:
            - 'metadata':
                - 'repo_id_or_name' (str): The GitLab project ID or path.
                - 'merge_or_pull_req_id' (int): The merge request ID.
                - 'comment_id' (int): The note ID.
        reaction (str): The name of the award emoji reaction to be added to the note.

    Returns:
        dict[str, Any]: A dictionary containing the attributes of the created award
            emoji.

    Raises:
        GitlabAuthenticationError: If there is an issue with GitLab authentication.
        GitlabGetError: If there is an error retrieving GitLab project, merge request,
            or note details.
        Exception: If an unexpected error occurs during the process.
    """
    try:
        gl = _get_gitlab_client(config.vcs_api_token)

        project = gl.projects.get(event['metadata']['repo_id_or_name'])
        mr = project.mergerequests.get(event['metadata']['merge_or_pull_req_id'])
        note = mr.notes.get(event['metadata']['comment_id'])
        award = note.awardemojis.create({'name': reaction})

        logger.debug(f"Added GitLab award emoji: {award.attributes}.")
        return award.attributes

    except GitlabAuthenticationError as e:
        logger.error(f"GitLab authentication error: {e}.")
        raise
    except GitlabGetError as e:
        logger.error(f"GitLab get error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding award emoji to GitLab note: {e}.")
        raise


def post_gitlab_comment(event: dict[str, Any], comment_text: str) -> dict[str, Any]:
    """Posts a comment on a GitLab merge request.

    This function interacts with the GitLab API to post a comment on a specified
    GitLab merge request using the provided event details and comment text. It
    handles authentication and error reporting.

    Args:
        event (dict[str, Any]): A dictionary containing metadata about the GitLab
            repository and merge request.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (str): The GitLab repository ID or name.
                - 'merge_or_pull_req_id' (int): The merge request ID.
        comment_text (str): The text content of the comment to be posted.

    Returns:
        dict[str, Any]: A dictionary containing the attributes of the created
            comment.

    Raises:
        GitlabAuthenticationError: If there is an authentication issue with the
            GitLab API.
        GitlabGetError: If there is an error retrieving the specified repository
            or merge request.
        Exception: For unexpected errors encountered during the operation.
    """
    try:
        gl = _get_gitlab_client(config.vcs_api_token)
        project = gl.projects.get(event['metadata']['repo_id_or_name'])
        mr = project.mergerequests.get(event['metadata']['merge_or_pull_req_id'])
        note = mr.notes.create({'body': comment_text})

        logger.debug(f"Posted GitLab merge request comment: {note.attributes}.")
        return note.attributes

    except GitlabAuthenticationError as e:
        logger.error(f"GitLab authentication error: {e}.")
        raise
    except GitlabGetError as e:
        logger.error(f"GitLab get error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error posting GitLab comment: {e}.")
        raise


def post_help_message_gitlab(event: dict[str, Any]) -> dict[str, Any]:
    """Posts a help message as a GitLab merge request comment.

    This function generates and posts a help message to a GitLab merge request
    comment using the provided event data.

    Args:
        event (dict[str, Any]): A dictionary containing event data relevant to the
            GitLab merge request. This typically includes information needed
            for identifying the merge request and generating the comment.
            Expected keys include:
            - 'metadata':
                - 'repo_id_or_name' (str): The GitLab repository ID or name.
                - 'merge_or_pull_req_id' (int): The merge request ID.

    Returns:
        dict[str, Any]: A dictionary containing the response from the GitLab API
            after posting the comment.
    """
    return post_gitlab_comment(event, HELP_MESSAGE.format(spec_provider='GitLab MR notes'))


def _group_file_paths_by_directory(file_paths: list[str]) -> dict[str, set[str]]:
    """Groups a list of file paths by their parent directories.

    This function takes a list of file paths and organizes them into a dictionary where the
    keys are directory paths and the values are sets of file names belonging to each directory.

    Args:
        file_paths (list[str]): A list of file paths as strings to be grouped by their
            parent directory.

    Returns:
        dict[str, set[str]]: A dictionary mapping directory paths (keys) to sets of file names
            (values) belonging to those directories.
    """
    files_by_dir: dict[str, set[str]] = {}

    for path in file_paths:
        posix_path = PurePosixPath(path)
        parent = str(posix_path.parent)
        dir_path = parent if parent != "." else ""
        files_by_dir.setdefault(dir_path, set()).add(posix_path.name)

    return files_by_dir


def _get_missing_files_from_directory(
        project: Any,
        dir_path: str,
        expected_files: set[str],
        branch: str,
) -> list[str]:
    """Identifies missing files from a specified directory in a GitLab repository.

    This function compares a set of expected files with the actual contents of a directory
    in a GitLab repository. It returns a list of files that are expected but not present in
    the specified directory.

    Args:
        project (Any): The GitLab project instance, used to query the repository.
        dir_path (str): The directory path within the repository to check. If None or
            an empty string,
            the root directory will be checked.
        expected_files (set[str]): A set of file names that are expected to exist in
            the specified directory.
        branch (str): The name of the branch in the repository to query the directory contents.

    Returns:
        list[str]: A list of missing file paths relative to the repository root.

    Raises:
        GitlabGetError: If a non-404 error occurs while fetching the directory tree
            from the repository.
    """
    logger.debug(f"Fetching GitLab repository tree for directory {dir_path or '/'}")

    try:
        # get_all=True is required: without it python-gitlab returns only the first
        # page, and existing files beyond it would be reported as missing.
        tree = project.repository_tree(
            path=dir_path or None,
            ref=branch,
            recursive=False,
            get_all=True,
        )
    except GitlabGetError as e:
        if e.response_code != 404:
            raise
        return [
            f"{dir_path}/{file_name}" if dir_path else file_name
            for file_name in expected_files
        ]

    existing_files = {
        item["name"]
        for item in tree
        if item["type"] == "blob"
    }

    return [
        f"{dir_path}/{file_name}" if dir_path else file_name
        for file_name in expected_files
        if file_name not in existing_files
    ]


def check_files_exist_in_repo_gitlab(
        event: dict[str, Any],
        file_paths: list[str],
) -> bool:
    """Checks if the given files exist in a GitLab repository on a specific branch.

    This function verifies the existence of a list of files in a specified GitLab
    repository and branch. It uses the metadata provided in the event dictionary
    to fetch the repository and branch details. If any file from the list does not
    exist in the repository, the function logs a warning and returns `False`,
    otherwise it returns `True`.

    Args:
        event (dict[str, Any]): A dictionary containing metadata about the repository
            and branch.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (str): The project identifier or name.
                - 'merge_or_pull_req_id' (int): The merge request ID.
        file_paths (list[str]): A list of file paths to check for existence in the
            repository.

    Returns:
        bool: `True` if all the files exist on the specified branch in the repository,
        `False` otherwise.

    Raises:
        GitlabAuthenticationError: If there is an authentication error with the GitLab
            client.
        GitlabGetError: If there is an API-related error while accessing the GitLab
            repository or merge request.
        Exception: If any other unexpected error occurs during the operation.
    """
    try:
        project_id_or_path = event['metadata']['repo_id_or_name']
        merge_request_id = event['metadata']['merge_or_pull_req_id']

        gl = _get_gitlab_client(config.vcs_api_token)
        project = gl.projects.get(project_id_or_path)
        branch = project.mergerequests.get(merge_request_id).source_branch

        logger.debug(
            f"Batch-checking {len(file_paths)} file(s) in project "
            f"'{project_id_or_path}' on branch '{branch}'."
        )

        missing_files: list[str] = []
        for dir_path, expected_files in _group_file_paths_by_directory(file_paths).items():
            missing_files.extend(
                _get_missing_files_from_directory(
                    project=project,
                    dir_path=dir_path,
                    expected_files=expected_files,
                    branch=branch,
                )
            )

        if missing_files:
            logger.warning(f"Some requested file(s) are missing from the repository: {missing_files}")
            return False

        logger.info("All files exist in the repository on the specified branch.")
        return True

    except GitlabAuthenticationError as e:
        logger.error(f"GitLab authentication error: {e}.")
        raise

    except GitlabGetError as e:
        logger.error(f"GitLab API error: {e}.")
        raise

    except Exception as e:
        logger.error(f"Unexpected error while checking file existence: {e}.")
        raise


def commit_files_to_branch_gitlab(
        event: dict[str, Any],
        file_paths_with_content: list[tuple[str, str]],
        commit_message: str,
) -> dict[str, Any]:
    """Commits a list of files to a specific branch in a GitLab project.

    The branch used for the commit is the source branch of a merge request specified
    in the event metadata. Each file in the provided list is updated or created in
    the commit based on the action specified.

    Args:
        event (dict[str, Any]): The event contains metadata including the GitLab project ID or name
            and the merge request ID. These are used to derive the project details and the branch to
            which the files will be committed.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (str): The GitLab project ID or name.
                - 'merge_or_pull_req_id' (int): The merge request ID.
        file_paths_with_content (list[tuple[str, str]]): A list of tuples where each tuple consists of
            the file path as a string and the file content as a string. These represent the files to
            update or create in the branch.
        commit_message (str): The commit message to associate with the commit.

    Returns:
        dict[str, Any]: The attributes of the created commit, containing details about the commit, such
        as its ID, the committed files, and other GitLab metadata.

    Raises:
        GitlabAuthenticationError: If authentication to the GitLab API fails.
        GitlabGetError: If there is an error retrieving project or merge request details.
        GitlabCreateError: If there is an error creating the commit in GitLab.
        Exception: For any other unexpected errors during the commit process.
    """
    try:
        gl = _get_gitlab_client(config.vcs_api_token)

        metadata = event.get("metadata", {})
        project_id = metadata.get("repo_id_or_name")
        mr_id = metadata.get("merge_or_pull_req_id")

        project = gl.projects.get(project_id)
        mr = project.mergerequests.get(mr_id)

        # Use the source branch of the merge request (equivalent to PR head branch)
        branch = mr.source_branch
        logger.debug(
            f"Preparing to commit {len(file_paths_with_content)} file(s) "
            f"to project '{project_id}' on branch '{branch}'."
        )

        # Prepare actions for the commit API
        actions = []
        for path, content in file_paths_with_content:
            logger.debug(f"Scheduling update for {path}")
            actions.append(
                {
                    "action": "update",  # assumes files already exist; use "create" if you need to add new ones
                    "file_path": path,
                    "content": content,
                }
            )

        if not actions:
            logger.warning("No files provided for commit; skipping commit creation.")
            return {}

        # Create a single commit with all actions on the MR source branch
        commit = project.commits.create(
            {
                "branch": branch,
                "commit_message": commit_message,
                "actions": actions,
            }
        )

        logger.info(
            f"Successfully committed {len(file_paths_with_content)} file(s) "
            f"to branch '{branch}'. Commit ID: {commit.id}."
        )
        return commit.attributes

    except GitlabAuthenticationError as e:
        logger.error(f"GitLab authentication error while committing files: {e}.")
        raise
    except GitlabGetError as e:
        logger.error(f"GitLab get error while committing files: {e}.")
        raise
    except GitlabCreateError as e:
        logger.error(f"GitLab create error while committing files: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error committing files to GitLab repo: {e}.")
        raise


def get_all_tf_files_from_paths_list_gitlab(
        event: dict[str, Any],
        paths_list: list[str]
) -> list[tuple[str, str]]:
    """Fetches all Terraform (.tf) files from the specified paths in a GitLab repository.

    This function connects to GitLab using a pre-configured API client, retrieves files with the
    ".tf" extension from the provided list of directory paths, and decodes their contents
    from base64 to a UTF-8 text string. The result is a list of tuples containing the file path
    and its content.

    Args:
        event (dict[str, Any]): A dictionary containing metadata about the GitLab repository.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (str): The ID or name of the GitLab repository.
                - 'source_branch' (str): The name of the repository branch to fetch files from.

        paths_list (list[str]): A list of directory paths within the GitLab repository from
            which to retrieve Terraform files.

    Returns:
        list[tuple[str, str]]: A list where each element is a tuple containing:
            - str: The file path of the Terraform file within the repository.
            - str: The decoded content of the Terraform file as a UTF-8 string.
    """
    gl = _get_gitlab_client(config.vcs_api_token)
    project = gl.projects.get(event['metadata']['repo_id_or_name'])

    # List to hold tuples of (repo_path, file_content_text)
    tf_files = []

    for target_dir in paths_list:

        items = project.repository_tree(
            path=target_dir,
            ref=event['metadata']['source_branch'],
            get_all=True,
        )
        for item in items:
            if item['type'] == 'blob' and item['name'].endswith('.tf'):
                logger.info(f"Fetching Terraform file '{item['path']}' from GitLab...")
                file = project.files.get(file_path=item['path'], ref=event['metadata']['source_branch'])
                # Decode base64 content to text string (assume UTF-8)
                content_text = base64.b64decode(file.content).decode('utf-8')
                tf_files.append((item['path'], content_text))

    return tf_files


def get_files_content_from_repo_gitlab(
        event: dict[str, Any],
        file_paths: list[str]
) -> dict[str, str | None]:
    """Fetch the current content of files from the merge request source branch in GitLab.

    Args:
        event (dict[str, Any]): A dictionary containing metadata about the GitLab repository.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (str): The ID or name of the GitLab repository.
                - 'source_branch' (str): The name of the repository branch to fetch files from.
        file_paths (list[str]): Paths to files relative to the repository root.

    Returns:
        dict[str, str | None]: Mapping of each path to its decoded UTF-8 content, or
            ``None`` when the file does not exist on the branch.
    """
    gl = _get_gitlab_client(config.vcs_api_token)
    project = gl.projects.get(event['metadata']['repo_id_or_name'])
    branch = event['metadata']['source_branch']

    contents: dict[str, str | None] = {}
    for path in file_paths:
        try:
            file = project.files.get(file_path=path, ref=branch)
            contents[path] = base64.b64decode(file.content).decode('utf-8')
        except GitlabGetError:
            logger.warning(f"File does not exist in repo on branch '{branch}': {path}")
            contents[path] = None
    return contents
