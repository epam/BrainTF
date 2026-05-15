import pytest


def test_process_vcs_webhook_payload_github(patched_config_github, webhook_event_github,
                                            expected_webhook_event_metadata_github, monkeypatch, caplog):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import process_vcs_webhook_payload
    result = process_vcs_webhook_payload(webhook_event_github)
    assert 'Processing VCS webhook payload...' in caplog.text
    assert isinstance(result, dict)
    assert webhook_event_github.get('metadata')
    assert result.get('metadata') == expected_webhook_event_metadata_github


def test_process_vcs_webhook_payload_gitlab(patched_config_gitlab, webhook_event_gitlab,
                                            expected_webhook_event_metadata_gitlab, caplog):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import process_vcs_webhook_payload
    result = process_vcs_webhook_payload(webhook_event_gitlab)
    assert 'Processing VCS webhook payload...' in caplog.text
    assert isinstance(result, dict)
    assert result.get('metadata')
    assert webhook_event_gitlab.get('metadata')
    assert result.get('metadata') == expected_webhook_event_metadata_gitlab


def test_process_vcs_webhook_payload_wrong_vcs(patched_config_wrong_vcs, webhook_event_github,
                                               expected_webhook_event_metadata_github, monkeypatch):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import process_vcs_webhook_payload

    with pytest.raises(ValueError):
        process_vcs_webhook_payload(webhook_event_github)


def test_lambda_handler_http_status_codes(patched_environment):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import HTTP_SUCCESS, HTTP_BAD_REQUEST, HTTP_FORBIDDEN
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
