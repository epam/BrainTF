def test_process_vcs_webhook_payload_github(patched_config_github, webhook_event_github,
                                            expected_webhook_event_metadata_github, monkeypatch):
    monkeypatch.setattr("ai_handler_comment_lambda.ai_handler_comment_lambda.get_last_commit_sha_github",
                        lambda x, y: "1234")
    from ai_handler_comment_lambda.ai_handler_comment_lambda import process_vcs_webhook_payload
    result = process_vcs_webhook_payload(webhook_event_github)
    assert isinstance(result, dict)
    assert webhook_event_github.get('metadata')
    assert result.get('metadata') == expected_webhook_event_metadata_github


def test_process_vcs_webhook_payload_gitlab(patched_config_gitlab, webhook_event_gitlab,
                                     expected_webhook_event_metadata_gitlab):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import process_vcs_webhook_payload
    result = process_vcs_webhook_payload(webhook_event_gitlab)
    assert isinstance(result, dict)
    assert result.get('metadata')
    assert webhook_event_gitlab.get('metadata')
    assert result.get('metadata') == expected_webhook_event_metadata_gitlab


def test_lambda_handler_http_status_codes(patched_environment):
    from ai_handler_comment_lambda.ai_handler_comment_lambda import HTTP_SUCCESS, HTTP_BAD_REQUEST, HTTP_FORBIDDEN
    assert HTTP_SUCCESS == 200
    assert HTTP_BAD_REQUEST == 400
    assert HTTP_FORBIDDEN == 403
