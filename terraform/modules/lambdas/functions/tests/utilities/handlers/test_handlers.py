def test_handle_help_command(patched_environment, webhook_event_dummy, caplog, monkeypatch):
    from utilities import handlers
    monkeypatch.setattr("utilities.handlers.post_help_message", lambda x: {})
    handlers.handle_help_command(webhook_event_dummy)
    assert 'Processing help command...' in caplog.text


def test_handle_comment_commands_dummy_webhook(patched_environment, webhook_event_dummy, caplog, monkeypatch):
    from utilities import handlers
    monkeypatch.setattr("utilities.handlers.post_comment", lambda x, y: {})
    handlers.handle_comment_commands(webhook_event_dummy)
    assert 'No actionable context found in the comment.' in caplog.text


def test_handle_comment_commands_webhook_help_context(patched_environment, webhook_event_command_help_github, caplog, monkeypatch):
    from utilities import handlers
    monkeypatch.setattr("utilities.handlers.post_help_message", lambda x: {})

    def mock_add_award_to_note(note_id, award_name):
        return f"Mocked award '{award_name}' added to note {note_id}"

    monkeypatch.setattr("utilities.handlers.add_award_to_note", mock_add_award_to_note)
    handlers.handle_comment_commands(webhook_event_command_help_github)
    assert 'Help context found in the comment.' in caplog.text


def test_handle_comment_commands_webhook_help_with_rest_context(patched_environment, webhook_event_command_help_rest_context_github, caplog,
                                                                monkeypatch):
    from utilities import handlers
    monkeypatch.setattr("utilities.handlers.post_comment", lambda x, y: {})

    def mock_add_award_to_note(note_id, award_name):
        return f"Mocked award '{award_name}' added to note {note_id}"

    monkeypatch.setattr("utilities.handlers.add_award_to_note", mock_add_award_to_note)
    handlers.handle_comment_commands(webhook_event_command_help_rest_context_github)
    assert 'No actionable context found in the comment.' in caplog.text


def test_handle_comment_commands_webhook_bot_list_context(patched_environment, webhook_event_command_bot_list_github, caplog,
                                                          monkeypatch):
    from utilities import handlers
    monkeypatch.setattr("utilities.handlers.post_comment", lambda x, y: {})

    def mock_add_award_to_note(note_id, award_name):
        return f"Mocked award '{award_name}' added to note {note_id}"

    def mock_get_file_names_from_s3_directory(bucket_name: str, path_to_files: str) -> list[str]:
        return []

    monkeypatch.setattr("utilities.handlers.add_award_to_note", mock_add_award_to_note)
    monkeypatch.setattr("utilities.handlers.get_file_names_from_s3_directory", mock_get_file_names_from_s3_directory)
    handlers.handle_comment_commands(webhook_event_command_bot_list_github)
    assert 'Bot context found in the comment.' in caplog.text
    assert 'Processing list command...' in caplog.text
    assert 'Listing rest_comment: `..`' in caplog.text


def test_handle_comment_commands_webhook_bot_list_context_no_files(patched_environment, webhook_event_command_bot_list_github, caplog,
                                                                   monkeypatch):
    from utilities import handlers
    monkeypatch.setattr("utilities.handlers.post_comment", lambda x, y: {})

    def mock_add_award_to_note(note_id, award_name):
        return f"Mocked award '{award_name}' added to note {note_id}"

    def mock_get_file_names_from_s3_directory(bucket_name: str, path_to_files: str) -> list[str]:
        return ['demo/broken/main.tf', 'demo/broken/validate.tf']

    monkeypatch.setattr("utilities.handlers.add_award_to_note", mock_add_award_to_note)
    monkeypatch.setattr("utilities.handlers.get_file_names_from_s3_directory", mock_get_file_names_from_s3_directory)
    handlers.handle_comment_commands(webhook_event_command_bot_list_github)
    assert 'Bot context found in the comment.' in caplog.text
    assert 'Processing list command...' in caplog.text
    assert 'Listing rest_comment: `demo/broken/main.tf`\n\n`demo/broken/validate.tf`' in caplog.text


def test_handle_comment_commands_webhook_bot_approve_context_mising(patched_environment, 
        webhook_event_command_bot_approve_context_missing_all_github, caplog,
        monkeypatch):
    from utilities import handlers
    monkeypatch.setattr("utilities.handlers.post_comment", lambda x, y: {})

    def mock_add_award_to_note(note_id, award_name):
        return f"Mocked award '{award_name}' added to note {note_id}"

    def mock_get_file_names_from_s3_directory(bucket_name: str, path_to_files: str) -> list[str]:
        return []

    monkeypatch.setattr("utilities.handlers.add_award_to_note", mock_add_award_to_note)
    monkeypatch.setattr("utilities.handlers.get_file_names_from_s3_directory", mock_get_file_names_from_s3_directory)
    handlers.handle_comment_commands(webhook_event_command_bot_approve_context_missing_all_github)
    assert 'Bot context found in the comment.' in caplog.text
    assert 'Unknown bot command: approve' in caplog.text


def test_handle_comment_commands_webhook_bot_approve_all_context(patched_environment, 
        webhook_event_command_bot_approve_all_context_github, caplog,
        monkeypatch):
    from utilities import handlers
    monkeypatch.setattr("utilities.handlers.post_comment", lambda x, y: {})

    def mock_add_award_to_note(note_id, award_name):
        return f"Mocked award '{award_name}' added to note {note_id}"

    def mock_get_file_names_from_s3_directory(bucket_name: str, path_to_files: str) -> list[str]:
        return []

    monkeypatch.setattr("utilities.handlers.add_award_to_note", mock_add_award_to_note)
    monkeypatch.setattr("utilities.handlers.get_all_files_from_s3_directory", mock_get_file_names_from_s3_directory)
    handlers.handle_comment_commands(webhook_event_command_bot_approve_all_context_github)
    assert 'Bot context found in the comment.' in caplog.text
    assert 'Approve context found in the comment.' in caplog.text
    assert 'Processing approve command...' in caplog.text
    assert 'Approving all rest_comment...' in caplog.text
