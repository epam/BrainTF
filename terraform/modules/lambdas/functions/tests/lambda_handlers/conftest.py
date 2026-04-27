from tests.utilities.auth.conftest import *
import pytest

from tests.data.events import WEBHOOK_EVENT_METADATA_GITHUB, WEBHOOK_EVENT_METADATA_GITLAB


@pytest.fixture
def expected_webhook_event_metadata_github():
    return WEBHOOK_EVENT_METADATA_GITHUB


@pytest.fixture
def expected_webhook_event_metadata_gitlab():
    return WEBHOOK_EVENT_METADATA_GITLAB
