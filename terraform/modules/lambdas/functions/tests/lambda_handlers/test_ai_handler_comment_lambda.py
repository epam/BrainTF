import json

import pytest

from utilities.exceptions import (
    AuthorMismatchException,
    BranchMismatchException,
    MissingWebhookDataException,
)


def set_webhook_payload_value(event, path, value):
    webhook_payload = json.loads(event["body"])
    payload_section = webhook_payload
    for key in path[:-1]:
        payload_section = payload_section[key]
    payload_section[path[-1]] = value
    event["body"] = json.dumps(webhook_payload)


def test_process_vcs_webhook_payload_github(patched_config_github, webhook_event_github,
                                            expected_webhook_event_metadata_github, monkeypatch, caplog):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )
    result = process_vcs_webhook_payload(webhook_event_github)
    assert 'Processing VCS webhook payload...' in caplog.text
    assert isinstance(result, dict)
    assert webhook_event_github.get('metadata')
    assert result.get('metadata') == expected_webhook_event_metadata_github


def test_process_vcs_webhook_payload_gitlab(patched_config_gitlab, webhook_event_gitlab,
                                            expected_webhook_event_metadata_gitlab, caplog):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )
    result = process_vcs_webhook_payload(webhook_event_gitlab)
    assert 'Processing VCS webhook payload...' in caplog.text
    assert isinstance(result, dict)
    assert result.get('metadata')
    assert webhook_event_gitlab.get('metadata')
    assert result.get('metadata') == expected_webhook_event_metadata_gitlab


@pytest.mark.parametrize("missing_value", [None, ""], ids=["none", "empty"])
@pytest.mark.parametrize("payload_path", [
    ("merge_request", "last_commit", "id"),
    ("project_id",),
    ("merge_request", "source_branch"),
    ("object_attributes", "note"),
    ("merge_request", "iid"),
    ("object_attributes", "id"),
], ids=[
    "last_commit_id",
    "project_id",
    "source_branch",
    "note",
    "merge_request_iid",
    "comment_id",
])
def test_process_vcs_webhook_payload_gitlab_missing_data(patched_config_gitlab, webhook_event_gitlab, payload_path,
                                                         missing_value):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    set_webhook_payload_value(webhook_event_gitlab, payload_path, missing_value)

    with pytest.raises(MissingWebhookDataException):
        process_vcs_webhook_payload(webhook_event_gitlab)


@pytest.mark.parametrize("missing_value", [None, ""], ids=["none", "empty"])
@pytest.mark.parametrize("payload_path", [
    ("repository", "full_name"),
    ("comment", "body"),
    ("comment", "id"),
    ("issue", "number"),
], ids=[
    "repository_full_name",
    "comment_body",
    "comment_id",
    "issue_number",
])
def test_process_vcs_webhook_payload_github_missing_data(patched_config_github, webhook_event_github, payload_path,
                                                         missing_value):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    set_webhook_payload_value(webhook_event_github, payload_path, missing_value)

    with pytest.raises(MissingWebhookDataException):
        process_vcs_webhook_payload(webhook_event_github)


def test_process_vcs_webhook_payload_gitlab_preserves_zero_values(patched_config_gitlab, webhook_event_gitlab):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    webhook_payload = json.loads(webhook_event_gitlab["body"])
    webhook_payload["project_id"] = 0
    webhook_payload["merge_request"]["iid"] = 0
    webhook_payload["object_attributes"]["id"] = 0
    webhook_event_gitlab["body"] = json.dumps(webhook_payload)

    result = process_vcs_webhook_payload(webhook_event_gitlab)

    assert result["metadata"]["repo_id_or_name"] == 0
    assert result["metadata"]["merge_or_pull_req_id"] == 0
    assert result["metadata"]["comment_id"] == 0


def test_process_vcs_webhook_payload_github_preserves_zero_values(patched_config_github, webhook_event_github,
                                                                  monkeypatch):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    webhook_payload = json.loads(webhook_event_github["body"])
    webhook_payload["comment"]["id"] = 0
    webhook_payload["issue"]["number"] = 0
    webhook_event_github["body"] = json.dumps(webhook_payload)

    result = process_vcs_webhook_payload(webhook_event_github)

    assert result["metadata"]["comment_id"] == 0
    assert result["metadata"]["merge_or_pull_req_id"] == 0


