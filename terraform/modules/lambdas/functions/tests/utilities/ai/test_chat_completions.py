import logging
from types import SimpleNamespace
from typing import Any

import httpx
import pytest
from openai.types.chat import ChatCompletionUserMessageParam


class FakeOpenAIResponse:
    def __init__(self, data: dict[str, Any] | None = None):
        self._data = data or {}
        self.choices = []

        for choice_data in self._data.get("choices", []):
            message_data = choice_data.get("message")
            message = None
            if message_data is not None:
                message = SimpleNamespace(content=message_data.get("content"))
            self.choices.append(SimpleNamespace(message=message))

        usage_data = self._data.get("usage")
        self.usage = SimpleNamespace(**usage_data) if isinstance(usage_data, dict) else None


def user_message(content: str) -> ChatCompletionUserMessageParam:
    return {"role": "user", "content": content}


def fake_openai_client(fake_create):
    def fake_openai(**kwargs: Any):
        assert kwargs["max_retries"] == 0
        return SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=fake_create),
            ),
        )

    return fake_openai


def test_generate_response_ai_success(patched_environment, ssm_setup, monkeypatch):
    from utilities.ai.chat_completions import generate_response_ai
    from utilities.messages import SYSTEM_ROLE_MESSAGE

    captured = {}

    def fake_create(**kwargs):
        captured["create_kwargs"] = kwargs
        return FakeOpenAIResponse(
            {
                "choices": [{"message": {"content": " fixed response  "}}],
                "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            }
        )

    def fake_openai(**kwargs):
        captured["client_kwargs"] = kwargs
        return SimpleNamespace(
            chat=SimpleNamespace(
                completions=SimpleNamespace(create=fake_create),
            ),
        )

    monkeypatch.setattr("utilities.ai.chat_completions.OpenAI", fake_openai)

    result = generate_response_ai([user_message("hello")])

    assert captured["client_kwargs"]["base_url"] == "https://api.testopenai.com/v1"
    assert captured["client_kwargs"]["api_key"] == "token"
    assert captured["client_kwargs"]["max_retries"] == 0
    assert captured["create_kwargs"]["model"] == "gpt-3.5-turbo"
    assert captured["create_kwargs"]["messages"][0] == {"role": "system", "content": SYSTEM_ROLE_MESSAGE}
    assert captured["create_kwargs"]["messages"][1] == {"role": "user", "content": "hello"}
    assert captured["create_kwargs"]["temperature"] == 0.4
    assert result == {
        "message": " fixed response  ",
        "tokens": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }


def test_generate_response_ai_retries_then_success(patched_environment, ssm_setup, monkeypatch):
    from openai import APITimeoutError

    from utilities.ai.chat_completions import generate_response_ai

    request = httpx.Request("POST", "https://api.testopenai.com/v1")
    responses = [
        APITimeoutError(request=request),
        FakeOpenAIResponse(
            {
                "choices": [{"message": {"content": "ok"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
            }
        ),
    ]
    create_calls = {"count": 0}
    sleeps = []

    def fake_create(**kwargs: Any):
        assert kwargs["temperature"] == 0.4
        idx = create_calls["count"]
        create_calls["count"] += 1
        response = responses[idx]
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(
        "utilities.ai.chat_completions.OpenAI",
        fake_openai_client(fake_create),
    )
    monkeypatch.setattr("utilities.ai.chat_completions.time.sleep", lambda s: sleeps.append(s))

    result = generate_response_ai([user_message("x")], retries=3)

    assert create_calls["count"] == 2
    assert sleeps == [1]
    assert result["message"] == "ok"
    assert result["tokens"]["total_tokens"] == 3


def test_generate_response_ai_raises_after_retries(patched_environment, ssm_setup, monkeypatch, caplog):
    from openai import APITimeoutError

    from utilities.ai.chat_completions import generate_response_ai

    sleeps = []
    create_calls = {"count": 0}
    request = httpx.Request("POST", "https://api.testopenai.com/v1")

    def fake_create(**kwargs: Any):
        assert kwargs["temperature"] == 0.4
        create_calls["count"] += 1
        raise APITimeoutError(request=request)

    monkeypatch.setattr(
        "utilities.ai.chat_completions.OpenAI",
        fake_openai_client(fake_create),
    )
    monkeypatch.setattr("utilities.ai.chat_completions.time.sleep", lambda s: sleeps.append(s))

    caplog.set_level(logging.ERROR, logger="braintf")

    messages = [user_message("x")]

    with pytest.raises(APITimeoutError):
        generate_response_ai(messages, retries=2)

    assert create_calls["count"] == 3
    assert sleeps == [1, 2]
    assert "failed after 2 retries" in caplog.text


def test_generate_response_ai_defaults_when_usage_or_content_missing(patched_environment, ssm_setup, monkeypatch):
    from utilities.ai.chat_completions import generate_response_ai

    def fake_create(**kwargs: Any):
        assert kwargs["temperature"] == 0.4
        return FakeOpenAIResponse(
            {"choices": [{"message": {"content": None}}]},
        )

    monkeypatch.setattr(
        "utilities.ai.chat_completions.OpenAI",
        fake_openai_client(fake_create),
    )

    result = generate_response_ai([user_message("x")])

    assert result == {
        "message": "",
        "tokens": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
    }


def test_generate_response_ai_raises_when_response_choices_missing(
        patched_environment,
        ssm_setup,
        monkeypatch,
):
    from utilities.ai.chat_completions import generate_response_ai

    def fake_create(**kwargs: Any):
        assert kwargs["temperature"] == 0.4
        return FakeOpenAIResponse()

    monkeypatch.setattr(
        "utilities.ai.chat_completions.OpenAI",
        fake_openai_client(fake_create),
    )

    messages = [user_message("x")]

    with pytest.raises(IndexError):
        generate_response_ai(messages)
