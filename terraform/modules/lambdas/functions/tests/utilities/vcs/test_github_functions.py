import pytest
from github.GithubException import (BadCredentialsException, GithubException,
                                    UnknownObjectException)


class MockIssueComment:
    def __init__(self, body):
        self.body = body
        self.create_reaction_called = 0
        self.last_reaction = None
        self.side_effect_create_reaction = None

    def create_reaction(self, reaction):
        self.create_reaction_called += 1
        self.last_reaction = reaction
        if self.side_effect_create_reaction:
            raise self.side_effect_create_reaction
        return True


class MockPRHead:
    def __init__(self, ref, sha="default-sha"):
        self.ref = ref
        self.sha = sha


class MockPR:
    def __init__(self):
        self.create_issue_comment_called = 0
        self.last_body = None
        self.side_effect_create_comment = None
        self.get_issue_comment_called = 0
        self.last_comment_id = None
        self.side_effect_get_issue_comment = None
        self.comment = MockIssueComment("original body")
        self.head = MockPRHead("feature-branch")

    def create_issue_comment(self, body):
        self.create_issue_comment_called += 1
        self.last_body = body
        if self.side_effect_create_comment:
            raise self.side_effect_create_comment
        return MockIssueComment(body)

    def get_issue_comment(self, comment_id):
        self.get_issue_comment_called += 1
        self.last_comment_id = comment_id
        if self.side_effect_get_issue_comment:
            raise self.side_effect_get_issue_comment
        return self.comment


class MockRepo:
    def __init__(self):
        self.get_pull_called = 0
        self.last_pull_number = None
        self.pr = MockPR()
        self.side_effect_get_pull = None
        self.get_contents_called = 0
        self.last_path = None
        self.last_ref = None
        self.side_effect_get_contents = None  # Can be an exception or a function

    def get_pull(self, pull_number):
        self.get_pull_called += 1
        self.last_pull_number = pull_number
        if self.side_effect_get_pull:
            raise self.side_effect_get_pull
        return self.pr

    def get_contents(self, path, ref=None):
        self.get_contents_called += 1
        self.last_path = path
        self.last_ref = ref
        if self.side_effect_get_contents:
            if isinstance(self.side_effect_get_contents, dict):
                if path in self.side_effect_get_contents:
                    exc = self.side_effect_get_contents[path]
                    if exc:
                        raise exc
            elif callable(self.side_effect_get_contents):
                return self.side_effect_get_contents(path, ref)
            else:
                raise self.side_effect_get_contents
        return "content"


class MockGithubInstance:
    def __init__(self):
        self.get_user_called = 0
        self.side_effect_get_user = None
        self.get_repo_called = 0
        self.last_repo_name = None
        self.repo = MockRepo()
        self.side_effect_get_repo = None

    def get_user(self):
        self.get_user_called += 1
        if self.side_effect_get_user:
            raise self.side_effect_get_user
        return "user"

    def get_repo(self, name):
        self.get_repo_called += 1
        self.last_repo_name = name
        if self.side_effect_get_repo:
            raise self.side_effect_get_repo
        return self.repo


class MockGithubClass:
    def __init__(self):
        self.call_count = 0
        self.last_kwargs = {}
        self.instance = MockGithubInstance()

    def __call__(self, **kwargs):
        self.call_count += 1
        self.last_kwargs = kwargs
        return self.instance


class MockAuthClass:
    class Token:
        def __init__(self, token):
            self.token = token


class MockLogger:
    def __init__(self):
        self.error_called = 0
        self.warning_called = 0

    def error(self, msg):
        self.error_called += 1

    def warning(self, msg):
        self.warning_called += 1


@pytest.fixture
def mock_github(monkeypatch):
    mock_gh_class = MockGithubClass()
    mock_auth_class = MockAuthClass()
    monkeypatch.setattr("utilities.vcs.github_functions.Github", mock_gh_class)
    monkeypatch.setattr("utilities.vcs.github_functions.Auth", mock_auth_class)
    return mock_gh_class, mock_auth_class


def test_get_github_client_success(patched_config_gitlab, ssm_setup, mock_github, expected_token_gitlab):
    from utilities.vcs.github_functions import _get_github_client
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    client = _get_github_client()

    assert client == mock_gh_class.instance
    assert mock_gh_class.call_count == 1
    assert mock_gh_class.last_kwargs["base_url"] == "https://gitlab.com"
    assert mock_gh_class.last_kwargs["auth"].token == expected_token_gitlab
    assert mock_gh_class.instance.get_user_called == 1