@pytest.mark.parametrize(("provider_fixture", "payload_update"), [
    ("patched_config_gitlab", {"merge_request": None}),
    ("patched_config_gitlab", {"object_attributes": None}),
    ("patched_config_github", {"repository": None}),
    ("patched_config_github", {"comment": None}),
], ids=[
    "gitlab_missing_merge_request",
    "gitlab_missing_object_attributes",
    "github_missing_repository",
    "github_missing_comment",
])
def test_process_vcs_webhook_payload_malformed_nested_data(request, provider_fixture, payload_update,
                                                           webhook_event_gitlab, webhook_event_github):
    request.getfixturevalue(provider_fixture)
    event = webhook_event_gitlab if provider_fixture == "patched_config_gitlab" else webhook_event_github
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    webhook_payload = json.loads(event["body"])
    webhook_payload.update(payload_update)
    event["body"] = json.dumps(webhook_payload)

    with pytest.raises(MissingWebhookDataException):
        process_vcs_webhook_payload(event)


def test_process_vcs_webhook_payload_wrong_vcs(patched_config_wrong_vcs, webhook_event_github,
                                               expected_webhook_event_metadata_github, monkeypatch):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    with pytest.raises(ValueError):
        process_vcs_webhook_payload(webhook_event_github)


def test_lambda_handler_http_status_codes(patched_environment):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        HTTP_BAD_REQUEST,
        HTTP_FORBIDDEN,
        HTTP_SUCCESS,
    )
    assert HTTP_SUCCESS == 200
    assert HTTP_BAD_REQUEST == 400
    assert HTTP_FORBIDDEN == 403


def test_lambda_handler_comment_event_gitlab(patched_config_gitlab, webhook_event_gitlab):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler
    lambda_handler(webhook_event_gitlab, {})


def test_lambda_handler_comment_event_invalid_token_gitlab(patched_config_gitlab, webhook_event_invalid_token_gitlab):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler
    result = lambda_handler(webhook_event_invalid_token_gitlab, {})
    assert result == {'body': 'Forbidden', 'statusCode': 403}


def test_lambda_handler_bad_event(patched_config_github):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler
    result = lambda_handler({}, {})
    assert isinstance(result, dict)
    assert result == {'statusCode': 400, 'body': 'Invalid payload'}


def test_lambda_handler_comment_event_bot_list(patched_config_github, webhook_event_github, monkeypatch):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")

    # Define a mock implementation for the function
    def mock_add_award_to_note(note_id, award_name):
        # Simulate the behavior you want or return a fake value
        return f"Mocked award '{award_name}' added to note {note_id}"

    monkeypatch.setattr("utilities.handlers.add_award_to_note",
                        mock_add_award_to_note)

    monkeypatch.setattr("utilities.handlers.post_comment",
                        lambda x, y: {})

    monkeypatch.setattr("utilities.handlers.get_file_names_from_s3_directory",
                        lambda x, y: [])

    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler

    result = lambda_handler(webhook_event_github, {})

    assert result == {'statusCode': 200, 'body': 'Successfully invoked'}


def test_lambda_handler_comment_event_missing_x_hub_signature_256(patched_config_github, webhook_event_github,
                                                                  monkeypatch):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")

    # Define a mock implementation for the function
    def mock_add_award_to_note(note_id, award_name):
        # Simulate the behavior you want or return a fake value
        return f"Mocked award '{award_name}' added to note {note_id}"

    monkeypatch.setattr("utilities.handlers.add_award_to_note",
                        mock_add_award_to_note)

    monkeypatch.setattr("utilities.handlers.post_comment",
                        lambda x, y: {})

    monkeypatch.setattr("utilities.handlers.get_file_names_from_s3_directory",
                        lambda x, y: [])

    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler

    headers = webhook_event_github.get('headers', {})
    headers.pop('x-hub-signature-256')
    webhook_event_github.update({'headers': headers})

    result = lambda_handler(webhook_event_github, {})

    assert result == {'body': 'Invalid payload', 'statusCode': 400}


