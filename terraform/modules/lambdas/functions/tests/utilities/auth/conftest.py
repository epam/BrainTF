import hashlib
import hmac
import json
from copy import deepcopy

import pytest
from tests.data.events import WEBHOOK_EVENT_GITLAB

GITHUB_SIGNATURE_HEADER = "x-hub-signature-256"
GITLAB_TOKEN_HEADER = "x-gitlab-token"

EXPECTED_TOKEN_GITLAB = "SoMeSeCrEtToKeN_737"
EXPECTED_TOKEN_GITHUB = "SoMeSeCrEtToKeN_737_777"
INVALID_TOKEN_GITLAB = "SoMeSeCrEtToKeN_737_727"
INVALID_TOKEN_GITHUB = "SoMeSeCrEtToKeN_737_727"


def generate_github_signature(secret: str, payload: str | bytes) -> str:
    payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload
    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
    return f"sha256={signature}"


def _clone_github_event() -> dict:
    from tests.data.events import WEBHOOK_EVENT_GITHUB
    return deepcopy(WEBHOOK_EVENT_GITHUB)


def _set_github_signature_header(event: dict, secret: str) -> dict:
    payload_str: str = event.get("body", "")
    headers = event.get("headers", {})
    headers[GITHUB_SIGNATURE_HEADER] = generate_github_signature(secret, payload_str)
    event["headers"] = headers
    return event


@pytest.fixture
def webhook_event_gitlab():
    return deepcopy(WEBHOOK_EVENT_GITLAB)


@pytest.fixture
def webhook_event_github(expected_token_github):
    event = _clone_github_event()
    return _set_github_signature_header(event, expected_token_github)


@pytest.fixture
def webhook_event_action_is_not_created_github(expected_token_github):
    event = _clone_github_event()
    webhook_payload = json.loads(event.get("body", "{}"))
    webhook_payload["action"] = "else"
    event["body"] = json.dumps(webhook_payload)
    return _set_github_signature_header(event, expected_token_github)


@pytest.fixture
def expected_token_gitlab():
    return EXPECTED_TOKEN_GITLAB


@pytest.fixture
def expected_token_github():
    return EXPECTED_TOKEN_GITHUB


@pytest.fixture
def invalid_token_gitlab():
    return INVALID_TOKEN_GITLAB


@pytest.fixture
def invalid_token_github():
    return INVALID_TOKEN_GITHUB


@pytest.fixture
def x_gitlab_token():
    event = deepcopy(WEBHOOK_EVENT_GITLAB)
    return event.get("headers", {}).get(GITLAB_TOKEN_HEADER)


@pytest.fixture
def webhook_event_invalid_token_gitlab(invalid_token_gitlab):
    event = deepcopy(WEBHOOK_EVENT_GITLAB)
    headers = event.get("headers", {})
    headers[GITLAB_TOKEN_HEADER] = invalid_token_gitlab
    event["headers"] = headers
    return event
