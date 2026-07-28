import pytest


def test_verify_token_gitlab(patched_config_gitlab, x_gitlab_token, expected_token_gitlab, caplog):
    from utilities.auth import verify_token
    verify_token(x_gitlab_token, expected_token_gitlab)

    assert 'Webhook token verified successfully.' in caplog.text


def test_verify_token_invalid_token_gitlab(patched_config_gitlab, x_gitlab_token, invalid_token_gitlab):
    from utilities.auth import verify_token
    from utilities.exceptions import InvalidTokenException

    with pytest.raises(InvalidTokenException):
        verify_token(x_gitlab_token, invalid_token_gitlab)


def test_verify_token_missing_token_gitlab(patched_config_gitlab, expected_token_gitlab):
    from utilities.auth import verify_token
    from utilities.exceptions import MissingTokenException

    with pytest.raises(MissingTokenException):
        verify_token('', expected_token_gitlab)


def test_webhook_authenticator_success_gitlab(patched_config_gitlab, webhook_event_gitlab, caplog):
    from utilities.auth import webhook_authenticator
    webhook_authenticator(webhook_event_gitlab)
    assert 'Webhook token verified successfully.' in caplog.text


def test_webhook_authenticator_success_github(patched_config_github, webhook_event_github, caplog):
    from utilities.auth import webhook_authenticator
    webhook_authenticator(webhook_event_github)
    assert 'Webhook signature verified successfully.' in caplog.text


def test_webhook_authenticator_wrong_vcs_provider(patched_config_github, webhook_event_github, caplog):
    patched_config_github.setattr("utilities.auth.config.vcs_provider",
                                  "bitbucket")
    from utilities.auth import webhook_authenticator
    from utilities.exceptions import HTTPException

    with pytest.raises(HTTPException):
        webhook_authenticator(webhook_event_github)


def test_verify_signature_success_github(webhook_event_github, expected_token_github, caplog):
    from utilities.auth import verify_signature
    verify_signature(webhook_event_github, expected_token_github)
    assert 'Webhook signature verified successfully.' in caplog.text


def test_verify_signature_invalid_token_github(webhook_event_github, invalid_token_github):
    from utilities.auth import verify_signature
    from utilities.exceptions import HTTPException

    with pytest.raises(HTTPException):
        verify_signature(webhook_event_github, invalid_token_github)


def test_verify_signature_missing_signature_header_github(webhook_event_github, expected_token_github):
    from utilities.auth import verify_signature
    from utilities.exceptions import HTTPException

    with pytest.raises(HTTPException):
        verify_signature({}, expected_token_github)


def test_is_github_issue_comment_success(webhook_event_github):
    from utilities.auth import is_github_issue_comment
    result = is_github_issue_comment(webhook_event_github)
    assert result == True


def test_is_github_issue_comment_failure(webhook_event_not_issue_github):
    from utilities.auth import is_github_issue_comment
    from utilities.exceptions import MissingCommentContextException

    with pytest.raises(MissingCommentContextException):
        is_github_issue_comment(webhook_event_not_issue_github)


def test_is_github_issue_action_is_not_created(webhook_event_action_is_not_created_github):
    from utilities.auth import is_github_issue_comment
    from utilities.exceptions import MissingCommentContextException

    with pytest.raises(MissingCommentContextException):
        is_github_issue_comment(webhook_event_action_is_not_created_github)
