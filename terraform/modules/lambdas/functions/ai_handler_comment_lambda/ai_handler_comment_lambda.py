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
    """
    Processes the webhook payload from a version control system (VCS) and extracts relevant metadata
    based on the configured provider. The function is tailored to work with popular VCS providers
    like GitLab and GitHub, and it assumes payloads follow their respective webhook notification
    formats as described in their official documentation.

    Args:
        event (Dict[str, Any]): A dictionary representing the webhook event. The event must
            contain a 'body' field with a JSON-formatted string representing the payload received
            from the VCS webhook. Additional context can be included as needed.

    Returns:
        Dict[str, Any]: The original `event` dictionary updated with a 'metadata' field. The
            'metadata' field contains extracted information such as repository name/ID, merge or
            pull request ID, comment content, source branch, commit SHA, and comment ID, depending
            on the VCS provider.

    Raises:
        ValueError: If the VCS provider specified in the global `config.vcs_provider` is not
            supported or recognized.
    """
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
    """
    Handles an AWS Lambda function triggered by a Version Control System (VCS) webhook. The function
    validates the webhook request, processes the payload, and extracts bot commands, if any. It returns
    an appropriate HTTP status code and message based on the workflow and error conditions.

    Args:
        event: Dict[str, Any]
            The event data provided to the Lambda function, typically representing the VCS webhook
            payload, including headers and body.
        context: Any
            The runtime information of the Lambda function, including details of execution and
            environment.

    Returns:
        Dict[str, Any]: A dictionary containing the HTTP status code and message indicating the result
        of the function's execution. Known webhook and payload errors are handled internally and
        converted into HTTP responses.
    """
    try:
        # Validate the request headers from the VCS webhook
        webhook_authenticator(event)
        # Process the VCS webhook payload
        process_vcs_webhook_payload(event)
        # Handle bot commands from the comment
        handle_comment_commands(event)

        logger.info('Lambda invocation completed successfully.')
        return {'statusCode': HTTP_SUCCESS, 'body': 'Successfully invoked'}

    except InvalidTokenException as error:
        logger.error(f'Invalid token: {error}.')
        return {'statusCode': HTTP_FORBIDDEN, 'body': 'Forbidden'}

    except MissingCommentContextException as exception:
        logger.debug(f'Webhook comment is outside bot command context: {exception}.')
        return {'statusCode': HTTP_SUCCESS, 'body': 'Out of bot context, no action taken'}

    except (json.JSONDecodeError, HTTPException, MissingWebhookDataException, MissingTokenException) as error:
        logger.error(f'Failed to process VCS webhook payload: {error}.')
        return {'statusCode': HTTP_BAD_REQUEST, 'body': 'Invalid payload'}
