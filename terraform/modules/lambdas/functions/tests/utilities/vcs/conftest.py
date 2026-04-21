from types import SimpleNamespace

import pytest


@pytest.fixture
def mock_functions():
    """Fixture to provide mocked functions."""
    return SimpleNamespace(
        mock_post_comment=lambda: "mock_post_comment",
        mock_add_award=lambda: "mock_add_award",
        mock_check_files_exist=lambda: "mock_check_files_exist",
        mock_commit_files=lambda: "mock_commit_files",
        mock_get_tf_files=lambda: "mock_get_tf_files",
    )


@pytest.fixture
def patched_vcs_module_github(monkeypatch, mock_functions):
    """Fixture for GitHub VCS module patching."""
    # Mock the VCS provider config
    monkeypatch.setattr("config.config.vcs_provider", "github")

    # Patch GitHub-specific functions
    monkeypatch.setattr("utilities.vcs.github_functions.post_pr_comment_github", mock_functions.mock_post_comment)
    monkeypatch.setattr("utilities.vcs.github_functions.add_reaction_to_pr_comment_github",
                        mock_functions.mock_add_award)
    monkeypatch.setattr("utilities.vcs.github_functions.check_files_exist_in_repo_github",
                        mock_functions.mock_check_files_exist)
    monkeypatch.setattr("utilities.vcs.github_functions.commit_files_to_branch_github",
                        mock_functions.mock_commit_files)
    monkeypatch.setattr("utilities.vcs.github_functions.get_all_tf_files_from_paths_list_github",
                        mock_functions.mock_get_tf_files)

@pytest.fixture
def patched_vcs_module_gitlab(monkeypatch, mock_functions):
    """Fixture for GitLab VCS module patching."""
    # Mock the VCS provider config
    monkeypatch.setattr("config.config.vcs_provider", "gitlab")

    # Patch GitLab-specific functions
    monkeypatch.setattr("utilities.vcs.gitlab_functions.post_gitlab_comment", mock_functions.mock_post_comment)
    monkeypatch.setattr("utilities.vcs.gitlab_functions.add_award_to_note_gitlab",
                        mock_functions.mock_add_award)
    monkeypatch.setattr("utilities.vcs.gitlab_functions.check_files_exist_in_repo_gitlab",
                        mock_functions.mock_check_files_exist)
    monkeypatch.setattr("utilities.vcs.gitlab_functions.commit_files_to_branch_gitlab",
                        mock_functions.mock_commit_files)
    monkeypatch.setattr("utilities.vcs.gitlab_functions.get_all_tf_files_from_paths_list_gitlab",
                        mock_functions.mock_get_tf_files)
