from tests.utilities.auth.conftest import *
from copy import deepcopy

import pytest

from tests.data.events import WEBHOOK_EVENT_METADATA_GITHUB, WEBHOOK_EVENT_METADATA_GITLAB, S3_BUCKET_EVENT_TFLINT


@pytest.fixture
def expected_webhook_event_metadata_github():
    return WEBHOOK_EVENT_METADATA_GITHUB


@pytest.fixture
def expected_webhook_event_metadata_gitlab():
    return WEBHOOK_EVENT_METADATA_GITLAB


@pytest.fixture
def s3_bucket_event_tflint():
    event = deepcopy(S3_BUCKET_EVENT_TFLINT)
    return event