def test_get_github_client_failure(patched_config_gitlab, mock_github, monkeypatch):
    from utilities.vcs.github_functions import _get_github_client
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github
    mock_gh_class.instance.side_effect_get_user = Exception("Verification failed")

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.github_functions.logger", mock_logger)

    with pytest.raises(Exception, match="Verification failed"):
        _get_github_client()

    assert mock_logger.error_called == 1
    assert mock_gh_class.instance.get_user_called == 1


def test_get_github_client_caching(patched_config_gitlab, mock_github):
    from utilities.vcs.github_functions import _get_github_client
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    client1 = _get_github_client()
    client2 = _get_github_client()

    assert client1 is client2
    assert mock_gh_class.call_count == 1


def test_post_pr_comment_github_success(patched_config_gitlab, ssm_setup, mock_github):
    from utilities.vcs.github_functions import (_get_github_client,
                                                post_pr_comment_github)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    event = {
        "metadata": {
            "repo_id_or_name": "owner/repo",
            "merge_or_pull_req_id": 123
        }
    }
    comment_text = "Hello world"

    result = post_pr_comment_github(event, comment_text)

    assert result.body == "Hello world"
    assert mock_gh_class.instance.get_repo_called == 1
    assert mock_gh_class.instance.last_repo_name == "owner/repo"
    assert mock_gh_class.instance.repo.get_pull_called == 1
    assert mock_gh_class.instance.repo.last_pull_number == 123
    assert mock_gh_class.instance.repo.pr.create_issue_comment_called == 1
    assert mock_gh_class.instance.repo.pr.last_body == "Hello world"


@pytest.mark.parametrize("exception_class, match_msg", [
    (BadCredentialsException, "Auth failed"),
    (UnknownObjectException, "Not found"),
    (GithubException, "API error"),
    (Exception, "Unexpected error")
])
def test_post_pr_comment_github_failures(patched_config_gitlab, mock_github, monkeypatch, exception_class, match_msg):
    from utilities.vcs.github_functions import (_get_github_client,
                                                post_pr_comment_github)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    # Setup failure at create_issue_comment
    if exception_class in (BadCredentialsException, UnknownObjectException, GithubException):
        # PyGithub exceptions usually take (status, data, headers)
        exc = exception_class(401 if exception_class == BadCredentialsException else 404, {"message": match_msg}, {})
    else:
        exc = exception_class(match_msg)

    mock_gh_class.instance.repo.pr.side_effect_create_comment = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.github_functions.logger", mock_logger)

    event = {
        "metadata": {
            "repo_id_or_name": "owner/repo",
            "merge_or_pull_req_id": 123
        }
    }

    with pytest.raises(exception_class):
        post_pr_comment_github(event, "test")

    assert mock_logger.error_called == 1


def test_post_help_message_github_success(patched_config_gitlab, ssm_setup, mock_github):
    from utilities.vcs.github_functions import (_get_github_client,
                                                post_help_message_github)
    from utilities.messages import HELP_MESSAGE
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    event = {
        "metadata": {
            "repo_id_or_name": "owner/repo",
            "merge_or_pull_req_id": 123
        }
    }

    result = post_help_message_github(event)

    expected_body = HELP_MESSAGE.format(spec_provider='GitHub PR comments')
    assert result.body == expected_body
    assert mock_gh_class.instance.repo.pr.last_body == expected_body


def test_get_pr_source_branch_name_success(patched_config_gitlab, ssm_setup, mock_github):
    from utilities.vcs.github_functions import (_get_github_client,
                                                get_pr_source_branch_name)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github
    mock_gh_class.instance.repo.pr.head.ref = "test-branch"

    branch_name = get_pr_source_branch_name("owner/repo", 123)

    assert branch_name == "test-branch"
    assert mock_gh_class.instance.get_repo_called == 1
    assert mock_gh_class.instance.last_repo_name == "owner/repo"
    assert mock_gh_class.instance.repo.get_pull_called == 1
    assert mock_gh_class.instance.repo.last_pull_number == 123


