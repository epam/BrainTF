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
    Generates a response from an AI system by sending a list of message prompts and processing the
    response. Handles retries in case of connection or server errors with an exponential backoff
    strategy.

    Args:
        messages (list[ChatCompletionMessageParam]): A list of message objects to be sent as prompts
            to the AI system.
        retries (int, optional): The number of retry attempts to make in case of errors. Defaults to 3.

    Returns:
        dict: A dictionary containing the AI's response message and token usage details:
            - 'message': The content of the response as a string.
            - 'tokens': A nested dictionary with token usage details:
                - 'prompt_tokens': The number of tokens used in the input prompt.
                - 'completion_tokens': The number of tokens used in the generated completion.
                - 'total_tokens': The combined total of prompt and completion tokens.

    Raises:
        ValueError: If the AI response contains no choices or is improperly formatted.
        APITimeoutError: If the API request times out.
        APIConnectionError: If there is a connection issue with the API.
        APIStatusError: If the API returns an unexpected status code.
    """
    system_role_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": SYSTEM_ROLE_MESSAGE
    }
    request_messages: list[ChatCompletionMessageParam] = [system_role_message] + messages

    client = OpenAI(
        base_url=config.ai_api_base_url,
        api_key=config.ai_api_token,
        max_retries=0,
    )

    attempt = 0

    while True:
        logger.debug(f"Requesting AI API with baseurl: {config.ai_api_base_url}")
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

    if not response.choices:
        raise ValueError("AI API response is missing choices.")

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
