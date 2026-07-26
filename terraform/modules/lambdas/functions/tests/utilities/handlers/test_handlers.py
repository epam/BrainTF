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
    assert 'Prepared artifact file list: `..`.' in caplog.text


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
    assert 'Prepared artifact file list: `demo/broken/main.tf`\n\n`demo/broken/validate.tf`.' in caplog.text


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
    assert 'Approving all corrected files...' in caplog.text


def test_build_approval_commit_message_uses_files_only(patched_environment):
    from utilities.handlers import build_approval_commit_message

    result = build_approval_commit_message(
        ['demo/broken/main.tf', 'demo/broken/validate.tf']
    )

    assert result == 'AI-bot fixed issues in files demo/broken/main.tf,\ndemo/broken/validate.tf'
    assert max(len(line) for line in result.splitlines()) <= 72


def test_build_approval_commit_message_uses_file_for_single_item(patched_environment):
    from utilities.handlers import build_approval_commit_message

    result = build_approval_commit_message(['demo/broken/main.tf'])

    assert result == 'AI-bot fixed issues in the file demo/broken/main.tf'
    assert max(len(line) for line in result.splitlines()) <= 72


def test_build_approval_commit_message_wraps_and_truncates_long_file_list(patched_environment):
    from utilities.handlers import build_approval_commit_message

    approved_files = [f"demo/file-{index:011}.tf" for index in range(38)]

    result = build_approval_commit_message(approved_files)

    assert len(result) <= 1000
    assert '\n' in result
    assert max(len(line) for line in result.splitlines()) <= 72
    assert result.endswith('and others')
    assert result.startswith('AI-bot fixed issues in files')


def test_render_approval_commit_message_wraps_and_appends_suffix(patched_environment):
    from utilities.handlers import render_approval_commit_message

    approved_files = [f"demo/file-{index:011}.tf" for index in range(3)]

    result = render_approval_commit_message(approved_files, include_suffix=True)

    assert '\n' in result
    assert max(len(line) for line in result.splitlines()) <= 72
    assert result.endswith('and others')
    assert result.startswith('AI-bot fixed issues in files')


def test_handle_prompt_command_persists_metadata_when_missing(monkeypatch):
    from utilities import handlers

    event = {}

    monkeypatch.setattr("utilities.handlers.get_context_memory_window", lambda event: [])
    monkeypatch.setattr(
        "utilities.handlers.generate_response_ai",
        lambda messages: {
            "message": "done",
            "tokens": {
                "prompt_tokens": 1,
                "completion_tokens": 1,
                "total_tokens": 2,
            },
        },
    )
    monkeypatch.setattr("utilities.handlers.post_comment", lambda event, message: {})
    monkeypatch.setattr("utilities.handlers.handle_ai_response_message", lambda event: None)
    monkeypatch.setattr("utilities.handlers.create_context_memory_window", lambda event: None)

    handlers.handle_prompt_command(event, ["fix", "this"])

    assert "metadata" in event
    assert event["metadata"]["prompt"] == "fix this"
    assert event["metadata"]["ai_response"] == "done"


def test_handle_approve_command_all_uses_generated_commit_message(patched_environment,
                                                                  webhook_event_command_bot_approve_all_context_github,
                                                                  monkeypatch):
    from utilities import handlers

    commit_calls = []
    delete_calls = []

    monkeypatch.setattr("utilities.handlers.add_award_to_note", lambda event, award: {})
    monkeypatch.setattr(
        "utilities.handlers.get_all_files_from_s3_directory",
        lambda bucket_name, path_to_files: [('demo/broken/main.tf', 'content')]
    )
    monkeypatch.setattr("utilities.handlers.check_files_exist_in_repo", lambda event, files: True)
    monkeypatch.setattr(
        "utilities.handlers.commit_files_to_branch",
        lambda event, files, commit_message: commit_calls.append((files, commit_message))
    )
    monkeypatch.setattr(
        "utilities.handlers.delete_files_from_s3",
        lambda bucket_name, path_to_files: delete_calls.append((bucket_name, path_to_files))
    )

    handlers.handle_approve_command(webhook_event_command_bot_approve_all_context_github, ['all'])

    assert commit_calls == [
        (
            [('demo/broken/main.tf', 'content')],
            'AI-bot fixed issues in the file demo/broken/main.tf'
        )
    ]
    assert len(delete_calls) == 1