@pytest.mark.parametrize("exception_class, match_msg", [
    (BadCredentialsException, "Auth failed"),
    (UnknownObjectException, "Not found"),
    (GithubException, "API error"),
    (Exception, "Unexpected error")
])
def test_get_pr_source_branch_name_failures(patched_config_gitlab, mock_github, monkeypatch, exception_class,
                                            match_msg):
    from utilities.vcs.github_functions import (_get_github_client,
                                                get_pr_source_branch_name)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    if exception_class in (BadCredentialsException, UnknownObjectException, GithubException):
        exc = exception_class(401 if exception_class == BadCredentialsException else 404, {"message": match_msg}, {})
    else:
        exc = exception_class(match_msg)

    mock_gh_class.instance.repo.side_effect_get_pull = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.github_functions.logger", mock_logger)

    with pytest.raises(exception_class):
        get_pr_source_branch_name("owner/repo", 123)

    assert mock_logger.error_called == 1


def test_add_reaction_to_pr_comment_github_success(patched_config_gitlab, ssm_setup, mock_github):
    from utilities.vcs.github_functions import (_get_github_client,
                                                add_reaction_to_pr_comment_github)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    event = {
        "metadata": {
            "repo_id_or_name": "owner/repo",
            "merge_or_pull_req_id": 123,
            "comment_id": 456
        }
    }
    reaction = "+1"

    result = add_reaction_to_pr_comment_github(event, reaction)

    assert result == mock_gh_class.instance.repo.pr.comment
    assert mock_gh_class.instance.get_repo_called == 1
    assert mock_gh_class.instance.last_repo_name == "owner/repo"
    assert mock_gh_class.instance.repo.get_pull_called == 1
    assert mock_gh_class.instance.repo.last_pull_number == 123
    assert mock_gh_class.instance.repo.pr.get_issue_comment_called == 1
    assert mock_gh_class.instance.repo.pr.last_comment_id == 456
    assert mock_gh_class.instance.repo.pr.comment.create_reaction_called == 1
    assert mock_gh_class.instance.repo.pr.comment.last_reaction == "+1"


@pytest.mark.parametrize("exception_class, match_msg", [
    (BadCredentialsException, "Auth failed"),
    (UnknownObjectException, "Not found"),
    (GithubException, "API error"),
    (Exception, "Unexpected error")
])
def test_add_reaction_to_pr_comment_github_failures(patched_config_gitlab, mock_github, monkeypatch, exception_class,
                                                    match_msg):
    from utilities.vcs.github_functions import (_get_github_client,
                                                add_reaction_to_pr_comment_github)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    if exception_class in (BadCredentialsException, UnknownObjectException, GithubException):
        exc = exception_class(401 if exception_class == BadCredentialsException else 404, {"message": match_msg}, {})
    else:
        exc = exception_class(match_msg)

    mock_gh_class.instance.repo.pr.side_effect_get_issue_comment = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.github_functions.logger", mock_logger)

    event = {
        "metadata": {
            "repo_id_or_name": "owner/repo",
            "merge_or_pull_req_id": 123,
            "comment_id": 456
        }
    }

    with pytest.raises(exception_class):
        add_reaction_to_pr_comment_github(event, "heart")

    assert mock_logger.error_called == 1


def test_get_last_commit_sha_github_success(patched_config_gitlab, ssm_setup, mock_github):
    from utilities.vcs.github_functions import (_get_github_client,
                                                get_last_commit_sha_github)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github
    mock_gh_class.instance.repo.pr.head.sha = "latest-sha-123"

    sha = get_last_commit_sha_github("owner/repo", 123)

    assert sha == "latest-sha-123"
    assert mock_gh_class.instance.get_repo_called == 1
    assert mock_gh_class.instance.last_repo_name == "owner/repo"
    assert mock_gh_class.instance.repo.get_pull_called == 1
    assert mock_gh_class.instance.repo.last_pull_number == 123


@pytest.mark.parametrize("exception_class, match_msg", [
    (BadCredentialsException, "Auth failed"),
    (UnknownObjectException, "Not found"),
    (GithubException, "API error"),
    (Exception, "Unexpected error")
])
def test_get_last_commit_sha_github_failures(patched_config_gitlab, mock_github, monkeypatch, exception_class,
                                             match_msg):
    from utilities.vcs.github_functions import (_get_github_client,
                                                get_last_commit_sha_github)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    if exception_class in (BadCredentialsException, UnknownObjectException, GithubException):
        exc = exception_class(401 if exception_class == BadCredentialsException else 404, {"message": match_msg}, {})
    else:
        exc = exception_class(match_msg)

    mock_gh_class.instance.repo.side_effect_get_pull = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.github_functions.logger", mock_logger)

    with pytest.raises(exception_class):
        get_last_commit_sha_github("owner/repo", 123)

    assert mock_logger.error_called == 1