def test_lambda_handler_comment_event_wrong_action_github(patched_config_github,
                                                          webhook_event_action_is_not_created_github,
                                                          monkeypatch):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")

    # Define a mock implementation for the function
    def mock_add_award_to_note(note_id, award_name):
        # Simulate the behavior you want or return a fake value
        return f"Mocked award '{award_name}' added to note {note_id}"

    monkeypatch.setattr("utilities.handlers.add_award_to_note",
                        mock_add_award_to_note)

    monkeypatch.setattr("utilities.handlers.post_comment",
                        lambda x, y: {})

    monkeypatch.setattr("utilities.handlers.get_file_names_from_s3_directory",
                        lambda x, y: [])

    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler

    result = lambda_handler(webhook_event_action_is_not_created_github, {})

    assert result == {'body': 'Out of bot context, no action taken', 'statusCode': 200}


# --- Per-branch instance filtering (TARGET_BRANCH) ---------------------------------------------------------------

MODULE = "ai_handler_comment_lambda.ai_handler_comment_lambda"
OTHER_BRANCH_RESULT = {'statusCode': 200, 'body': "Not this instance's branch, no action taken"}


def _fail_if_called(*args, **kwargs):
    raise AssertionError("must not be called")


def _set_target_branch(monkeypatch, branch):
    from config import config
    monkeypatch.setattr(config, "target_branch", branch)


def test_process_vcs_webhook_payload_github_target_branch_match(patched_config_github, webhook_event_github,
                                                                monkeypatch):
    _set_target_branch(monkeypatch, "feature-x")
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", lambda repo, number: "feature-x")
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    result = process_vcs_webhook_payload(webhook_event_github)

    assert result['metadata']['commit_short_sha'] == "1234"
    # The filter must not change what the rest of the handler sees for GitHub.
    assert result['metadata']['source_branch'] is None


def test_lambda_handler_github_other_branch_is_ignored(patched_config_github, webhook_event_github, monkeypatch):
    _set_target_branch(monkeypatch, "feature-x")
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", lambda repo, number: "someone-elses-branch")
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", _fail_if_called)
    monkeypatch.setattr(f"{MODULE}.handle_comment_commands", _fail_if_called)
    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler

    assert lambda_handler(webhook_event_github, {}) == OTHER_BRANCH_RESULT


def test_process_vcs_webhook_payload_github_issue_comment_is_ignored(patched_config_github, webhook_event_github,
                                                                     monkeypatch):
    _set_target_branch(monkeypatch, "feature-x")
    payload = json.loads(webhook_event_github["body"])
    del payload["issue"]["pull_request"]
    webhook_event_github["body"] = json.dumps(payload)
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", _fail_if_called)
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", _fail_if_called)
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    with pytest.raises(BranchMismatchException):
        process_vcs_webhook_payload(webhook_event_github)


def test_process_vcs_webhook_payload_github_no_target_branch_handles_everything(patched_config_github,
                                                                               webhook_event_github, monkeypatch):
    _set_target_branch(monkeypatch, "")
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", _fail_if_called)
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    assert process_vcs_webhook_payload(webhook_event_github)['metadata']['commit_short_sha'] == "1234"


def test_process_vcs_webhook_payload_gitlab_target_branch_match(patched_config_gitlab, webhook_event_gitlab,
                                                                monkeypatch):
    _set_target_branch(monkeypatch, "SYNC-branch")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    result = process_vcs_webhook_payload(webhook_event_gitlab)

    assert result['metadata']['source_branch'] == "SYNC-branch"


def test_lambda_handler_gitlab_other_branch_is_ignored(patched_config_gitlab, webhook_event_gitlab, monkeypatch):
    _set_target_branch(monkeypatch, "feature-x")
    monkeypatch.setattr(f"{MODULE}.handle_comment_commands", _fail_if_called)
    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler

    assert lambda_handler(webhook_event_gitlab, {}) == OTHER_BRANCH_RESULT


