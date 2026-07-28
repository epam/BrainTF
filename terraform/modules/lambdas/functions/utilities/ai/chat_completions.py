import time

import requests

from config import config
from utilities.logger import logger
from utilities.messages import SYSTEM_ROLE_MESSAGE


def generate_response_ai(messages: list, retries: int = 3) -> dict:
    """
    Generates a response from an AI model by sending a set of messages to the AI API,
    handles retries on certain types of errors, and parses the response to return
    useful message content and token usage information.

    Args:
        messages (list): A list of message dictionaries to send to the AI API. Each dictionary
            should have a "role" (e.g., "user", "assistant") and "content" (the text of the
            message).
        retries (int): The maximum number of retries allowed in case of API request failures.
            Defaults to 3.

    Returns:
        dict: A dictionary containing:
            - "message" (str): The AI-generated response content.
            - "tokens" (dict): A dictionary detailing token usage, with the following keys:
                - "prompt_tokens" (int): The number of tokens used for the input messages.
                - "completion_tokens" (int): The number of tokens generated for the output.
                - "total_tokens" (int): The total number of tokens used (sum of prompt and
                  completion tokens).

    Raises:
        requests.Timeout: If the API request times out and the retry limit is exceeded.
        requests.ConnectionError: If the API connection fails and the retry limit is exceeded.
        requests.HTTPError: If a server-side (5xx) or client-side (4xx) error occurs and the
            retry limit is exceeded.
    """
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
        logger.debug(f"Requesting AI API with baseurl: {config.ai_api_endpoint}")
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
