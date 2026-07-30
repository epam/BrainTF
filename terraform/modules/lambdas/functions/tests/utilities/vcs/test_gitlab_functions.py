import base64

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
        self.source_branch = "feature-branch"


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
        self.commits = MockCommits()
        self.files = MockFiles()
        self.repository_tree_called = 0
        self.repository_tree_calls = []
        self.repository_tree_return_by_path = {}
        self.repository_tree_side_effect_by_path = {}

    def repository_tree(self, path=None, ref=None, recursive=False):
        self.repository_tree_called += 1
        self.repository_tree_calls.append({
            "path": path,
            "ref": ref,
            "recursive": recursive,
        })
        if path in self.repository_tree_side_effect_by_path:
            raise self.repository_tree_side_effect_by_path[path]
        return self.repository_tree_return_by_path.get(path, [])


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


class MockCommit:
    def __init__(self, data):
        self.id = "abc123"
        self.attributes = data


class MockCommits:
    def __init__(self):
        self.create_called = 0
        self.last_data = None
        self.side_effect_create = None

    def create(self, data):
        self.create_called += 1
        self.last_data = data
        if self.side_effect_create:
            raise self.side_effect_create
        return MockCommit(data)


class MockFile:
    def __init__(self, content):
        self.content = content


class MockFiles:
    def __init__(self):
        self.get_called = 0
        self.get_calls = []
        self.content_by_path = {}
        self.side_effect_get = None

    def get(self, file_path, ref):
        self.get_called += 1
        self.get_calls.append({"file_path": file_path, "ref": ref})
        if self.side_effect_get:
            raise self.side_effect_get
        return MockFile(self.content_by_path[file_path])


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

    def info(self, msg):
        return None

    def debug(self, msg):
        return None


@pytest.fixture
def mock_gitlab(monkeypatch):
    mock_gl_class = MockGitlabClass()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.gitlab.Gitlab", mock_gl_class)
    return mock_gl_class


