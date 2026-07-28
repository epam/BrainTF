import time

from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI
from openai.types import CompletionUsage
from openai.types.chat import (ChatCompletionMessageParam,
                               ChatCompletionSystemMessageParam)

from config import config
from utilities.logger import logger
from utilities.messages import SYSTEM_ROLE_MESSAGE


def generate_response_ai(messages: list[ChatCompletionMessageParam], retries: int = 3) -> dict:
    """
    Generates a response from an AI model based on the provided messages and retry logic.

    This function sends a request to the AI API to generate a completion for the given chat
    messages. It includes customizable retry logic to handle transient errors during the
    API communication.

    Args:
        messages (list[ChatCompletionMessageParam]): A list of message parameters to be sent
            to the AI API for generating a response. These typically include user and system
            prompts.
        retries (int, optional): The maximum number of retry attempts to make in case of API
            errors. Defaults to 3.

    Returns:
        dict: A dictionary containing the AI-generated message and token usage details. The
            keys are:
            - "message": The generated message content (str).
            - "tokens": A dictionary with token usage details, including:
                - "prompt_tokens" (int): Number of tokens used for the prompt.
                - "completion_tokens" (int): Number of tokens used for the completion.
                - "total_tokens" (int): Total tokens consumed.

    Raises:
        APITimeoutError: If the API request times out and exceeds the allowed retry attempts.
        APIConnectionError: If there is a connection issue with the API.
        APIStatusError: If the API returns an invalid or error status code after retries.
    """
    system_role_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": SYSTEM_ROLE_MESSAGE
    }
    request_messages: list[ChatCompletionMessageParam] = [system_role_message] + messages

    client = OpenAI(
        base_url=config.ai_api_endpoint,
        api_key=config.ai_api_token,
        max_retries=0,
    )

    attempt = 0

    while True:
        logger.debug(f"Requesting AI API with baseurl: {config.ai_api_endpoint}")
        try:
            response = client.chat.completions.create(
                model=config.llm_model,
                messages=request_messages,
                temperature=0.4,
            )

            break

        except (APITimeoutError, APIConnectionError, APIStatusError) as e:

            attempt += 1

            if attempt > retries:
                logger.error(f"AI API request failed after {retries} retries: {e}.")
                raise

            wait = 2 ** (attempt - 1)
            logger.warning(f"AI API error: {e} — retry {attempt}/{retries} in {wait}s")
            time.sleep(wait)

    content = response.choices[0].message.content or ''

    usage: CompletionUsage | None = response.usage
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    total_tokens = usage.total_tokens if usage else 0

    logger.info(
        f"AI API used prompt tokens: {prompt_tokens}, completion tokens: {completion_tokens}, total tokens: {total_tokens}"
    )

    return {
        "message": content,
        "tokens": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }
    }