# --- Personal instance filtering (OWNER_GITHUB) ------------------------------------------------------------------

OTHER_OWNER_RESULT = {'statusCode': 200, 'body': "Not this instance's owner, no action taken"}
# The github webhook fixture's pull request author (issue.user.login).
FIXTURE_PR_AUTHOR = "testuser"


def _set_owner_github(monkeypatch, owner):
    from config import config
    monkeypatch.setattr(config, "owner_github", owner)


def test_process_vcs_webhook_payload_github_owner_match(patched_config_github, webhook_event_github, monkeypatch):
    _set_owner_github(monkeypatch, FIXTURE_PR_AUTHOR)
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    result = process_vcs_webhook_payload(webhook_event_github)

    assert result['metadata']['commit_short_sha'] == "1234"


def test_lambda_handler_github_other_owner_is_ignored(patched_config_github, webhook_event_github, monkeypatch):
    _set_owner_github(monkeypatch, "someone-else")
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", _fail_if_called)
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", _fail_if_called)
    monkeypatch.setattr(f"{MODULE}.handle_comment_commands", _fail_if_called)
    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler

    assert lambda_handler(webhook_event_github, {}) == OTHER_OWNER_RESULT


def test_process_vcs_webhook_payload_github_owner_issue_comment_is_ignored(patched_config_github,
                                                                         webhook_event_github, monkeypatch):
    _set_owner_github(monkeypatch, FIXTURE_PR_AUTHOR)
    payload = json.loads(webhook_event_github["body"])
    del payload["issue"]["pull_request"]
    webhook_event_github["body"] = json.dumps(payload)
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", _fail_if_called)
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", _fail_if_called)
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    with pytest.raises(AuthorMismatchException):
        process_vcs_webhook_payload(webhook_event_github)


def test_process_vcs_webhook_payload_github_owner_missing_user_is_ignored(patched_config_github,
                                                                          webhook_event_github, monkeypatch):
    _set_owner_github(monkeypatch, FIXTURE_PR_AUTHOR)
    payload = json.loads(webhook_event_github["body"])
    del payload["issue"]["user"]
    webhook_event_github["body"] = json.dumps(payload)
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", _fail_if_called)
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    with pytest.raises(AuthorMismatchException):
        process_vcs_webhook_payload(webhook_event_github)


def test_process_vcs_webhook_payload_github_no_owner_handles_everything(patched_config_github,
                                                                        webhook_event_github, monkeypatch):
    _set_owner_github(monkeypatch, "")
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", _fail_if_called)
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    assert process_vcs_webhook_payload(webhook_event_github)['metadata']['commit_short_sha'] == "1234"


def test_lambda_handler_github_owner_checked_before_branch(patched_config_github, webhook_event_github,
                                                           monkeypatch):
    _set_owner_github(monkeypatch, "someone-else")
    _set_target_branch(monkeypatch, "feature-x")
    # An author mismatch must short-circuit before the branch check's API call.
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", _fail_if_called)
    monkeypatch.setattr(f"{MODULE}.handle_comment_commands", _fail_if_called)
    from ai_handler_comment_lambda.ai_handler_comment_lambda import lambda_handler

    assert lambda_handler(webhook_event_github, {}) == OTHER_OWNER_RESULT


def test_process_vcs_webhook_payload_github_owner_and_branch_match(patched_config_github, webhook_event_github,
                                                                   monkeypatch):
    _set_owner_github(monkeypatch, FIXTURE_PR_AUTHOR)
    _set_target_branch(monkeypatch, "feature-x")
    monkeypatch.setattr(f"{MODULE}.get_pr_head_ref_github", lambda repo, number: "feature-x")
    monkeypatch.setattr(f"{MODULE}.get_last_commit_sha_github", lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import (
        process_vcs_webhook_payload,
    )

    result = process_vcs_webhook_payload(webhook_event_github)

    assert result['metadata']['commit_short_sha'] == "1234"
