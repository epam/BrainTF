class FakeResponse:
    def __init__(self, status_code=200, json_data=None, raise_exc=None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self._raise_exc = raise_exc

    def raise_for_status(self):
        if self._raise_exc:
            raise self._raise_exc

    def json(self):
        return self._json_data


def test_generate_response_ai_success(patched_environment, ssm_setup, monkeypatch):
    from utilities.ai.chat_completions import generate_response_ai
    from utilities.messages import SYSTEM_ROLE_MESSAGE

    captured = {}

    def fake_post(url, headers, json, timeout):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse(
            status_code=200,
            json_data={
                "choices": [{"message": {"content": " fixed response  "}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            },
        )

    monkeypatch.setattr("utilities.ai.chat_completions.requests.post", fake_post)

    result = generate_response_ai([{"role": "user", "content": "hello"}])

    assert captured["url"] == "https://ai.example.com"
    assert captured["headers"]["Api-Key"] == "token"
    assert captured["json"]["model"] == "gpt-3.5-turbo"
    assert captured["json"]["messages"][0] == {"role": "system", "content": SYSTEM_ROLE_MESSAGE}
    assert captured["json"]["messages"][1] == {"role": "user", "content": "hello"}
    assert captured["timeout"] == (361, 361)
    assert result == {
        "message": "fixed response\n",
        "tokens": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }

def test_generate_response_ai_retries_then_success(patched_environment, ssm_setup, monkeypatch):
    from utilities.ai.chat_completions import generate_response_ai

    responses = [
        FakeResponse(status_code=500),
        FakeResponse(
            status_code=200,
            json_data={
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
            },
        ),
    ]
    post_calls = {"count": 0}
    sleeps = []

    def fake_post(*args, **kwargs):
        idx = post_calls["count"]
        post_calls["count"] += 1
        return responses[idx]

    monkeypatch.setattr("utilities.ai.chat_completions.requests.post", fake_post)
    monkeypatch.setattr("utilities.ai.chat_completions.time.sleep", lambda s: sleeps.append(s))

    result = generate_response_ai([{"role": "user", "content": "x"}], retries=3)

    assert post_calls["count"] == 2
    assert sleeps == [1]
    assert result["message"] == "ok\n"
    assert result["tokens"]["total_tokens"] == 3


def test_generate_response_ai_raises_after_retries(patched_environment, ssm_setup, monkeypatch):
    import requests
    from utilities.ai.chat_completions import generate_response_ai

    sleeps = []
    errors = []

    def fake_post(*args, **kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr("utilities.ai.chat_completions.requests.post", fake_post)
    monkeypatch.setattr("utilities.ai.chat_completions.time.sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr("utilities.ai.chat_completions.logger.error", lambda msg: errors.append(msg))

    try:
        generate_response_ai([{"role": "user", "content": "x"}], retries=2)
        assert False, "Expected timeout to be raised"
    except requests.Timeout:
        pass

    assert sleeps == [1, 2]
    assert len(errors) == 1
    assert "failed after 2 retries" in errors[0]


def test_generate_response_ai_defaults_when_response_fields_missing(patched_environment, ssm_setup, monkeypatch):
    from utilities.ai.chat_completions import generate_response_ai

    monkeypatch.setattr(
        "utilities.ai.chat_completions.requests.post",
        lambda *args, **kwargs: FakeResponse(status_code=200, json_data={}),
    )

    result = generate_response_ai([{"role": "user", "content": "x"}])

    assert result == {
        "message": "\n",
        "tokens": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }
