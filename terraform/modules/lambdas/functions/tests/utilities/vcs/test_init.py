import importlib

import pytest


def test_github_imports(patched_vcs_module_github, mock_functions):
    # Reload the __init__.py module so the mocks are applied
    import utilities.vcs as vcs
    importlib.reload(vcs)
    # Import the module
    from utilities.vcs import (FAILURE, SUCCESS, add_award_to_note,
                               check_files_exist_in_repo,
                               commit_files_to_branch,
                               get_all_tf_files_from_paths_list, post_comment)

    # Assert the imported functions are correct
    assert post_comment is mock_functions.mock_post_comment
    assert add_award_to_note is mock_functions.mock_add_award
    assert check_files_exist_in_repo is mock_functions.mock_check_files_exist
    assert commit_files_to_branch is mock_functions.mock_commit_files
    assert get_all_tf_files_from_paths_list is mock_functions.mock_get_tf_files

    # Assert constants
    assert SUCCESS == "+1"
    assert FAILURE == "confused"


def test_gitlab_imports(patched_vcs_module_gitlab, mock_functions):
    # Reload the __init__.py module so the mocks are applied
    import utilities.vcs as vcs
    importlib.reload(vcs)
    # Import the module
    from utilities.vcs import (FAILURE, SUCCESS, add_award_to_note,
                               check_files_exist_in_repo,
                               commit_files_to_branch,
                               get_all_tf_files_from_paths_list, post_comment)

    # Assert the imported functions are correct
    assert post_comment is mock_functions.mock_post_comment
    assert add_award_to_note is mock_functions.mock_add_award
    assert check_files_exist_in_repo is mock_functions.mock_check_files_exist
    assert commit_files_to_branch is mock_functions.mock_commit_files
    assert get_all_tf_files_from_paths_list is mock_functions.mock_get_tf_files

    # Assert constants
    assert SUCCESS == 'white_check_mark'
    assert FAILURE == 'rotating_light'


def test_invalid_vcs_provider(monkeypatch):
    # Mock an unsupported VCS provider
    monkeypatch.setattr("config.config.vcs_provider", "unsupported")

    # Expect a ValueError when importing the module
    with pytest.raises(ValueError, match="Unsupported VCS provider: unsupported"):
        # Reload the __init__.py module so the mocked config is applied
        import utilities.vcs as vcs
        importlib.reload(vcs)