def test_get_gitlab_client_success(patched_config_gitlab, ssm_setup, mock_gitlab, expected_token_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client
    _get_gitlab_client.cache_clear()

    client = _get_gitlab_client(expected_token_gitlab)

    assert client == mock_gitlab.instance
    assert mock_gitlab.call_count == 1
    assert mock_gitlab.last_kwargs == {
        "url": "https://gitlab.com",
        "private_token": expected_token_gitlab
    }
    assert mock_gitlab.instance.auth_called == 1
    assert mock_gitlab.instance.version_called == 1

def test_get_gitlab_client_auth_failure(patched_config_gitlab, mock_gitlab, expected_token_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client
    _get_gitlab_client.cache_clear()
    mock_gitlab.instance.side_effect_auth = gitlab.GitlabAuthenticationError("Auth failed")

    with pytest.raises(gitlab.GitlabAuthenticationError, match="Auth failed"):
        _get_gitlab_client(expected_token_gitlab)

    assert mock_gitlab.instance.auth_called == 1

def test_get_gitlab_client_version_failure(patched_config_gitlab, mock_gitlab, monkeypatch, expected_token_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client
    _get_gitlab_client.cache_clear()
    mock_gitlab.instance.side_effect_version = Exception("Version check failed")

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.logger", mock_logger)

    with pytest.raises(Exception, match="Version check failed"):
        _get_gitlab_client(expected_token_gitlab)

    assert mock_logger.error_called >= 1
    assert mock_gitlab.instance.auth_called == 1
    assert mock_gitlab.instance.version_called == 1

def test_get_gitlab_client_caching(patched_config_gitlab, mock_gitlab, expected_token_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client
    _get_gitlab_client.cache_clear()

    client1 = _get_gitlab_client(expected_token_gitlab)
    client2 = _get_gitlab_client(expected_token_gitlab)
    _get_gitlab_client("rotated-token")

    assert client1 is client2
    assert mock_gitlab.call_count == 2


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

    assert mock_logger.error_called >= 1


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


def test_get_mr_source_branch_name_success(patched_config_gitlab, ssm_setup, mock_gitlab):
    from utilities.vcs.gitlab_functions import (_get_gitlab_client,
                                                get_mr_source_branch_name)
    _get_gitlab_client.cache_clear()

    project_id = "group/project"
    mr_id = 456
    mock_gitlab.instance.projects.project.mergerequests.mr.source_branch = "test-branch"

    result = get_mr_source_branch_name(project_id, mr_id)

    assert result == "test-branch"
    assert mock_gitlab.instance.projects.get_called == 1
    assert mock_gitlab.instance.projects.last_id == project_id
    assert mock_gitlab.instance.projects.project.mergerequests.get_called == 1
    assert mock_gitlab.instance.projects.project.mergerequests.last_iid == mr_id


@pytest.mark.parametrize("exception_class, match_msg, failure_at", [
    (gitlab.GitlabAuthenticationError, "Auth failed", "project"),
    (gitlab.GitlabGetError, "Not found", "mr"),
    (Exception, "Unexpected error", "project")
])
def test_get_mr_source_branch_name_failures(patched_config_gitlab, mock_gitlab, monkeypatch, exception_class, match_msg, failure_at):
    from utilities.vcs.gitlab_functions import (_get_gitlab_client,
                                                get_mr_source_branch_name)
    _get_gitlab_client.cache_clear()

    if exception_class in (gitlab.GitlabAuthenticationError, gitlab.GitlabGetError):
        exc = exception_class(match_msg, response_code=401 if exception_class == gitlab.GitlabAuthenticationError else 404)
    else:
        exc = exception_class(match_msg)

    if failure_at == "project":
        mock_gitlab.instance.projects.side_effect_get = exc
    else:
        mock_gitlab.instance.projects.project.mergerequests.side_effect_get = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.logger", mock_logger)

    with pytest.raises(exception_class):
        get_mr_source_branch_name("group/project", 456)

    assert mock_logger.error_called >= 1

# --- New tests for add_award_to_note_gitlab ---

class MockAwardEmojis:
    def __init__(self):
        self.create_called = 0
        self.last_data = None
        self.side_effect_create = None

    def create(self, data):
        self.create_called += 1
        self.last_data = data
        if self.side_effect_create:
            raise self.side_effect_create
        class MockAward:
            def __init__(self, data):
                self.attributes = data
        return MockAward(data)

class MockNoteWithAwards(MockNote):
    def __init__(self, data):
        super().__init__(data)
        self.awardemojis = MockAwardEmojis()

class MockNotesWithAwards(MockNotes):
    def __init__(self):
        super().__init__()
        self.note = MockNoteWithAwards({"id": 789})
        self.side_effect_get = None
        self.get_called = 0
        self.last_comment_id = None

    def get(self, id):
        self.get_called += 1
        self.last_comment_id = id
        if self.side_effect_get:
            raise self.side_effect_get
        return self.note

def test_add_award_to_note_gitlab_success(patched_config_gitlab, mock_gitlab, monkeypatch):
    from utilities.vcs.gitlab_functions import add_award_to_note_gitlab, _get_gitlab_client
    _get_gitlab_client.cache_clear()
    
    # Inject mock with awardemojis
    mock_gitlab.instance.projects.project.mergerequests.mr.notes = MockNotesWithAwards()
    
    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
            "comment_id": 789
        }
    }
    reaction = "thumbsup"
    
    result = add_award_to_note_gitlab(event, reaction)
    
    assert result["name"] == reaction
    assert mock_gitlab.instance.projects.project.mergerequests.mr.notes.note.awardemojis.create_called == 1
    assert mock_gitlab.instance.projects.project.mergerequests.mr.notes.note.awardemojis.last_data["name"] == reaction

@pytest.mark.parametrize("exception_class, match_msg", [
    (gitlab.GitlabAuthenticationError, "Auth failed"),
    (gitlab.GitlabGetError, "Not found"),
    (Exception, "Unexpected error")
])
def test_add_award_to_note_gitlab_failures(patched_config_gitlab, mock_gitlab, monkeypatch, exception_class, match_msg):
    from utilities.vcs.gitlab_functions import add_award_to_note_gitlab, _get_gitlab_client
    _get_gitlab_client.cache_clear()
    
    mock_gitlab.instance.projects.project.mergerequests.mr.notes = MockNotesWithAwards()
    
    if exception_class in (gitlab.GitlabAuthenticationError, gitlab.GitlabGetError):
        exc = exception_class(match_msg, response_code=401 if exception_class == gitlab.GitlabAuthenticationError else 404)
    else:
        exc = exception_class(match_msg)
        
    mock_gitlab.instance.projects.project.mergerequests.mr.notes.note.awardemojis.side_effect_create = exc
    
    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.logger", mock_logger)
    
    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
            "comment_id": 789
        }
    }
    
    with pytest.raises(exception_class):
        add_award_to_note_gitlab(event, "thumbsup")
        
    assert mock_logger.error_called == 1


