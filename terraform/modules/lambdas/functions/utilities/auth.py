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

    logger.info('Webhook token verified successfully.')


def webhook_authenticator(event: Dict[str, Any]):
    """
    Authenticates incoming webhook events based on the selected VCS provider and its respective
    authentication mechanism.

    Verifies the authenticity of webhook requests either through token-based or signature-based
    authentication, depending on the configured version control system (VCS) provider.

    Args:
        event (dict): The incoming webhook event. This should include a `headers` key
            containing the HTTP headers required for authentication.

    Raises:
        HTTPException: If the VCS provider is invalid or if authentication fails.
    """
    match config.vcs_provider:
        case "gitlab" if 'x-gitlab-token' in event.get('headers', {}):
            # Verify the GitLab token
            token_from_header: str = event.get('headers', {}).get('x-gitlab-token')
            logger.info(f"Authenticating {config.vcs_provider} webhook.")
            verify_token(token_from_header, config.webhook_secret)
        case 'github' if 'x-hub-signature-256' in event.get('headers', {}):

            # Verify the GitHub signature
            logger.info(f"Authenticating {config.vcs_provider} webhook.")
            verify_signature(event, config.webhook_secret)

        case _:
            raise HTTPException(status_code=403, detail="Invalid VCS provider!")


def verify_signature(event, secret_token) -> None:
    """
    Verifies the HMAC signature of a request payload to ensure its integrity and authentication.

    This function checks the `x-hub-signature-256` header present in the event's headers
    against an HMAC signature computed using the provided secret token and the payload body.
    If the signature does not match, an exception is raised.

    Args:
        event: A dictionary representing the request event. It should have the following keys:
            - `headers` (dict): A dictionary of header key-value pairs, where
              `x-hub-signature-256` is expected.
            - `body` (str): The raw payload body of the request.
        secret_token: A string used as the secret key for generating the HMAC signature.

    Raises:
        HTTPException: If the `x-hub-signature-256` header is missing, or if the computed
        signature does not match the header's signature.
    """
    signature_header = event.get('headers', {}).get('x-hub-signature-256')

    if not signature_header:
        raise HTTPException(status_code=403, detail="x-hub-signature-256 header is missing!")
    payload_body = event.get('body').encode('utf-8')
    hash_object = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=403, detail="Request signatures didn't match!")

    logger.info('Webhook signature verified successfully.')


def is_github_issue_comment(event: Dict[str, Any]) -> bool:
    """
    Determines if the provided event signifies a GitHub issue comment and validates its structure.

    This method checks if the given event corresponds to a GitHub webhook for an issue comment
    creation. If the event does not conform to the expected structure or is not an issue comment
    event, a MissingCommentContextException is raised. Otherwise, a boolean value or None is
    returned.

    Args:
        event (Dict[str, Any]): The event payload containing HTTP headers and a JSON body
            that represents the data from a GitHub webhook.

    Raises:
        MissingCommentContextException: If the event is not a valid GitHub issue comment
            event.

    Returns:
        bool | None: True if the event is a valid GitHub issue comment event; otherwise,
            None or an exception is raised.
    """
    github_event = event.get('headers', {}).get('x-github-event')
    webhook_payload = json.loads(event.get('body', ''))

    if webhook_payload.get('action') != 'created' or github_event != 'issue_comment':
        raise MissingCommentContextException('Not a GitHub issue comment event')
    else:
        return True
