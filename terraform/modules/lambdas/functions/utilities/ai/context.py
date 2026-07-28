import time
import zlib
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List

from botocore.exceptions import ClientError
from config import config
from utilities.aws import get_messages_from_db, put_messages_to_db
from utilities.logger import logger


def cutoff_large_text(
        text: str,
        max_length_bytes: int = 400000,
) -> str:
    """
    Truncates a large text string to fit within a specified maximum byte length.
    If the string exceeds the byte limit, it adds a marker indicating truncation and retains
    a portion of the start and end of the string. The text is truncated in UTF-8 encoding.

    Args:
        text (str): The input string that may need to be truncated.
        max_length_bytes (int): The maximum allowed byte length of the output. Defaults to 400000.

    Returns:
        str: The text string truncated to adhere to the specified byte length,
        if necessary, with a cutoff marker. The truncation preserves the start and
        end parts of the input text.
    """
    byte_string: bytes = text.encode('utf-8')

    if len(byte_string) < max_length_bytes:
        return text

    cutoff_block: bytes = b"\n\n--- cutoff ---\n\n"
    cutoff_block_length: int = len(cutoff_block)

    # Returns truncated text with a cutoff marker if too large
    available_length: int = max_length_bytes - cutoff_block_length
    index: int = available_length // 2
    start_of_string = byte_string[:index]
    end_of_string = byte_string[-index:]
    result_string: bytes = start_of_string + cutoff_block + end_of_string
    cutoff_text: str = result_string.decode('utf-8', errors='ignore')

    return cutoff_text


def create_context_memory_window(
        event: Dict[str, Any],
        max_retries: int = 3,
) -> None:
    """
    Attempts to create a context memory window by storing user and AI conversation data into a database. This function
    retrieves prior messages associated with a unique key, calculates appropriate sequence keys (`sk`), compresses,
    and stores new context for retrieval. The process includes error handling and retries for certain transient database
    errors.

    Args:
        event (Dict[str, Any]): Dictionary containing metadata and other information.
            It must include a `metadata` key with `commit_short_sha`, and optionally `prompt` and `ai_response` strings.
        max_retries (int): Maximum number of retries for transient database errors. Defaults to 3.

    Raises:
        ValueError: If `commit_short_sha` is missing in the `metadata` field of the event.
        ClientError: If a transient error persists after the specified retries or for non-retriable database errors.
    """
    metadata: Dict[str, Any] = event.get("metadata", {})
    commit_short_sha: str | None = metadata.get("commit_short_sha")

    if not commit_short_sha:
        raise ValueError("Missing commit_short_sha in event.metadata")

    for attempt in range(1, max_retries + 1):
        try:
            messages_from_db: List[Dict[str, Any]] = get_messages_from_db(config.table_name, commit_short_sha) or []

            last_sk: Decimal = (
                messages_from_db[-1]["sk"]
                if messages_from_db
                else Decimal(-1)  # ensures first sk = 0
            )

            prompt: str = event.get('metadata').get('prompt', '')
            ai_response: str = event.get('metadata').get('ai_response', '')
            binary_prompt: bytes = event.get('metadata').get('prompt', '').encode('utf-8')
            binary_ai_response: bytes = event.get('metadata').get('ai_response', '').encode('utf-8')

            # Calculate TTL: Current Unix timestamp + 30 days (in seconds)
            # DynamoDB TTL must be a Unix timestamp in seconds
            ttl_delta: timedelta = timedelta(days=config.ttl_delta_days)
            future_date: datetime = datetime.now() + ttl_delta
            ttl_timestamp: int = int(future_date.timestamp())

            messages_to_db: List[Dict[str, Any]] = [
                {
                    "pk": commit_short_sha,
                    "sk": last_sk + Decimal(1),
                    "role": "user",
                    "zipped_content": zlib.compress(binary_prompt),
                    "brief_content": cutoff_large_text(prompt),
                    "ttl": ttl_timestamp
                },
                {
                    "pk": commit_short_sha,
                    "sk": last_sk + Decimal(2),
                    "role": "assistant",
                    "zipped_content": zlib.compress(binary_ai_response),
                    "brief_content": cutoff_large_text(ai_response),
                    "ttl": ttl_timestamp
                },
            ]

            put_messages_to_db(config.table_name, messages_to_db)

            logger.debug(
                f"Stored context window for pk={commit_short_sha} "
                f"with sk={messages_to_db[0]['sk']} and {messages_to_db[1]['sk']}."
            )
            return

        except ClientError as e:
            error_code: str = e.response["Error"]["Code"]

            if error_code in (
                    "TransactionCanceledException",
                    "ConditionalCheckFailedException",
                    "ProvisionedThroughputExceededException",
            ):
                if attempt >= max_retries:
                    logger.error(
                        f"Failed to store context after {max_retries} retries "
                        f"for pk={commit_short_sha}."
                    )
                    raise
                # Backoff time
                backoff_time: int = 2 ** attempt
                logger.warning(
                    f"Retrying context storage. Attempt {attempt}/{max_retries} "
                    f"for pk={commit_short_sha}; waiting {backoff_time}s."
                )
                time.sleep(backoff_time)
                continue  # Ensure the loop retries on ClientError
            # Any other error is fatal
            raise


def get_context_memory_window(
        event: Dict[str, Any],
        max_retries: int = 3,
) -> List[Dict[str, Any]]:
    """
    Fetches and processes context messages associated with a specific commit SHA from a database.

    This function retrieves messages identified by a `commit_short_sha` key found in the `metadata` section of the
    provided event. It attempts to fetch those messages up to the specified number of retries if an error occurs during
    the fetch. The retrieved messages are then decompressed and transformed for further processing.

    Args:
        event: Dictionary containing event metadata. Must include a `commit_short_sha` key in its `metadata` field for
        identifying the relevant data.
        max_retries: Maximum number of retry attempts to fetch context messages in case of a failure.

    Raises:
        ValueError: If `commit_short_sha` is missing in the event's metadata.
        ClientError: If the fetch operation fails even after the specified number of retry attempts.

    Returns:
        A list of dictionaries containing processed messages, where decompressed content replaces any
        compressed message fields in the original data.
    """
    metadata: Dict = event.get("metadata", {})
    commit_short_sha: str | None = metadata.get("commit_short_sha")

    if not commit_short_sha:
        raise ValueError("Missing commit_short_sha in event.metadata")

    for attempt in range(1, max_retries + 1):
        try:
            messages_from_db: List[Dict[str, Any]] = get_messages_from_db(config.table_name, commit_short_sha)
            messages_for_ai: List[Dict[str, Any]] = [
                {key.lstrip('zipped_') if key == 'zipped_content'
                 else key: zlib.decompress(value.value).decode('utf-8') if key == 'zipped_content'
                else value
                 for key, value in item.items() if key in ('role', 'zipped_content')}
                for item in messages_from_db
            ]

            return messages_for_ai

        except ClientError:
            if attempt >= max_retries:
                logger.exception(
                    f"Failed to fetch context after {max_retries} retries "
                    f"for pk={commit_short_sha}."
                )
                raise
            # Backoff time
            backoff_time: int = 2 ** attempt
            logger.warning(
                f"Retrying context fetch after ClientError. "
                f"Attempt {attempt}/{max_retries} for pk={commit_short_sha}; "
                f"waiting {backoff_time}s."
            )
            time.sleep(backoff_time)
            continue  # Ensure the loop retries on ClientError
    return []
