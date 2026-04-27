import hashlib
import hmac
import json
from copy import deepcopy

import pytest

from tests.data.events import WEBHOOK_EVENT_GITLAB


def generate_x_hub_signature_256(secret, payload):
    # Ensure the payload is in bytes
    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    # Compute the HMAC-SHA256 signature
    signature = hmac.new(secret.encode('utf-8'), payload, hashlib.sha256).hexdigest()
    # Return the formatted signature
    return f"sha256={signature}"


@pytest.fixture
def webhook_event_gitlab():
    event = WEBHOOK_EVENT_GITLAB.copy()
    return event


@pytest.fixture
def webhook_event_github(expected_token_github):
    from tests.data.events import WEBHOOK_EVENT_GITHUB
    event = WEBHOOK_EVENT_GITHUB.copy()
    payload: str = event.get('body')
    generated_signature: str = generate_x_hub_signature_256(expected_token_github, payload)

    headers = event.get('headers', {})
    headers.update({'x-hub-signature-256': generated_signature})
    event.update({'headers': headers})
    return event


@pytest.fixture
def webhook_event_action_is_not_created_github(expected_token_github):
    from tests.data.events import WEBHOOK_EVENT_GITHUB
    event = WEBHOOK_EVENT_GITHUB.copy()
    webhook_payload = json.loads(event.get('body', {}))
    webhook_payload.update({'action': 'else'})
    event.update({'body': json.dumps(webhook_payload)})
    payload: str = event.get('body')
    generated_signature: str = generate_x_hub_signature_256(expected_token_github, payload)

    headers = event.get('headers', {})
    headers.update({'x-hub-signature-256': generated_signature})
    event.update({'headers': headers})
    return event


@pytest.fixture
def expected_token_gitlab():
    return 'SoMeSeCrEtToKeN_737'


@pytest.fixture
def expected_token_github():
    return 'SoMeSeCrEtToKeN_737_777'


@pytest.fixture
def invalid_token_gitlab():
    return 'SoMeSeCrEtToKeN_737_727'


@pytest.fixture
def invalid_token_github():
    return 'SoMeSeCrEtToKeN_737_727'


@pytest.fixture
def x_gitlab_token():
    event = deepcopy(WEBHOOK_EVENT_GITLAB)
    token = event.get('headers', {}).get('x-gitlab-token')
    return token


@pytest.fixture
def webhook_event_invalid_token_gitlab(invalid_token_gitlab):
    event = deepcopy(WEBHOOK_EVENT_GITLAB)
    headers = event.get('headers', {})
    headers.update({'x-gitlab-token': invalid_token_gitlab})
    event.update({'headers': headers})
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
    monkeypatch.setenv("AI_API_ENDPOINT", "https://ai.example.com")
    monkeypatch.setenv("DYNAMODB_TABLE_NAME", "table_name")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("RAG_ENABLED", "true")
    monkeypatch.setenv("TTL_DELTA_DAYS", "30")

    return monkeypatch


@pytest.fixture
def patched_config_gitlab(patched_environment, expected_token_gitlab):
    from utilities.auth import config

    # Patch the cached_property `webhook_secret`
    new_object = type(config)
    patched_environment.setattr(
        new_object,
        "webhook_secret",
        property(lambda self: expected_token_gitlab),
    )
    return patched_environment


@pytest.fixture
def patched_config_github(patched_environment, expected_token_github):
    from utilities.auth import config

    # Patch the cached_property `webhook_secret`
    new_object = type(config)

    patched_environment.setattr(
        new_object,
        "webhook_secret",
        property(lambda self: expected_token_github),
    )

    patched_environment.setattr(
        "utilities.auth.config.vcs_provider",
        "github"
    )
    return patched_environment


@pytest.fixture
def patched_config_wrong_vcs(patched_environment, expected_token_github):
    from utilities.auth import config

    # Patch the cached_property `webhook_secret`
    new_object = type(config)

    patched_environment.setattr(
        new_object,
        "webhook_secret",
        property(lambda self: expected_token_github),
    )

    patched_environment.setattr(
        "utilities.auth.config.vcs_provider",
        "bitbucket"
    )
    return patched_environment