def test_check_files_exist_in_repo_gitlab_all_exist(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import check_files_exist_in_repo_gitlab, _get_gitlab_client
    _get_gitlab_client.cache_clear()

    project = mock_gitlab.instance.projects.project
    project.repository_tree_return_by_path = {
        "dir1": [{"name": "a.tf", "type": "blob"}, {"name": "subdir", "type": "tree"}],
        None: [{"name": "root.tf", "type": "blob"}],
    }

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
        }
    }

    result = check_files_exist_in_repo_gitlab(event, ["dir1/a.tf", "root.tf"])

    assert result is True
    assert project.repository_tree_called == 2
    assert project.repository_tree_calls[0]["ref"] == "feature-branch"
    assert project.repository_tree_calls[1]["ref"] == "feature-branch"


def test_check_files_exist_in_repo_gitlab_missing_file_returns_false(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import check_files_exist_in_repo_gitlab, _get_gitlab_client
    _get_gitlab_client.cache_clear()

    project = mock_gitlab.instance.projects.project
    project.repository_tree_return_by_path = {
        "dir1": [{"name": "present.tf", "type": "blob"}],
    }

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
        }
    }

    result = check_files_exist_in_repo_gitlab(event, ["dir1/missing.tf"])

    assert result is False


def test_check_files_exist_in_repo_gitlab_missing_directory_returns_false(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import check_files_exist_in_repo_gitlab, _get_gitlab_client
    _get_gitlab_client.cache_clear()

    project = mock_gitlab.instance.projects.project
    project.repository_tree_side_effect_by_path = {
        "missing-dir": gitlab.GitlabGetError("Not found", response_code=404),
    }

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
        }
    }

    result = check_files_exist_in_repo_gitlab(event, ["missing-dir/file1.tf", "missing-dir/file2.tf"])

    assert result is False


@pytest.mark.parametrize("exception_class, match_msg, failure_stage", [
    (gitlab.GitlabAuthenticationError, "Auth failed", "branch"),
    (gitlab.GitlabGetError, "API failed", "tree"),
    (Exception, "Unexpected error", "tree"),
])
def test_check_files_exist_in_repo_gitlab_failures(
        patched_config_gitlab, mock_gitlab, monkeypatch, exception_class, match_msg, failure_stage
):
    from utilities.vcs.gitlab_functions import (
        _get_gitlab_client,
        check_files_exist_in_repo_gitlab,
    )
    _get_gitlab_client.cache_clear()

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
        }
    }

    if exception_class in (gitlab.GitlabAuthenticationError, gitlab.GitlabGetError):
        exc = exception_class(match_msg, response_code=401 if exception_class == gitlab.GitlabAuthenticationError else 500)
    else:
        exc = exception_class(match_msg)

    if failure_stage == "branch":
        mock_gitlab.instance.projects.side_effect_get = exc
    else:
        mock_gitlab.instance.projects.project.repository_tree_side_effect_by_path = {"dir1": exc}

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.logger", mock_logger)

    file_paths = ["dir1/file.tf"] if failure_stage == "tree" else ["root.tf"]

    with pytest.raises(exception_class):
        check_files_exist_in_repo_gitlab(event, file_paths)

    assert mock_logger.error_called >= 1


def test_commit_files_to_branch_gitlab_success(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import commit_files_to_branch_gitlab, _get_gitlab_client
    _get_gitlab_client.cache_clear()

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
        }
    }
    file_paths_with_content = [
        ("dir1/main.tf", "content 1"),
        ("dir2/vars.tf", "content 2"),
    ]

    result = commit_files_to_branch_gitlab(event, file_paths_with_content, "update tf files")

    assert result["branch"] == "feature-branch"
    assert result["commit_message"] == "update tf files"
    assert result["actions"] == [
        {"action": "update", "file_path": "dir1/main.tf", "content": "content 1"},
        {"action": "update", "file_path": "dir2/vars.tf", "content": "content 2"},
    ]
    assert mock_gitlab.instance.projects.project.commits.create_called == 1


