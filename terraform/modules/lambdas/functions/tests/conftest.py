import pytest

from data.events import WEBHOOK_EVENT_GITHUB, WEBHOOK_EVENT_METADATA_GITHUB


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
