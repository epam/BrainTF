import hashlib
import hmac
import json
from copy import deepcopy

import boto3
import pytest
from moto import mock_aws

from tests.data.events import (WEBHOOK_EVENT_GITHUB, WEBHOOK_EVENT_GITLAB,
                               WEBHOOK_EVENT_METADATA_GITHUB)
from tests.data.expected import EXPECTED_TOKEN_GITHUB, EXPECTED_TOKEN_GITLAB

GITHUB_SIGNATURE_HEADER = "x-hub-signature-256"
GITLAB_TOKEN_HEADER = "x-gitlab-token"

INVALID_TOKEN_GITLAB = "SoMeSeCrEtToKeN_737_727"
INVALID_TOKEN_GITHUB = "SoMeSeCrEtToKeN_737_727"


def generate_github_signature(secret: str, payload: str | bytes) -> str:
    payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={signature}"


def _set_github_signature_header(event: dict, secret: str) -> dict:
    headers = event.get("headers", {})
    headers[GITHUB_SIGNATURE_HEADER] = generate_github_signature(secret, event.get("body", ""))
    event["headers"] = headers
    return event


@pytest.fixture
def patched_environment(monkeypatch):
    # Set environment variables for consistency
    monkeypatch.setenv("VCS_PROVIDER", "gitlab")
    monkeypatch.setenv("VCS_TOKEN_NAME", "x-gitlab-token")
    monkeypatch.setenv("VCS_API_ENDPOINT", "https://gitlab.com")
    monkeypatch.setenv("WEBHOOK_SECRET_NAME", "webhook_secret")
    monkeypatch.setenv("ARTIFACTS_BUCKET", "artifacts_bucket")
    monkeypatch.setenv("ARTIFACTS_PATH", "artifacts")
    monkeypatch.setenv("AI_API_TOKEN_NAME", "token")
    monkeypatch.setenv("LLM_MODEL", "gpt-3.5-turbo")
    monkeypatch.setenv("AI_API_BASE_URL", "https://api.testopenai.com/v1")
    monkeypatch.setenv("DYNAMODB_TABLE_NAME", "table_name")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("RAG_ENABLED", "true")
    monkeypatch.setenv("TTL_DELTA_DAYS", "30")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-central-1")

    return monkeypatch


@pytest.fixture(autouse=True)
def aws_env_and_session(monkeypatch):
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-central-1")
    monkeypatch.setenv("AWS_REGION", "eu-central-1")
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")  # important in CI

    boto3.setup_default_session()
    yield
    boto3.DEFAULT_SESSION = None


@pytest.fixture
def ssm_setup():
    """Fixture to set up a mock SSM environment."""
    with mock_aws():
        client = boto3.client("ssm")
        # Create parameters in the mock SSM
        client.put_parameter(
            Name="test-parameter",
            Value="test-value",
            Type="String",
        )

        client.put_parameter(
            Name="x-gitlab-token",
            Value=EXPECTED_TOKEN_GITLAB,
            Type="String",
        )
        client.put_parameter(
            Name="x-github-token",
            Value=EXPECTED_TOKEN_GITHUB,
            Type="String",
        )
        client.put_parameter(
            Name="webhook_secret",
            Value=EXPECTED_TOKEN_GITLAB,
            Type="String",
        )
        client.put_parameter(
            Name="token",
            Value="token",
            Type="String",
        )
        yield


@pytest.fixture
def expected_token_gitlab():
    return EXPECTED_TOKEN_GITLAB


@pytest.fixture
def expected_token_github():
    return EXPECTED_TOKEN_GITHUB


@pytest.fixture
def patched_config_gitlab(patched_environment, ssm_setup, expected_token_gitlab):
    from config import config

    boto3.client("ssm").put_parameter(
        Name="webhook_secret",
        Value=expected_token_gitlab,
        Type="String",
        Overwrite=True,
    )

    patched_environment.setattr(config, "vcs_provider", "gitlab")
    patched_environment.setattr(config, "vcs_token_name", "x-gitlab-token")
    return patched_environment


