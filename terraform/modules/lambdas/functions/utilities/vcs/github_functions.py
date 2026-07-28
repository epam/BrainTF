from functools import lru_cache
from typing import Any, Dict, List, Union

from github import Auth, Github, InputGitTreeElement
from github.GithubException import (BadCredentialsException, GithubException,
                                    UnknownObjectException)

from config import config
from utilities.logger import logger
from utilities.messages import HELP_MESSAGE


@lru_cache(maxsize=1)
def _get_github_client() -> Github:
    """
    Fetches the GitHub client with a caching mechanism and verifies the session token.

    This function creates and caches a GitHub client for accessing the GitHub API.
    It utilizes an `lru_cache` decorator to cache the client instance and performs
    a lightweight health check to ensure the token and session are valid.

    Returns:
        Github: An authenticated client for accessing GitHub API.

    Raises:
        Exception: If the verification of the token or session fails, the exception
            propagates to prevent caching an invalid client.
    """
    auth = Auth.Token(config.vcs_api_token)
    base_url = config.vcs_api_endpoint

    client = Github(
        auth=auth,
        base_url=base_url
    ) if base_url else Github(auth=auth)

    # Perform a lightweight health check before caching
    try:
        client.get_user()  # verifies the token and session
    except Exception as e:
        # Do NOT cache a failed session, let the exception propagate
        logger.error(f"GitHub client verification failed: {e}.")
        raise

    return client  # gets cached only if everything above succeeds


def get_pr_source_branch_name(repo_id_or_name: Union[int, str], pull_number: int) -> str:
    """Get the source branch name of a GitHub pull request.

    Args:
        repo_id_or_name (Union[int, str]): The repository ID or "owner/name" string.
        pull_number (int): Pull request number.

    Returns:
        str: Name of the source branch.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If repository or PR is not found.
        GithubException: For other GitHub API errors.
    """

    try:
        gh = _get_github_client()
        repo = gh.get_repo(repo_id_or_name)
        pr = repo.get_pull(pull_number)
        return pr.head.ref

    except BadCredentialsException as e:
        logger.error(f"GitHub authentication error: {e}.")
        raise
    except UnknownObjectException as e:
        logger.error(f"GitHub object not found: {e}.")
        raise
    except GithubException as e:
        logger.error(f"GitHub API error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting PR source branch: {e}.")
        raise


def add_reaction_to_pr_comment_github(event: Dict[str, Any], reaction: str, ):
    """Add a reaction emoji to a GitHub pull request conversation comment (IssueComment).

    Args:
        event (Dict[str, Any]): Event metadata containing repo and PR info.
        reaction (str): Normalized GitHub reaction value (see VALID_GITHUB_REACTIONS).

    Returns:
        Any: The updated IssueComment object.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If repository, PR, or comment is not found.
        GithubException: For other GitHub API errors.
        ValueError: If the reaction is invalid, or the comment does not belong to the PR.
    """

    try:
        gh = _get_github_client()
        repo = gh.get_repo(event.get('metadata').get('repo_id_or_name'))
        # Ensure PR exists (will raise if not)
        pr = repo.get_pull(event.get('metadata').get('merge_or_pull_req_id'))
        issue_comment = pr.get_issue_comment(event.get('metadata').get('comment_id'))

        issue_comment.create_reaction(reaction)
        # get all info about comment

        return issue_comment

    except BadCredentialsException as e:
        logger.error(f"GitHub authentication error: {e}.")
        raise
    except UnknownObjectException as e:
        logger.error(f"GitHub object not found: {e}.")
        raise
    except GithubException as e:
        logger.error(f"GitHub API error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error adding reaction to GitHub PR comment: {e}.")
        raise


def post_pr_comment_github(event: Dict[str, Any], comment_text: str):
    """Post a new comment to a GitHub pull request.

    Args:
        event (Dict[str, Any]): Event metadata containing repo and PR info.
        comment_text (str): Comment body text.

    Returns:
        Any: The created IssueComment object.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If repository, PR, or comment is not found.
        GithubException: For other GitHub API errors.
        ValueError: If the reaction is invalid, or the comment does not belong to the PR.
    """

    try:
        gh = _get_github_client()
        repo = gh.get_repo(event.get('metadata').get('repo_id_or_name'))
        # Ensure PR exists (will raise if not)
        pr = repo.get_pull(event.get('metadata').get('merge_or_pull_req_id'))

        issue_comment = pr.create_issue_comment(body=f"{comment_text.strip()}")

        return issue_comment

    except BadCredentialsException as e:
        logger.error(f"GitHub authentication error: {e}.")
        raise
    except UnknownObjectException as e:
        logger.error(f"GitHub object not found: {e}.")
        raise
    except GithubException as e:
        logger.error(f"GitHub API error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error posting comment to GitHub PR: {e}.")
        raise


def post_help_message_github(event: Dict[str, Any]):
    """Post a help message on a GitHub pull request."""
    return post_pr_comment_github(event, HELP_MESSAGE.format(spec_provider='GitHub PR comments'))


