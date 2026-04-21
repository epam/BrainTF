from tests.utilities.auth.conftest import *
import pytest

WEBHOOK_EVENT_METADATA_GITHUB: dict = \
    {'repo_id_or_name': 'some-org/BrainTF',
     'source_branch': None,
     'comment_text': 'bot list',
     'merge_or_pull_req_id': 32,
     'commit_short_sha': '1234',
     'comment_id': 3927342816}

WEBHOOK_EVENT_METADATA_GITLAB: dict = \
    {'repo_id_or_name': 252745,
     'source_branch': 'SYNC-branch',
     'comment_text': ':information_source: AI Bot message\n\n---\n\nComment Commands Help\n\n---\n\nThis '
                     'system supports structured comment commands to trigger automation.\n\nBelow is a guide '
                     'to the supported commands:\n\n`bot approve *` or `bot approve all` - triggers the '
                     'approval of committing **all** files fixed by AI bot.\n\n`bot approve <path/to/file1> ['
                     '<path/to/file2> ...]` - triggers the approval of committing a **specific file** or '
                     '**files** fixed by AI bot.\n\n`bot list` - lists files correted by AI and ready to '
                     'commit.\n\n`bot prompt <user prompt>` - sends custom prompt to AI.\n\n`help` - shows '
                     'this help information in the GitLab MR notes.\n\n---\n\n> :warning: Notes:\n>\n> All '
                     'commands must begin with a **context word** (`bot`, `help`, etc.).\n>\n> Only `bot` '
                     'context supports nested command logic (e.g. `approve`).',
     'merge_or_pull_req_id': 86,
     'commit_short_sha': 'c1a2c57a',
     'comment_id': 13791132}


@pytest.fixture
def expected_webhook_event_metadata_github():
    return WEBHOOK_EVENT_METADATA_GITHUB


@pytest.fixture
def expected_webhook_event_metadata_gitlab():
    return WEBHOOK_EVENT_METADATA_GITLAB