def test_check_files_exist_in_repo_github_success(patched_config_gitlab, ssm_setup, mock_github):
    from utilities.vcs.github_functions import (_get_github_client,
                                                check_files_exist_in_repo_github)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    event = {
        "metadata": {
            "repo_id_or_name": "owner/repo",
            "merge_or_pull_req_id": 123
        }
    }
    file_paths = ["file1.txt", "file2.txt"]

    # Case 1: All files exist
    result = check_files_exist_in_repo_github(event, file_paths)
    assert result is True
    assert mock_gh_class.instance.repo.get_contents_called == 2
    assert mock_gh_class.instance.get_repo_called == 2
    assert mock_gh_class.instance.repo.last_ref == "feature-branch"

    # Case 2: Some files missing
    mock_gh_class.instance.repo.get_contents_called = 0
    mock_gh_class.instance.get_repo_called = 0
    mock_gh_class.instance.repo.side_effect_get_contents = {
        "file2.txt": UnknownObjectException(404, {"message": "Not found"}, {})
    }

    result = check_files_exist_in_repo_github(event, file_paths)
    assert result is False
    assert mock_gh_class.instance.repo.get_contents_called == 2
    assert mock_gh_class.instance.get_repo_called == 2


@pytest.mark.parametrize("exception_class, match_msg", [
    (BadCredentialsException, "Auth failed"),
    (UnknownObjectException, "Not found"),
    (GithubException, "API error"),
    (Exception, "Unexpected error")
])
def test_check_files_exist_in_repo_github_failures(patched_config_gitlab, mock_github, monkeypatch, exception_class,
                                                   match_msg):
    from utilities.vcs.github_functions import (_get_github_client,
                                                check_files_exist_in_repo_github)
    _get_github_client.cache_clear()
    mock_gh_class, _ = mock_github

    # Mock get_pr_source_branch_name to return a dummy branch and avoid its own logging
    monkeypatch.setattr("utilities.vcs.github_functions.get_pr_source_branch_name", lambda r, p: "main")

    if exception_class in (BadCredentialsException, UnknownObjectException, GithubException):
        exc = exception_class(401 if exception_class == BadCredentialsException else 404, {"message": match_msg}, {})
    else:
        exc = exception_class(match_msg)

    # Put the exception on get_repo to trigger the outer catch block in check_files_exist_in_repo_github
    mock_gh_class.instance.side_effect_get_repo = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.github_functions.logger", mock_logger)

    event = {
        "metadata": {
            "repo_id_or_name": "owner/repo",
            "merge_or_pull_req_id": 123
        }
    }

    with pytest.raises(exception_class):
        check_files_exist_in_repo_github(event, ["file1.txt"])

    assert mock_logger.error_called == 1


# --- New tests for commit_files_to_branch_github ---

class MockGitBlob:
    def __init__(self, sha):
        self.sha = sha


class MockGitTree:
    def __init__(self, sha):
        self.sha = sha


class MockGitCommit:
    def __init__(self, sha, tree=None):
        self.sha = sha
        self.tree = tree


class MockGitRef:
    def __init__(self, sha):
        self.object = MockGitCommit(sha)
        self.edit_called = 0
        self.last_commit_sha = None

    def edit(self, sha):
        self.edit_called += 1
        self.last_commit_sha = sha


class MockRepoCommit:
    def __init__(self):
        self.create_git_blob_called = 0
        self.create_git_tree_called = 0
        self.create_git_commit_called = 0
        self.git_ref = MockGitRef("initial-sha")

    def get_git_ref(self, ref):
        return self.git_ref

    def get_git_commit(self, sha):
        return MockGitCommit(sha)

    def create_git_blob(self, content, encoding):
        self.create_git_blob_called += 1
        return MockGitBlob(f"blob-sha-{self.create_git_blob_called}")

    def create_git_tree(self, tree_elements, base_tree=None):
        self.create_git_tree_called += 1
        return MockGitTree("tree-sha")

    def create_git_commit(self, message, tree, parents):
        self.create_git_commit_called += 1
        return MockGitCommit("new-commit-sha")


class MockRepoWithCommit(MockRepo):
    def __init__(self):
        super().__init__()
        self.commit_mock = MockRepoCommit()
        self.side_effect_get_ref = None

    def get_git_ref(self, ref):
        if self.side_effect_get_ref:
            raise self.side_effect_get_ref
        return self.commit_mock.get_git_ref(ref)

    def get_git_commit(self, sha):
        return self.commit_mock.get_git_commit(sha)

    def create_git_blob(self, content, encoding):
        return self.commit_mock.create_git_blob(content, encoding)

    def create_git_tree(self, tree_elements, base_tree=None):
        return self.commit_mock.create_git_tree(tree_elements, base_tree)

    def create_git_commit(self, message, tree, parents):
        return self.commit_mock.create_git_commit(message, tree, parents)


