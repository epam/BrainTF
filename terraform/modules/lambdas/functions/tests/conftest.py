import boto3
import pytest

from data.events import WEBHOOK_EVENT_GITHUB, WEBHOOK_EVENT_METADATA_GITHUB


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

    boto3.setup_default_session(
        aws_access_key_id="testing",
        aws_secret_access_key="testing",
        aws_session_token="testing",
        region_name="eu-central-1",
    )
    yield
    boto3.DEFAULT_SESSION = None


@pytest.fixture
def patched_config_gitlab(patched_environment, expected_token_gitlab):
    from config import config

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
    from config import config

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
    from config import config

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


@pytest.fixture
def webhook_event_dummy():
    return {}


@pytest.fixture
def webhook_event_not_issue_github():
    headers = WEBHOOK_EVENT_GITHUB.get('headers', {})
    headers.update({'x-github-event': 'else'})
    WEBHOOK_EVENT_GITHUB.update({'headers': headers})
    return WEBHOOK_EVENT_GITHUB


@pytest.fixture
def webhook_event_command_help_github():
    WEBHOOK_EVENT_METADATA_GITHUB.update({'comment_text': 'help'})
    WEBHOOK_EVENT_GITHUB.update({'metadata': WEBHOOK_EVENT_METADATA_GITHUB})
    return WEBHOOK_EVENT_GITHUB


@pytest.fixture
def webhook_event_command_help_rest_context_github():
    WEBHOOK_EVENT_METADATA_GITHUB.update({'comment_text': 'help to'})
    WEBHOOK_EVENT_GITHUB.update({'metadata': WEBHOOK_EVENT_METADATA_GITHUB})
    return WEBHOOK_EVENT_GITHUB


@pytest.fixture
def webhook_event_command_bot_list_github():
    WEBHOOK_EVENT_METADATA_GITHUB.update({'comment_text': 'bot list'})
    WEBHOOK_EVENT_GITHUB.update({'metadata': WEBHOOK_EVENT_METADATA_GITHUB})
    return WEBHOOK_EVENT_GITHUB


@pytest.fixture
def webhook_event_command_bot_approve_context_missing_all_github():
    WEBHOOK_EVENT_METADATA_GITHUB.update({'comment_text': 'bot approve'})
    WEBHOOK_EVENT_GITHUB.update({'metadata': WEBHOOK_EVENT_METADATA_GITHUB})
    return WEBHOOK_EVENT_GITHUB


@pytest.fixture
def webhook_event_command_bot_approve_all_context_github():
    WEBHOOK_EVENT_METADATA_GITHUB.update({'comment_text': 'bot approve all'})
    WEBHOOK_EVENT_GITHUB.update({'metadata': WEBHOOK_EVENT_METADATA_GITHUB})
    return WEBHOOK_EVENT_GITHUB
