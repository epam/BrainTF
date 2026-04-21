from utilities.messages import HELP_MESSAGE

def test_correct_help_message():
    assert not HELP_MESSAGE.startswith('\n')