def test_commit_files_to_branch_github_success(patched_config_gitlab, mock_github, monkeypatch):
    from utilities.vcs.github_functions import commit_files_to_branch_github, _get_github_client
    _get_github_client.cache_clear()

    # Use the extended mock repo
    mock_gh_class, _ = mock_github
    mock_gh_class.instance.repo = MockRepoWithCommit()

    event = {"metadata": {"repo_id_or_name": "owner/repo", "merge_or_pull_req_id": 123}}
    files = [("file1.txt", "content1")]

    commit_files_to_branch_github(event, files, "msg")

    assert mock_gh_class.instance.repo.commit_mock.create_git_blob_called == 1
    assert mock_gh_class.instance.repo.commit_mock.create_git_tree_called == 1
    assert mock_gh_class.instance.repo.commit_mock.create_git_commit_called == 1
    assert mock_gh_class.instance.repo.commit_mock.git_ref.edit_called == 1


@pytest.mark.parametrize("exception_class, match_msg", [
    (BadCredentialsException, "Auth failed"),
    (UnknownObjectException, "Not found"),
    (GithubException, "API error"),
    (Exception, "Unexpected error")
])
def test_commit_files_to_branch_github_failures(patched_config_gitlab, mock_github, monkeypatch, exception_class,
                                                match_msg):
    from utilities.vcs.github_functions import commit_files_to_branch_github, _get_github_client
    _get_github_client.cache_clear()

    mock_gh_class, _ = mock_github
    mock_gh_class.instance.repo = MockRepoWithCommit()

    if exception_class in (BadCredentialsException, UnknownObjectException, GithubException):
        exc = exception_class(401 if exception_class == BadCredentialsException else 404, {"message": match_msg}, {})
    else:
        exc = exception_class(match_msg)

    mock_gh_class.instance.repo.side_effect_get_ref = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.github_functions.logger", mock_logger)

    event = {"metadata": {"repo_id_or_name": "owner/repo", "merge_or_pull_req_id": 123}}

    with pytest.raises(exception_class):
        commit_files_to_branch_github(event, [("f", "c")], "msg")

    assert mock_logger.error_called == 1


# --- New test for get_all_tf_files_from_paths_list_github ---

class MockContentItem:
    def __init__(self, path, type, content):
        self.path = path
        self.type = type
        self.decoded_content = content.encode("utf-8")


def test_get_all_tf_files_from_paths_list_github_success(patched_config_gitlab, mock_github, monkeypatch):
    from utilities.vcs.github_functions import get_all_tf_files_from_paths_list_github, _get_github_client
    _get_github_client.cache_clear()

    mock_gh_class, _ = mock_github

    # Mock return values for get_contents
    item1 = MockContentItem("dir/main.tf", "file", "content1")
    item2 = MockContentItem("dir/vars.txt", "file", "other")
    item3 = MockContentItem("dir/other.tf", "file", "content2")

    def get_contents_side_effect(path, ref=None):
        return [item1, item2, item3]

    mock_gh_class.instance.repo.side_effect_get_contents = get_contents_side_effect

    event = {"metadata": {"repo_id_or_name": "owner/repo", "source_branch": "main"}}
    paths = ["dir"]

    results = get_all_tf_files_from_paths_list_github(event, paths)

    assert len(results) == 2
    assert results[0] == ("dir/main.tf", "content1")
    assert results[1] == ("dir/other.tf", "content2")


def test_get_all_tf_files_from_paths_list_github_exception(patched_config_gitlab, mock_github, monkeypatch):
    from utilities.vcs.github_functions import get_all_tf_files_from_paths_list_github, _get_github_client
    _get_github_client.cache_clear()

    mock_gh_class, _ = mock_github

    # Trigger GithubException on get_contents
    mock_gh_class.instance.repo.side_effect_get_contents = GithubException(404, {"message": "Not found"}, {})

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.github_functions.logger", mock_logger)

    event = {"metadata": {"repo_id_or_name": "owner/repo", "source_branch": "main"}}
    paths = ["dir"]

    results = get_all_tf_files_from_paths_list_github(event, paths)

    assert results == []
    assert mock_logger.error_called == 0  # It should log warning
