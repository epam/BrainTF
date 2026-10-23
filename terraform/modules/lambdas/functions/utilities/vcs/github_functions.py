from functools import lru_cache
from typing import Any

from github import Auth, Github, InputGitTreeElement
from github.GithubException import (
    BadCredentialsException,
    GithubException,
    UnknownObjectException,
)

from config import config
from utilities.logger import logger
from utilities.messages import HELP_MESSAGE


@lru_cache(maxsize=2)
def _get_github_client(vcs_api_token: str) -> Github:
    """Fetches the GitHub client with a caching mechanism and verifies the session token.

    This function creates and caches a GitHub client by token for accessing the
    GitHub API. It performs a lightweight health check to ensure the token and
    session are valid.

    Args:
        vcs_api_token (str): The GitHub API token used for authentication.

    Returns:
        Github: An authenticated client for accessing GitHub API.

    Raises:
        Exception: If the verification of the token or session fails, the exception
            propagates to prevent caching an invalid client.
    """
    auth = Auth.Token(vcs_api_token)
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


def _get_pull_request(repo_id_or_name: int | str, pull_number: int,
                      operation: str) -> Any:
    """Get a GitHub pull request.

    Args:
        repo_id_or_name (int | str): GitHub repository ID or full name.
        pull_number (int): Pull request number.
        operation (str): Operation name used in unexpected error messages.

    Returns:
        Any: The requested GitHub pull request.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If the repository or pull request is not found.
        GithubException: For other GitHub API errors.
        Exception: For unexpected errors while retrieving the pull request.
    """
    try:
        gh = _get_github_client(config.vcs_api_token)
        repo = gh.get_repo(repo_id_or_name)
        return repo.get_pull(pull_number)

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
        logger.error(f"Unexpected error getting {operation}: {e}.")
        raise


def add_reaction_to_pr_comment_github(event: dict[str, Any], reaction: str, ):
    """Add a reaction emoji to a GitHub pull request conversation comment
    (IssueComment).

    Args:
        event (dict[str, Any]): Event metadata containing repository, pull request, and
            comment information.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (int | str): The GitHub repository ID or full name.
                - 'merge_or_pull_req_id' (int): The pull request number.
                - 'comment_id' (int): The issue comment ID.
        reaction (str): Normalized GitHub reaction value (see VALID_GITHUB_REACTIONS).

    Returns:
        Any: The updated IssueComment object.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If repository, PR, or comment is not found.
        GithubException: For other GitHub API errors.
        ValueError: If the reaction is invalid, or the comment does not belong to
            the PR.
    """

    try:
        gh = _get_github_client(config.vcs_api_token)
        repo = gh.get_repo(event['metadata']['repo_id_or_name'])
        # Ensure PR exists (will raise if not)
        pr = repo.get_pull(event['metadata']['merge_or_pull_req_id'])
        issue_comment = pr.get_issue_comment(event['metadata']['comment_id'])

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


def post_pr_comment_github(event: dict[str, Any], comment_text: str):
    """Post a new comment to a GitHub pull request.

    Args:
        event (dict[str, Any]): Event metadata containing repository and pull request
            information.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (int | str): The GitHub repository ID or full name.
                - 'merge_or_pull_req_id' (int): The pull request number.
        comment_text (str): Comment body text.

    Returns:
        Any: The created IssueComment object.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If repository, PR, or comment is not found.
        GithubException: For other GitHub API errors.
        ValueError: If the reaction is invalid, or the comment does not belong to
            the PR.
    """

    try:
        gh = _get_github_client(config.vcs_api_token)
        repo = gh.get_repo(event['metadata']['repo_id_or_name'])
        # Ensure PR exists (will raise if not)
        pr = repo.get_pull(event['metadata']['merge_or_pull_req_id'])

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


def post_help_message_github(event: dict[str, Any]):
    """Post a help message on a GitHub pull request.

    Args:
        event (dict[str, Any]): Event metadata identifying the pull request.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (int | str): The GitHub repository ID or full name.
                - 'merge_or_pull_req_id' (int): The pull request number.

    Returns:
        Any: The created IssueComment object.
    """
    return post_pr_comment_github(event, HELP_MESSAGE.format(spec_provider='GitHub PR comments'))


def check_files_exist_in_repo_github(event: dict[str, Any],
                                     file_paths: list[str],
                                     ) -> bool:
    """Check that all given files exist in a GitHub repository on a specific branch.

    Args:
        event (dict[str, Any]): Event metadata containing repository and pull request
            information.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (int | str): The GitHub repository ID or full name.
                - 'merge_or_pull_req_id' (int): The pull request number.
        file_paths (list[str]): Paths to files relative to the repository root.

    Returns:
        bool: True if all files exist, False if at least one file is missing.

    Raises:
        BadCredentialsException: If authentication fails.
        UnknownObjectException: If the repository or branch is not found.
        GithubException: For other GitHub API errors.
    """
    try:
        repo_id_or_name = event['metadata']['repo_id_or_name']
        merge_or_pull_req_id = event['metadata']['merge_or_pull_req_id']
        gh = _get_github_client(config.vcs_api_token)
        repo = gh.get_repo(repo_id_or_name)
        branch = repo.get_pull(merge_or_pull_req_id).head.ref
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


