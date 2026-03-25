import hashlib
import hmac
import json
from typing import Any, Dict

from config import config
from utilities.exceptions import (HTTPException, InvalidTokenException,
                                  MissingCommentContextException,
                                  MissingTokenException)
from utilities.logger import logger


def verify_token(token_from_header: str, expected_token: str) -> None:
    """Verify the token provided in the header against the expected token.

    Args:
        token_from_header (str): The token provided in the HTTP header.
        expected_token (str): The expected token value.

    Raises:
        InvalidTokenException: If the provided token does not match the expected token.
        MissingTokenException: If the token is missing from the header.
    """
    if token_from_header:
        if token_from_header != expected_token:
            # Token mismatch, raise an exception
            raise InvalidTokenException('Invalid X-Gitlab-Token!')
    else:
        # Token missing, raise an exception
        raise MissingTokenException('X-Gitlab-Token header is missing!')

    logger.info('Token successfully verified!')


def webhook_authenticator(event: dict) -> None:
    if config.vcs_provider:
        # Retrieve tokens from request headers and SSM according to VCS provider
        match config.vcs_provider:
            case "gitlab" if 'x-gitlab-token' in event.get('headers'):
                # Verify the GitLab token
                token_from_header: str = event.get('headers').get('x-gitlab-token')
                logger.info(f"Webhook authentication for {config.vcs_provider}")
                verify_token(token_from_header, config.webhook_secret)
            case 'github' if 'x-hub-signature-256' in event.get('headers'):

                # Verify the GitHub signature
                logger.info(f"Webhook authentication for {config.vcs_provider}")
                verify_signature(event, config.webhook_secret)

            case _:
                logger.info(f"No authentication required for {config.vcs_provider}")


def verify_signature(event, secret_token):
    """Verify that the payload was sent from GitHub by validating SHA256.

    Raise and return 403 if not authorized.

    Args:
        payload_body: original request body to verify (request.body())
        secret_token: GitHub app webhook token (WEBHOOK_SECRET)
        signature_header: header received from GitHub (x-hub-signature-256)
    """
    signature_header = event.get('headers', {}).get('x-hub-signature-256')
    payload_body = event.get('body').encode('utf-8')

    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")

    logger.info('Token successfully verified!')


def is_github_issue_comment(event: Dict[str, Any]) -> Exception | None:
    """
    Determines if the provided event is a GitHub issue comment event.

    This function evaluates an event dictionary to check whether it corresponds to a
    GitHub issue comment event created via a webhook. If the event doesn't meet the
    expected conditions, it raises a `MissingCommentContextException`.

    Args:
        event (Dict[str, Any]): The event dictionary, which includes information such as
            headers and body. The `headers` key should contain a `x-github-event` key, and
            the `body` key should be a JSON string containing a GitHub webhook payload.

    Returns:
        Exception | None: Raises a `MissingCommentContextException` if the event is
            not a valid GitHub issue comment creation event. Otherwise, returns None.

    Raises:
        MissingCommentContextException: If the provided event does not correspond to
            a GitHub issue comment creation event.
    """
    github_event = event.get('headers', {}).get('x-github-event')
    webhook_payload = json.loads(event.get('body'))

    if webhook_payload.get('action') != 'created' and github_event == 'issue_comment':
        raise MissingCommentContextException('Not a GitHub issue comment event')
