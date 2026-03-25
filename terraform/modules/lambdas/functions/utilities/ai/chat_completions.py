import time

import requests

from config import config
from utilities.logger import logger
from utilities.messages import SYSTEM_ROLE_MESSAGE


def generate_response_ai(messages: list, retries: int = 3) -> dict:
    messages = [{"role": "system", "content": SYSTEM_ROLE_MESSAGE}] + messages
    headers = {
        "Content-Type": "application/json",
        "Api-Key": config.ai_api_token
    }

    payload = {
        "model": config.llm_model,
        "messages": messages,
        "temperature": 0.4
    }

    attempt = 0

    while True:
        try:
            resp = requests.post(
                config.ai_api_endpoint,
                headers=headers,
                json=payload,
                timeout=config.default_timeout
            )

            # Retry on 5xx responses
            if 500 <= resp.status_code < 600:
                raise requests.HTTPError(f"Server error: {resp.status_code}", response=resp)

            resp.raise_for_status()
            break  # success → exit retry loop

        except (requests.Timeout,
                requests.ConnectionError,
                requests.HTTPError) as e:

            attempt += 1

            if attempt > retries:
                logger.error(f"AI API request failed after {retries} retries: {e}")
                raise

            wait = 2 ** (attempt - 1)
            logger.warning(f"AI API error: {e} — retry {attempt}/{retries} in {wait}s")
            time.sleep(wait)

    # Parse JSON once
    data_json = resp.json()

    # Safely extract content
    message = (
            data_json.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip() + "\n"
    )

    usage = data_json.get("usage", {})
    prompt_tokens = usage.get("prompt_tokens", 0)
    completion_tokens = usage.get("completion_tokens", 0)
    total_tokens = usage.get("total_tokens", 0)

    logger.info(
        f"Prompt tokens: {prompt_tokens}, "
        f"Completion tokens: {completion_tokens}, "
        f"Total tokens: {total_tokens}"
    )

    return {
        "message": message,
        "tokens": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    }
