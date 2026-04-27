import json
from typing import Any, Dict

from config import config
from utilities.auth import is_github_issue_comment, webhook_authenticator
from utilities.exceptions import (HTTPException, InvalidTokenException,
                                  MissingCommentContextException,
                                  MissingTokenException,
                                  MissingWebhookDataException)
from utilities.handlers import handle_comment_commands
from utilities.logger import logger
from utilities.vcs.github_functions import get_last_commit_sha_github

HTTP_SUCCESS: int = 200
HTTP_BAD_REQUEST: int = 400
HTTP_FORBIDDEN: int = 403


def process_vcs_webhook_payload(event: Dict[str, Any]) -> Dict[str, Any]:
    """Process the VCS webhook payload and return the relevant information."""
    logger.info('Processing VCS webhook payload...')
    body: str = event.get('body', '{}')

    webhook_payload: Dict[str, Any] = json.loads(body)

    metadata: Dict[str, Any] = {}

    match config.vcs_provider:
        case 'gitlab':
            commit_id: str | None = webhook_payload.get('merge_request', {}).get('last_commit', {}).get('id')

            repo_id_or_name: str | None = webhook_payload.get('project_id')
            source_branch: str | None = webhook_payload.get('merge_request', {}).get('source_branch')
            comment_text: str = webhook_payload.get('object_attributes', {}).get('note', '').strip()
            merge_or_pull_req_id: str = webhook_payload.get('merge_request', {}).get('iid')
            commit_short_sha: str | None = commit_id[:8] if commit_id else None
            comment_id: str | None = webhook_payload.get('object_attributes', {}).get('id')

            metadata = {
                'repo_id_or_name': repo_id_or_name,
                'source_branch': source_branch,
                'comment_text': comment_text,
                'merge_or_pull_req_id': merge_or_pull_req_id,
                'commit_short_sha': commit_short_sha,
                'comment_id': comment_id,
            }

        case 'github':
            is_github_issue_comment(event)
            repository: Dict[str, Any] = webhook_payload.get('repository', {}) or {}
            repo_id_or_name: str = repository.get('full_name', '')
            comment: Dict[str, Any] = webhook_payload.get('comment', {}) or {}
            comment_text: str = comment.get('body', '').strip()
            comment_id: str | None = comment.get('id')
            issue: Dict[str, Any] = webhook_payload.get('issue', {})
            merge_or_pull_req_id: int = issue.get('number', 0)
            commit_sha: str | None = get_last_commit_sha_github(repo_id_or_name, merge_or_pull_req_id)
            commit_short_sha: str | None = commit_sha[:8] if commit_sha else None

            metadata = {
                'repo_id_or_name': repo_id_or_name,
                'source_branch': None,
                'comment_text': comment_text,
                'merge_or_pull_req_id': merge_or_pull_req_id,
                'commit_short_sha': commit_short_sha,
                'comment_id': comment_id,
            }

        case _:
            # Unknown or unsupported provider
            raise ValueError(f"Unsupported VCS provider founded in config: {config.vcs_provider}")

    event.setdefault('metadata', {}).update(metadata)
    return event


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:  # noqa:
    """Handle the AWS Lambda function invocation.

    Args:
        event (Dict[str, Any]): The event data passed to the Lambda function.
        context (Any): The runtime context for the Lambda function.

    Returns:
        Dict[str, Any]: The HTTP response with status code and body.
    """
    try:
        # Validate the request headers from the VCS webhook
        webhook_authenticator(event)
        # Process the VCS webhook payload
        process_vcs_webhook_payload(event)
        # Handle bot commands from the comment
        handle_comment_commands(event)

        logger.info('Successfully invoked')
        return {'statusCode': HTTP_SUCCESS, 'body': 'Successfully invoked'}

    except InvalidTokenException as e:
        logger.warning(f'Invalid token: {str(e)}')
        return {'statusCode': HTTP_FORBIDDEN, 'body': 'Forbidden'}

    except MissingCommentContextException as e:
        logger.warning(f'No comment context: {str(e)}')
        return {'statusCode': HTTP_SUCCESS, 'body': 'Out of bot context, no action taken'}

    except (json.JSONDecodeError, HTTPException, MissingWebhookDataException, MissingTokenException) as e:
        logger.error(f'Error in webhook payload: {str(e)}')
        return {'statusCode': HTTP_BAD_REQUEST, 'body': 'Invalid payload'}
