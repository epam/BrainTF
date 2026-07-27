import base64
from functools import lru_cache
from pathlib import PurePosixPath
from typing import Any, Dict, List

import gitlab
from gitlab import GitlabAuthenticationError, GitlabGetError

from config import config
from utilities.logger import logger
from utilities.messages import HELP_MESSAGE


@lru_cache(maxsize=1)
def _get_gitlab_client() -> gitlab.Gitlab:
    """Return an authenticated and verified GitLab client instance."""

    client = gitlab.Gitlab(
        url=config.vcs_api_endpoint,
        private_token=config.vcs_api_token,
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


def get_mr_source_branch_name(
        project_id_or_path: str,
        merge_request_id: int,
) -> str:
    """Get the source branch name of a GitLab Merge Request.

    Args:
        project_id_or_path (str): GitLab project ID or 'namespace/project'.
        merge_request_id (int): Merge Request IID (not global ID).

    Returns:
        str: Source branch name.

    Raises:
        GitlabAuthenticationError: If authentication fails.
        GitlabGetError: If a project or MR is not found.
    """
    try:
        gl = _get_gitlab_client()
        project = gl.projects.get(project_id_or_path)
        mr = project.mergerequests.get(merge_request_id)

        source_branch = mr.source_branch

        logger.debug(
            f"MR {merge_request_id} source branch: '{source_branch}' "
            f"(project: '{project_id_or_path}')"
        )

        return source_branch

    except GitlabAuthenticationError as e:
        logger.error(f"GitLab authentication error while fetching MR: {e}.")
        raise

    except GitlabGetError as e:
        logger.error(
            f"GitLab API error while fetching MR "
            f"{merge_request_id} in project '{project_id_or_path}': {e}."
        )
        raise

    except Exception as e:
        logger.error(
            f"Unexpected error while getting source branch for MR "
            f"{merge_request_id}: {e}."
        )
        raise


def add_award_to_note_gitlab(
        event: Dict[str, Any],
        reaction: str
) -> Dict[str, Any]:
    """Add an award emoji to a GitLab merge request note.

    """

    try:
        gl = _get_gitlab_client()

        project = gl.projects.get(event.get('metadata').get('repo_id_or_name'))
        mr = project.mergerequests.get(event.get('metadata').get('merge_or_pull_req_id'))
        note = mr.notes.get(event.get('metadata').get('comment_id'))
        award = note.awardemojis.create({'name': reaction})

        logger.debug(f"Added GitLab award emoji: {award.attributes}.")
        return award.attributes

    except gitlab.exceptions.GitlabAuthenticationError as e:
        logger.error(f"GitLab authentication error: {e}.")
        raise
    except gitlab.exceptions.GitlabGetError as e:
        logger.error(f"GitLab get error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding award emoji to GitLab note: {e}.")
        raise


def post_gitlab_comment(event: Dict[str, Any], comment_text: str) -> Dict[str, Any]:
    """Post a comment on a GitLab merge request.

    Args:

    Returns:
        Dict[str, Any]: The JSON response from the GitLab API.
    """

    try:
        gl = _get_gitlab_client()
        project = gl.projects.get(event.get('metadata').get('repo_id_or_name'))
        mr = project.mergerequests.get(event.get('metadata').get('merge_or_pull_req_id'))
        note = mr.notes.create({'body': comment_text})

        logger.debug(f"Posted GitLab merge request comment: {note.attributes}.")
        return note.attributes

    except gitlab.exceptions.GitlabAuthenticationError as e:
        logger.error(f"GitLab authentication error: {e}.")
        raise
    except gitlab.exceptions.GitlabGetError as e:
        logger.error(f"GitLab get error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error posting GitLab comment: {e}.")
        raise


def post_help_message_gitlab(event: Dict[str, Any]) -> Dict[str, Any]:
    """Post a help message on a GitLab merge request."""
    return post_gitlab_comment(event, HELP_MESSAGE.format(spec_provider='GitLab MR notes'))


def check_files_exist_in_repo_gitlab(
        event: Dict[str, Any],
        file_paths: List[str],
) -> bool:
    """Batch-check file existence in a GitLab repo using a repository tree.

    Uses fewer API calls than per-file lookup.
    """
    try:
        project_id_or_path = event.get('metadata').get('repo_id_or_name')
        merge_request_id = event.get('metadata').get('merge_or_pull_req_id')

        branch = get_mr_source_branch_name(project_id_or_path, merge_request_id)

        gl = _get_gitlab_client()
        project = gl.projects.get(project_id_or_path)

        logger.debug(
            f"Batch-checking {len(file_paths)} file(s) in project "
            f"'{project_id_or_path}' on branch '{branch}'."
        )

        # Group requested files by directory
        files_by_dir: dict[str, set[str]] = {}

        for path in file_paths:
            p = PurePosixPath(path)
            dir_path = str(p.parent) if str(p.parent) != "." else ""
            files_by_dir.setdefault(dir_path, set()).add(p.name)

        missing_files: List[str] = []

        for dir_path, expected_files in files_by_dir.items():
            logger.debug(f"Fetching GitLab repository tree for directory {dir_path or '/'}")

            try:
                tree = project.repository_tree(
                    path=dir_path or None,
                    ref=branch,
                    recursive=False,
                )
            except GitlabGetError as e:
                if e.response_code == 404:
                    # Directory itself does not exist
                    for fname in expected_files:
                        missing_files.append(
                            f"{dir_path}/{fname}" if dir_path else fname
                        )
                    continue
                raise

            existing_files = {
                item["name"]
                for item in tree
                if item["type"] == "blob"
            }

            for fname in expected_files:
                if fname not in existing_files:
                    missing_files.append(
                        f"{dir_path}/{fname}" if dir_path else fname
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
        event: Dict[str, Any],
        file_paths_with_content: list[tuple[str, str]],
        commit_message: str,
) -> Dict[str, Any]:
    """Commit multiple files to a GitLab merge request source branch in a single commit.

    Args:
        event (Dict[str, Any]): Event metadata containing repo and MR info.
            Expected keys in event["metadata"]:
              - "repo_id_or_name": GitLab project ID or path
              - "merge_or_pull_req_id": Merge request IID
        file_paths_with_content (list[tuple[str, str]]): List of (path, content) pairs.
            Paths are relative to the repository root.
        commit_message (str): Commit message for all files.

    Returns:
        Dict[str, Any]: The created commit attributes from GitLab.

    Raises:
        gitlab.exceptions.GitlabAuthenticationError: If authentication fails.
        gitlab.exceptions.GitlabGetError: If the project or MR is not found.
        gitlab.exceptions.GitlabCreateError: For other GitLab API errors during commit creation.
        Exception: For unexpected errors.
    """
    try:
        gl = _get_gitlab_client()

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

    except gitlab.exceptions.GitlabAuthenticationError as e:
        logger.error(f"GitLab authentication error while committing files: {e}.")
        raise
    except gitlab.exceptions.GitlabGetError as e:
        logger.error(f"GitLab get error while committing files: {e}.")
        raise
    except gitlab.exceptions.GitlabCreateError as e:
        logger.error(f"GitLab create error while committing files: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error committing files to GitLab repo: {e}.")
        raise


def get_all_tf_files_from_paths_list_gitlab(
        event: Dict[str, Any],
        paths_list: List[str]
) -> List[tuple[str, str]]:
    gl = _get_gitlab_client()
    project = gl.projects.get(event.get('metadata').get('repo_id_or_name'))

    # List to hold tuples of (repo_path, file_content_text)
    tf_files = []

    for target_dir in paths_list:
        items = project.repository_tree(path=target_dir, ref=event.get('metadata').get('source_branch'))
        for item in items:
            if item['type'] == 'blob' and item['name'].endswith('.tf'):
                logger.info(f"Fetching Terraform file '{item['path']}' from GitLab...")
                file = project.files.get(file_path=item['path'], ref=event.get('metadata').get('source_branch'))
                # Decode base64 content to text string (assume UTF-8)
                content_text = base64.b64decode(file.content).decode('utf-8')
                tf_files.append((item['path'], content_text))

    return tf_files