def commit_files_to_branch_github(event: dict[str, Any], file_paths_with_content: list[tuple[str, str]],
                                  commit_message: str):
    """Commits files with specified content to a branch in a GitHub repository.

    Args:
        event (dict[str, Any]): The event data dictionary containing metadata about the
            repository.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (int | str): The GitHub repository ID or full name.
                - 'merge_or_pull_req_id' (int): The pull request number.
        file_paths_with_content (list[tuple[str, str]]): A list of tuples representing
            file paths and their corresponding content to be committed.
        commit_message (str): The commit message to include with the changes.

    Returns:
        None: This function updates the branch and does not return a value.

    Raises:
        BadCredentialsException: If there is an authentication failure with GitHub.
        UnknownObjectException: If a specified repository, commit, or object is not found.
        GithubException: For other errors related to the GitHub API.
        Exception: For unexpected errors during the process.
    """
    try:
        gh = _get_github_client(config.vcs_api_token)
        repo = gh.get_repo(event['metadata']['repo_id_or_name'])
        merge_or_pull_req_id = event['metadata']['merge_or_pull_req_id']
        branch = repo.get_pull(merge_or_pull_req_id).head.ref

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


def get_last_commit_sha_github(repo_id_or_name: int | str, pull_number: int) -> str:
    """Get the last commit SHA for a GitHub pull request.

    Args:
        repo_id_or_name (int | str): GitHub repository ID or full name.
        pull_number (int): Pull request number.

    Returns:
        str: The SHA of the latest commit on the pull request's source branch.
    """
    return _get_pull_request(repo_id_or_name, pull_number, "PR head SHA").head.sha


def get_all_tf_files_from_paths_list_github(
        event: dict[str, Any],
        paths_list: list[str]
) -> list[tuple[str, str]]:
    """Fetch all Terraform (.tf) files from the specified paths in GitHub.

    Args:
        event (dict[str, Any]): A dictionary containing metadata about the GitHub
            repository.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (int | str): The GitHub repository ID or full name.
                - 'source_branch' (str): The name of the repository branch to fetch
                    files from.
        paths_list (list[str]): A list of directory paths within the GitHub repository
            from which to retrieve Terraform files.

    Returns:
        list[tuple[str, str]]: A list where each element is a tuple containing the
            Terraform file path and its decoded UTF-8 content.
    """
    repo_identifier = event['metadata']['repo_id_or_name']
    branch = event['metadata']['source_branch']
    gh = _get_github_client(config.vcs_api_token)
    repo = gh.get_repo(repo_identifier)

    tf_files: list[tuple[str, str]] = []
    for target_dir in paths_list:
        try:
            items = repo.get_contents(target_dir, ref=branch)
        except GithubException as exc:
            logger.warning(f"Skipping {target_dir}: {exc}")
            continue

        if not isinstance(items, list):
            items = [items]

        for item in items:
            if item.type == "file" and item.path.endswith(".tf"):
                logger.info(f"Terraform file {item.path} fetched from GitHub...")
                tf_files.append((item.path, item.decoded_content.decode("utf-8")))
    return tf_files


def get_files_content_from_repo_github(
        event: dict[str, Any],
        file_paths: list[str]
) -> dict[str, str | None]:
    """Fetch the current content of files from the pull request branch in GitHub.

    Args:
        event (dict[str, Any]): Event metadata containing repository and pull request
            information.
            Mandatory keys include:
            - 'metadata':
                - 'repo_id_or_name' (int | str): The GitHub repository ID or full name.
                - 'merge_or_pull_req_id' (int): The pull request number.
        file_paths (list[str]): Paths to files relative to the repository root.

    Returns:
        dict[str, str | None]: Mapping of each path to its decoded UTF-8 content, or
            ``None`` when the file does not exist on the branch.
    """
    pull = _get_pull_request(
        event['metadata']['repo_id_or_name'], event['metadata']['merge_or_pull_req_id'], "files content"
    )
    repo = _get_github_client(config.vcs_api_token).get_repo(event['metadata']['repo_id_or_name'])
    branch = pull.head.ref

    contents: dict[str, str | None] = {}
    for path in file_paths:
        try:
            contents[path] = repo.get_contents(path, ref=branch).decoded_content.decode("utf-8")
        except UnknownObjectException:
            logger.warning(f"File does not exist in repo on branch '{branch}': {path}")
            contents[path] = None
    return contents
