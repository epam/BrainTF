import pytest
from github.GithubException import (BadCredentialsException, GithubException,
                                    UnknownObjectException)


class MockIssueComment:
    def __init__(self, body):
        self.body = body


class MockPR:
    def __init__(self):
        self.create_issue_comment_called = 0
        self.last_body = None
        self.side_effect_create_comment = None

    def create_issue_comment(self, body):
        self.create_issue_comment_called += 1
        self.last_body = body
        if self.side_effect_create_comment:
            raise self.side_effect_create_comment
        return MockIssueComment(body)


class MockRepo:
    def __init__(self):
        self.get_pull_called = 0
        self.last_pull_number = None
        self.pr = MockPR()
        self.side_effect_get_pull = None

    def get_pull(self, pull_number):
        self.get_pull_called += 1
        self.last_pull_number = pull_number
        if self.side_effect_get_pull:
            raise self.side_effect_get_pull
        return self.pr


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


class MockAuthToken:
    def __init__(self, token):
        self.token = token


class MockAuthClass:
    @staticmethod
    def token(token):
        return MockAuthToken(token)

    Token = token


class MockLogger:
    def __init__(self):
        self.error_called = 0

    def error(self, msg):
        self.error_called += 1


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