@pytest.fixture
def patched_config_github(patched_environment, ssm_setup, expected_token_github):
    from config import config

    boto3.client("ssm").put_parameter(
        Name="webhook_secret",
        Value=expected_token_github,
        Type="String",
        Overwrite=True,
    )

    patched_environment.setattr(config, "vcs_provider", "github")
    patched_environment.setattr(config, "vcs_token_name", "x-github-token")
    return patched_environment


@pytest.fixture
def patched_config_wrong_vcs(patched_environment, ssm_setup, expected_token_github):
    from config import config

    boto3.client("ssm").put_parameter(
        Name="webhook_secret",
        Value=expected_token_github,
        Type="String",
        Overwrite=True,
    )

    patched_environment.setattr(config, "vcs_provider", "bitbucket")
    patched_environment.setattr(config, "vcs_token_name", "x-github-token")
    return patched_environment


@pytest.fixture
def invalid_token_gitlab():
    return INVALID_TOKEN_GITLAB


@pytest.fixture
def invalid_token_github():
    return INVALID_TOKEN_GITHUB


@pytest.fixture
def webhook_event_gitlab():
    return deepcopy(WEBHOOK_EVENT_GITLAB)


@pytest.fixture
def webhook_event_invalid_token_gitlab(invalid_token_gitlab):
    event = deepcopy(WEBHOOK_EVENT_GITLAB)
    headers = event.get("headers", {})
    headers[GITLAB_TOKEN_HEADER] = invalid_token_gitlab
    event["headers"] = headers
    return event


@pytest.fixture
def x_gitlab_token():
    event = deepcopy(WEBHOOK_EVENT_GITLAB)
    return event.get("headers", {}).get(GITLAB_TOKEN_HEADER)


@pytest.fixture
def webhook_event_github(expected_token_github):
    event = deepcopy(WEBHOOK_EVENT_GITHUB)
    return _set_github_signature_header(event, expected_token_github)


@pytest.fixture
def webhook_event_action_is_not_created_github(expected_token_github):
    event = deepcopy(WEBHOOK_EVENT_GITHUB)
    webhook_payload = json.loads(event.get("body", "{}"))
    webhook_payload["action"] = "else"
    event["body"] = json.dumps(webhook_payload)
    return _set_github_signature_header(event, expected_token_github)


@pytest.fixture
def webhook_event_dummy():
    return {}


@pytest.fixture
def webhook_event_not_issue_github():
    event = deepcopy(WEBHOOK_EVENT_GITHUB)
    headers = event.get('headers', {})
    headers.update({'x-github-event': 'else'})
    event.update({'headers': headers})
    return event


@pytest.fixture
def webhook_event_command_help_github():
    event = deepcopy(WEBHOOK_EVENT_GITHUB)
    metadata = deepcopy(WEBHOOK_EVENT_METADATA_GITHUB)
    metadata.update({'comment_text': 'help'})
    event.update({'metadata': metadata})
    return event


@pytest.fixture
def webhook_event_command_help_rest_context_github():
    event = deepcopy(WEBHOOK_EVENT_GITHUB)
    metadata = deepcopy(WEBHOOK_EVENT_METADATA_GITHUB)
    metadata.update({'comment_text': 'help to'})
    event.update({'metadata': metadata})
    return event


@pytest.fixture
def webhook_event_command_bot_list_github():
    event = deepcopy(WEBHOOK_EVENT_GITHUB)
    metadata = deepcopy(WEBHOOK_EVENT_METADATA_GITHUB)
    metadata.update({'comment_text': 'bot list'})
    event.update({'metadata': metadata})
    return event


@pytest.fixture
def webhook_event_command_bot_approve_context_missing_all_github():
    event = deepcopy(WEBHOOK_EVENT_GITHUB)
    metadata = deepcopy(WEBHOOK_EVENT_METADATA_GITHUB)
    metadata.update({'comment_text': 'bot approve'})
    event.update({'metadata': metadata})
    return event


@pytest.fixture
def webhook_event_command_bot_approve_all_context_github():
    event = deepcopy(WEBHOOK_EVENT_GITHUB)
    metadata = deepcopy(WEBHOOK_EVENT_METADATA_GITHUB)
    metadata.update({'comment_text': 'bot approve all'})
    event.update({'metadata': metadata})
    return event