def test_commit_files_to_branch_gitlab_no_actions_returns_empty_dict(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import commit_files_to_branch_gitlab, _get_gitlab_client
    _get_gitlab_client.cache_clear()

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
        }
    }

    result = commit_files_to_branch_gitlab(event, [], "empty commit")

    assert result == {}
    assert mock_gitlab.instance.projects.project.commits.create_called == 0


@pytest.mark.parametrize("exception_class, match_msg, failure_at", [
    (gitlab.GitlabAuthenticationError, "Auth failed", "project"),
    (gitlab.GitlabGetError, "Not found", "mr"),
    (gitlab.GitlabCreateError, "Create failed", "commit"),
    (Exception, "Unexpected error", "commit"),
])
def test_commit_files_to_branch_gitlab_failures(
        patched_config_gitlab, mock_gitlab, monkeypatch, exception_class, match_msg, failure_at
):
    from utilities.vcs.gitlab_functions import commit_files_to_branch_gitlab, _get_gitlab_client
    _get_gitlab_client.cache_clear()

    if exception_class in (gitlab.GitlabAuthenticationError, gitlab.GitlabGetError, gitlab.GitlabCreateError):
        exc = exception_class(
            match_msg,
            response_code=401 if exception_class == gitlab.GitlabAuthenticationError else 404
        )
    else:
        exc = exception_class(match_msg)

    if failure_at == "project":
        mock_gitlab.instance.projects.side_effect_get = exc
    elif failure_at == "mr":
        mock_gitlab.instance.projects.project.mergerequests.side_effect_get = exc
    else:
        mock_gitlab.instance.projects.project.commits.side_effect_create = exc

    mock_logger = MockLogger()
    monkeypatch.setattr("utilities.vcs.gitlab_functions.logger", mock_logger)

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "merge_or_pull_req_id": 456,
        }
    }
    file_paths_with_content = [("dir1/main.tf", "content")]

    with pytest.raises(exception_class):
        commit_files_to_branch_gitlab(event, file_paths_with_content, "update tf files")

    assert mock_logger.error_called >= 1


def test_get_all_tf_files_from_paths_list_gitlab_success(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client, get_all_tf_files_from_paths_list_gitlab
    _get_gitlab_client.cache_clear()

    project = mock_gitlab.instance.projects.project
    project.repository_tree_return_by_path = {
        "dir1": [
            {"type": "blob", "name": "main.tf", "path": "dir1/main.tf"},
            {"type": "blob", "name": "notes.txt", "path": "dir1/notes.txt"},
        ],
        "dir2": [
            {"type": "blob", "name": "vars.tf", "path": "dir2/vars.tf"},
            {"type": "tree", "name": "nested", "path": "dir2/nested"},
        ],
    }
    project.files.content_by_path = {
        "dir1/main.tf": base64.b64encode(b'resource "aws_s3_bucket" "b" {}').decode("utf-8"),
        "dir2/vars.tf": base64.b64encode(b'variable "name" {}').decode("utf-8"),
    }

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "source_branch": "feature-branch",
        }
    }

    result = get_all_tf_files_from_paths_list_gitlab(event, ["dir1", "dir2"])

    assert result == [
        ("dir1/main.tf", 'resource "aws_s3_bucket" "b" {}'),
        ("dir2/vars.tf", 'variable "name" {}'),
    ]
    assert project.files.get_called == 2


def test_get_all_tf_files_from_paths_list_gitlab_no_tf_files(patched_config_gitlab, mock_gitlab):
    from utilities.vcs.gitlab_functions import _get_gitlab_client, get_all_tf_files_from_paths_list_gitlab
    _get_gitlab_client.cache_clear()

    project = mock_gitlab.instance.projects.project
    project.repository_tree_return_by_path = {
        "dir1": [
            {"type": "blob", "name": "readme.md", "path": "dir1/readme.md"},
            {"type": "tree", "name": "subdir", "path": "dir1/subdir"},
        ],
    }

    event = {
        "metadata": {
            "repo_id_or_name": "group/project",
            "source_branch": "feature-branch",
        }
    }

    result = get_all_tf_files_from_paths_list_gitlab(event, ["dir1"])

    assert result == []
    assert project.files.get_called == 0