def check_files_exist_in_repo_github(event: Dict[str, Any],
                                     file_paths: list[str],
                                     ) -> bool:
    """Check that all given files exist in a GitHub repository on a specific branch.

    Args:
        event (Dict[str, Any]): Event metadata containing repo and PR info.
        file_paths (list[str]): Paths to files relative to the repository root.

    Returns:
        bool: True if all files exist, False if at least one file is missing.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If the repository or branch is not found.
        GithubException: For other GitHub API errors.
    """
    try:
        repo_id_or_name = event.get('metadata').get('repo_id_or_name')
        merge_or_pull_req_id = event.get('metadata').get('merge_or_pull_req_id')
        # Use the source branch of the PR as the default
        branch = get_pr_source_branch_name(repo_id_or_name, merge_or_pull_req_id)
        gh = _get_github_client()
        repo = gh.get_repo(repo_id_or_name)
        logger.debug(
            f"Checking existence of {len(file_paths)} file(s) in repo '{repo_id_or_name}' "
            f"on branch '{branch}'."
        )

        missing_files: list[str] = []

        for path in file_paths:
            try:
                # Will raise UnknownObjectException if the file or ref does not exist
                repo.get_contents(path, ref=branch)
                logger.debug(f"File exists in repo: {path}")
            except UnknownObjectException:
                logger.warning(f"File does not exist in repo on branch '{branch}': {path}")
                missing_files.append(path)

        if missing_files:
            logger.warning(f"Missing {len(missing_files)} file(s) in repo: {missing_files}")
            return False

        logger.info("All files exist in the GitHub repository on the specified branch.")
        return True

    except BadCredentialsException as e:
        logger.error(f"GitHub authentication error while checking file existence: {e}.")
        raise
    except UnknownObjectException as e:
        # This usually indicates repo or branch doesn't exist
        logger.error(f"GitHub object not found while checking file existence: {e}.")
        raise
    except GithubException as e:
        logger.error(f"GitHub API error while checking file existence: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error while checking file existence in GitHub repo: {e}.")
        raise


def commit_files_to_branch_github(event: Dict[str, Any], file_paths_with_content: list[tuple[str, str]],
                                  commit_message: str):
    """Commit multiple existing files to a GitHub repository branch in a single commit.

    Args:
        event (Dict[str, Any]): Event metadata containing repo and PR info.
        file_paths (list[str]): List of file paths to commit.
        commit_message (str): Commit message for all files.

    Returns:
        Any: The commit object created.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If repository or branch is not found.
        GithubException: For other GitHub API errors.
    """
    try:
        gh = _get_github_client()
        repo = gh.get_repo(event.get('metadata').get('repo_id_or_name'))
        merge_or_pull_req_id = event.get('metadata').get('merge_or_pull_req_id')
        branch = get_pr_source_branch_name(event.get('metadata').get('repo_id_or_name'), merge_or_pull_req_id)

        # Get reference and latest commit
        ref = repo.get_git_ref(f"heads/{branch}")
        latest_commit = repo.get_git_commit(ref.object.sha)
        logger.debug(f"Latest commit on branch '{branch}': {latest_commit.sha}")

        # Prepare tree elements
        tree_elements = []

        for path, content in file_paths_with_content:
            blob = repo.create_git_blob(content, "utf-8")
            logger.debug(f"Created Git blob for {path} with SHA {blob.sha}")
            element = InputGitTreeElement(
                path=path,
                mode="100644",
                type="blob",
                sha=blob.sha,
            )
            tree_elements.append(element)
        logger.debug(f"Prepared Git tree element(s): {tree_elements} for commit")

        # Create a new tree
        new_tree = repo.create_git_tree(tree_elements, base_tree=latest_commit.tree)

        # Create commit
        new_commit = repo.create_git_commit(commit_message, new_tree, [latest_commit])

        # Point a branch to the new commit
        ref.edit(new_commit.sha)

        logger.debug(f"Successfully committed file(s) {file_paths_with_content} to branch '{branch}'.")


    except BadCredentialsException as e:
        logger.error(f"GitHub authentication error: {e}.")
        raise
    except UnknownObjectException as e:
        logger.error(f"GitHub object not found: {e}.")
        raise
    except GithubException as e:
        logger.error(f"GitHub API error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error committing files to GitHub repo: {e}.")
        raise


def get_last_commit_sha_github(repo_id_or_name: Union[int, str], pull_number: int) -> str:
    """Get the last commit SHA for a GitHub pull request.

    """
    try:
        gh = _get_github_client()
        repo = gh.get_repo(repo_id_or_name)
        pr = repo.get_pull(pull_number)
        return pr.head.sha

    except BadCredentialsException as e:
        logger.error(f"GitHub authentication error: {e}.")
        raise
    except UnknownObjectException as e:
        logger.error(f"GitHub object not found: {e}.")
        raise
    except GithubException as e:
        logger.error(f"GitHub API error: {e}.")
        raise
    except Exception as e:
        logger.error(f"Unexpected error getting PR head SHA: {e}.")
        raise


def get_all_tf_files_from_paths_list_github(
        event: Dict[str, Any],
        paths_list: List[str]
) -> List[tuple[str, str]]:
    repo_identifier = event.get('metadata', {}).get('repo_id_or_name')
    branch = event.get('metadata', {}).get('source_branch')
    gh = _get_github_client()
    repo = gh.get_repo(repo_identifier)

    tf_files: List[tuple[str, str]] = []
    for target_dir in paths_list:
        try:
            items = repo.get_contents(target_dir, ref=branch)
        except GithubException as exc:
            logger.warning(f"Skipping {target_dir}: {exc}")
            continue

        for item in items:
            if item.type == "file" and item.path.endswith(".tf"):
                logger.info(f"Terraform file {item.path} fetched from GitHub...")
                tf_files.append((item.path, item.decoded_content.decode("utf-8")))
    return tf_files
