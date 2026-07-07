import pytest

from tests.data.logs_s3 import LOG_TEXT_TRIVY


# Constants
MOCK_FILE_CONTENT = {
    'content': '2 issue(s) found:\n\nWarning: terraform "required_version" attribute is required ('
               'terraform_required_version)\n\n  on demo/broken/main.tf line 1:\n   1: terraform {'
               '\n\nReference:https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.14.1/docs'
               '/rules/terraform_required_version.md\n\nWarning: Missing version constraint for provider "aws" in '
               '`required_providers` (terraform_required_providers)\n\n  on demo/broken/main.tf line 6:\n   6: '
               'provider "aws" {\n\nReference: '
               'https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.14.1/docs/rules'
               '/terraform_required_providers.md\n\nWorking Directory: demo/broken\n\n',
    'metadata': {'base_repo_name': 'some-org/BrainTF', 'base_repo_owner': 'some-org',
                 'commit_sha': 'a65f6658342bb3b91afc1d2588f0744b320c8366',
                 'head_branch_name': 'FEAT-branch',
                 'pull_num': '22', 'tool_name': 'TFLint'}
}

MOCK_TF_FILES = [
    ('main.tf', 'some content'),
    ('validate.tf', 'variable "aws_region" { default = "eu-central-1" }\n')
]


# Helper / Mock Functions
def mock_s3_file_content(bucket, key):
    """Mock function for fetching file content with metadata from S3."""
    return MOCK_FILE_CONTENT


def mock_tf_files_list(event, paths_to_files):
    """Mock function for fetching Terraform files from a list of paths."""
    return MOCK_TF_FILES


def mock_ai_response(messages: list, retries: int = 3) -> dict:
    """Mock function for simulating AI response generation."""
    return {
        "message": "some message",
        "tokens": {
            "prompt_tokens": 3,
            "completion_tokens": 2,
            "total_tokens": 5
        }
    }


MOCK_TRIVY_FILE_CONTENT = {
    "content": LOG_TEXT_TRIVY,
    "metadata": {
        "base_repo_name": "some-org/BrainTF",
        "base_repo_owner": "some-org",
        "commit_sha": "a65f6658342bb3b91afc1d2588f0744b320c8366",
        "head_branch_name": "FEAT-branch",
        "pull_num": "22",
        "tool_name": "Trivy",
    },
}


def setup_monkeypatches(monkeypatch):
    """Common setup for monkeypatching dependencies in tests."""
    monkeypatch.setattr("utilities.aws.get_file_content_with_metadata_from_s3", mock_s3_file_content)
    monkeypatch.setattr("utilities.vcs.get_all_tf_files_from_paths_list", mock_tf_files_list)
    monkeypatch.setattr("utilities.ai.chat_completions.generate_response_ai", mock_ai_response)
    monkeypatch.setattr("utilities.vcs.post_comment", lambda x, y: {})
    monkeypatch.setattr("utilities.ai.context.create_context_memory_window", lambda event: None)


def setup_monkeypatches_trivy(monkeypatch):
    monkeypatch.setattr("utilities.aws.get_file_content_with_metadata_from_s3", lambda bucket, key: MOCK_TRIVY_FILE_CONTENT)
    monkeypatch.setattr("utilities.vcs.get_all_tf_files_from_paths_list", mock_tf_files_list)
    monkeypatch.setattr("utilities.ai.chat_completions.generate_response_ai", mock_ai_response)
    monkeypatch.setattr("utilities.vcs.post_comment", lambda x, y: {})
    monkeypatch.setattr("utilities.ai.context.create_context_memory_window", lambda event: None)


# Tests
def test_lambda_invokes_ai_handler_successfully(patched_config_github, monkeypatch, s3_bucket_event_tflint, caplog):
    setup_monkeypatches(monkeypatch)
    from ai_handler_tf_errors_lambda.ai_handler_tf_errors_lambda import lambda_handler

    lambda_handler(s3_bucket_event_tflint, {})
    assert 'Successfully invoked' in caplog.text


def test_lambda_invokes_ai_handler_successfully_for_trivy(patched_config_github, monkeypatch, s3_bucket_event_trivy, caplog):
    setup_monkeypatches_trivy(monkeypatch)
    from ai_handler_tf_errors_lambda.ai_handler_tf_errors_lambda import lambda_handler

    lambda_handler(s3_bucket_event_trivy, {})
    assert 'Successfully invoked' in caplog.text


def test_lambda_raises_exception_on_invalid_event(patched_config_github, monkeypatch, s3_bucket_event_tflint, caplog):
    setup_monkeypatches(monkeypatch)
    from ai_handler_tf_errors_lambda.ai_handler_tf_errors_lambda import lambda_handler

    with pytest.raises(Exception):
        lambda_handler({}, {})


def test_process_s3_event_with_github_metadata(patched_config_github, monkeypatch, s3_bucket_event_tflint):
    setup_monkeypatches(monkeypatch)
    from ai_handler_tf_errors_lambda.ai_handler_tf_errors_lambda import process_s3_event

    result = process_s3_event(s3_bucket_event_tflint)

    assert 'metadata' in result
    assert result["metadata"]["repo_id_or_name"] == 'some-org/BrainTF'
    assert result["metadata"]["source_branch"] == 'FEAT-branch'
    assert "terraform_required_version" in result["metadata"]["log_file_content"]
    assert result["metadata"]["merge_or_pull_req_id"] == 22


def test_process_s3_event_raises_missing_records(patched_config_gitlab):
    from ai_handler_tf_errors_lambda.ai_handler_tf_errors_lambda import process_s3_event

    with pytest.raises(ValueError, match="S3 event is missing Records entries."):
        process_s3_event({})