def test_handle_approve_command_all_stops_when_repo_check_fails(patched_environment,
                                                                webhook_event_command_bot_approve_all_context_github,
                                                                monkeypatch):
    from utilities import handlers

    commit_calls = []
    comments = []

    monkeypatch.setattr("utilities.handlers.add_award_to_note", lambda event, award: {})
    monkeypatch.setattr(
        "utilities.handlers.get_all_files_from_s3_directory",
        lambda bucket_name, path_to_files: [('demo/broken/main.tf', 'content')]
    )
    monkeypatch.setattr("utilities.handlers.check_files_exist_in_repo", lambda event, files: False)
    monkeypatch.setattr(
        "utilities.handlers.commit_files_to_branch",
        lambda event, files, commit_message: commit_calls.append((files, commit_message))
    )
    monkeypatch.setattr("utilities.handlers.post_comment", lambda event, body: comments.append(body))

    handlers.handle_approve_command(webhook_event_command_bot_approve_all_context_github, ['all'])

    assert commit_calls == []
    assert comments == ['Some approved files do not exist in the repository']


def test_handle_approve_command_specific_checks_repo_before_commit(patched_environment,
                                                                   webhook_event_command_bot_approve_all_context_github,
                                                                   monkeypatch):
    from utilities import handlers

    commit_calls = []
    comments = []

    monkeypatch.setattr("utilities.handlers.add_award_to_note", lambda event, award: {})
    monkeypatch.setattr(
        "utilities.handlers.get_file_names_from_s3_directory",
        lambda bucket_name, path_to_files: ['demo/broken/main.tf']
    )
    monkeypatch.setattr("utilities.handlers.check_files_exist_in_repo", lambda event, files: False)
    monkeypatch.setattr(
        "utilities.handlers.get_particular_files_from_s3_directory",
        lambda bucket_name, path_to_files, file_names: [('demo/broken/main.tf', 'content')]
    )
    monkeypatch.setattr(
        "utilities.handlers.commit_files_to_branch",
        lambda event, files, commit_message: commit_calls.append((files, commit_message))
    )
    monkeypatch.setattr("utilities.handlers.post_comment", lambda event, body: comments.append(body))

    handlers.handle_approve_command(webhook_event_command_bot_approve_all_context_github, ['demo/broken/main.tf'])

    assert commit_calls == []
    assert comments == ['Some selected files do not exist in the repository.']


def test_handle_approve_command_specific_deletes_artifacts_after_commit(patched_environment,
                                                                       webhook_event_command_bot_approve_all_context_github,
                                                                       monkeypatch):
    from utilities import handlers

    commit_calls = []
    delete_calls = []

    monkeypatch.setattr("utilities.handlers.add_award_to_note", lambda event, award: {})
    monkeypatch.setattr(
        "utilities.handlers.get_file_names_from_s3_directory",
        lambda bucket_name, path_to_files: ['demo/broken/main.tf', 'demo/broken/validate.tf']
    )
    monkeypatch.setattr("utilities.handlers.check_files_exist_in_repo", lambda event, files: True)
    monkeypatch.setattr(
        "utilities.handlers.get_particular_files_from_s3_directory",
        lambda bucket_name, path_to_files, file_names: [('demo/broken/main.tf', 'content')]
    )
    monkeypatch.setattr(
        "utilities.handlers.commit_files_to_branch",
        lambda event, files, commit_message: commit_calls.append((files, commit_message))
    )
    monkeypatch.setattr(
        "utilities.handlers.delete_files_from_s3",
        lambda bucket_name, path_to_files: delete_calls.append((bucket_name, path_to_files))
    )

    handlers.handle_approve_command(webhook_event_command_bot_approve_all_context_github, ['demo/broken/main.tf'])

    assert commit_calls == [
        (
            [('demo/broken/main.tf', 'content')],
            'AI-bot fixed issues in the file demo/broken/main.tf'
        )
    ]
    assert delete_calls == [('artifacts_bucket', 'artifacts/32/')]
