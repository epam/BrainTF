import gitlab
import pytest


class MockNote:
    def __init__(self, data):
        self.attributes = data


class MockNotes:
    def __init__(self):
        self.create_called = 0
        self.last_data = None
        self.side_effect_create = None

    def create(self, data):
        self.create_called += 1
        self.last_data = data
        if self.side_effect_create:
            raise self.side_effect_create
        return MockNote(data)


class MockMergeRequest:
    def __init__(self):
        self.notes = MockNotes()


class MockMergeRequests:
    def __init__(self):
        self.get_called = 0
        self.last_iid = None
        self.mr = MockMergeRequest()
        self.side_effect_get = None

    def get(self, iid):
        self.get_called += 1
        self.last_iid = iid
        if self.side_effect_get:
            raise self.side_effect_get
        return self.mr


class MockProject:
    def __init__(self):
        self.mergerequests = MockMergeRequests()


class MockProjects:
    def __init__(self):
        self.get_called = 0
        self.last_id = None
        self.project = MockProject()
        self.side_effect_get = None

    def get(self, id):
        self.get_called += 1
        self.last_id = id
        if self.side_effect_get:
            raise self.side_effect_get
        return self.project


class MockGitlabInstance:
    def __init__(self):
        self.auth_called = 0
        self.version_called = 0
        self.side_effect_auth = None
        self.side_effect_version = None
        self.projects = MockProjects()

    def auth(self):
        self.auth_called += 1
        if self.side_effect_auth:
            raise self.side_effect_auth

    def version(self):
        self.version_called += 1
        if self.side_effect_version:
            raise self.side_effect_version


class MockGitlabClass:
    def __init__(self):
        self.call_count = 0
        self.last_kwargs = {}
        self.instance = MockGitlabInstance()

    def __call__(self, **kwargs):
        self.call_count += 1
        self.last_kwargs = kwargs
        return self.instance


class MockLogger:
    def __init__(self):
        self.error_called = 0

    def error(self, msg):
        self.error_called += 1


@pytest.fixture
def mock_gitlab(monkeypatch):
    mock_gl_class = MockGitlabClass()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.gitlab.Gitlab", mock_gl_class)
    return mock_gl_class


def test_get_gitlab_client_success(patched_config_gitlab, ssm_setup, mock_gitlab, expected_token_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client
    _get_gitlab_client.cache_clear()

    client = _get_gitlab_client()

    assert client == mock_gitlab.instance
    assert mock_gitlab.call_count == 1
    assert mock_gitlab.last_kwargs == {
        "url": "https://gitlab.com",
        "private_token": expected_token_gitlab
    }
    assert mock_gitlab.instance.auth_called == 1
    assert mock_gitlab.instance.version_called == 1

def test_get_gitlab_client_auth_failure(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client
    _get_gitlab_client.cache_clear()
    mock_gitlab.instance.side_effect_auth = gitlab.GitlabAuthenticationError("Auth failed")

    with pytest.raises(gitlab.GitlabAuthenticationError, match="Auth failed"):
        _get_gitlab_client()

    assert mock_gitlab.instance.auth_called == 1

def test_get_gitlab_client_version_failure(patched_config_gitlab, mock_gitlab,monkeypatch):
    from utilities.vcs.gitlab_functions import _get_gitlab_client
    _get_gitlab_client.cache_clear()
    mock_gitlab.instance.side_effect_version = Exception("Version check failed")

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.logger", mock_logger)

    with pytest.raises(Exception, match="Version check failed"):
        _get_gitlab_client()

    assert mock_logger.error_called == 1
    assert mock_gitlab.instance.auth_called == 1
    assert mock_gitlab.instance.version_called == 1

def test_get_gitlab_client_caching(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client
    _get_gitlab_client.cache_clear()

    client1 = _get_gitlab_client()
    client2 = _get_gitlab_client()

    assert client1 is client2
    assert mock_gitlab.call_count == 1


def test_post_gitlab_comment_success(patched_config_gitlab, ssm_setup, mock_gitlab):
    from utilities.vcs.gitlab_functions import (_get_gitlab_client,
                                                post_gitlab_comment)
    _get_gitlab_client.cache_clear()

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456
        }
    }
    comment_text = "Test GitLab comment"

    result = post_gitlab_comment(event, comment_text)

    assert result == {"body": "Test GitLab comment"}
    assert mock_gitlab.instance.projects.get_called == 1
    assert mock_gitlab.instance.projects.last_id == "group/project"
    assert mock_gitlab.instance.projects.project.mergerequests.get_called == 1
    assert mock_gitlab.instance.projects.project.mergerequests.last_iid == 456
    assert mock_gitlab.instance.projects.project.mergerequests.mr.notes.create_called == 1
    assert mock_gitlab.instance.projects.project.mergerequests.mr.notes.last_data == {"body": "Test GitLab comment"}


@pytest.mark.parametrize("exception_class, match_msg", [
    (gitlab.GitlabAuthenticationError, "Auth failed"),
    (gitlab.GitlabGetError, "Not found"),
    (Exception, "Unexpected error")
])
def test_post_gitlab_comment_failures(patched_config_gitlab, mock_gitlab, monkeypatch, exception_class, match_msg):
    from utilities.vcs.gitlab_functions import (_get_gitlab_client,
                                                post_gitlab_comment)
    _get_gitlab_client.cache_clear()

    # Setup failure at notes.create
    if exception_class in (gitlab.GitlabAuthenticationError, gitlab.GitlabGetError):
        exc = exception_class(match_msg, response_code=401 if exception_class == gitlab.GitlabAuthenticationError else 404)
    else:
        exc = exception_class(match_msg)

    mock_gitlab.instance.projects.project.mergerequests.mr.notes.side_effect_create = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.logger", mock_logger)

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456
        }
    }

    with pytest.raises(exception_class):
        post_gitlab_comment(event, "test")

    assert mock_logger.error_called == 1


def test_post_help_message_gitlab_success(patched_config_gitlab, ssm_setup, mock_gitlab):
    from utilities.messages import HELP_MESSAGE
    from utilities.vcs.gitlab_functions import (_get_gitlab_client,
                                                post_help_message_gitlab)
    _get_gitlab_client.cache_clear()

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456
        }
    }

    expected_help_message = HELP_MESSAGE.format(spec_provider='GitLab MR notes')

    result = post_help_message_gitlab(event)

    assert result == {"body": expected_help_message}
    assert mock_gitlab.instance.projects.project.mergerequests.mr.notes.create_called == 1
    assert mock_gitlab.instance.projects.project.mergerequests.mr.notes.last_data == {"body": expected_help_message}
