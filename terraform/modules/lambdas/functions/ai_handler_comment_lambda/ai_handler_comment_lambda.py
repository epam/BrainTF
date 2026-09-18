import json
from typing import Any

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


def process_vcs_webhook_payload(event: dict[str, Any]) -> dict[str, Any]:
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
    body: str = event['body']

    webhook_payload: dict[str, Any] = json.loads(body)

    metadata: dict[str, Any] = {}

    match config.vcs_provider:
        case 'gitlab':
            try:
                merge_request: dict[str, Any] = webhook_payload['merge_request']
                object_attributes: dict[str, Any] = webhook_payload['object_attributes']
                commit_id: str = merge_request['last_commit']['id']
                repo_id_or_name: int = webhook_payload['project_id']
                source_branch: str = merge_request['source_branch']
                comment_text: str = object_attributes['note']
                merge_or_pull_req_id: int = merge_request['iid']
                comment_id: str = object_attributes['id']
            except (KeyError, TypeError):
                raise MissingWebhookDataException

            if any(value is None or value == '' for value in (
                    commit_id,
                    repo_id_or_name,
                    source_branch,
                    comment_text,
                    merge_or_pull_req_id,
                    comment_id
            )):
                raise MissingWebhookDataException

            comment_text = comment_text.strip()
            commit_short_sha: str = commit_id[:8]

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
            try:
                repository: dict[str, Any] = webhook_payload['repository']
                repo_id_or_name: str = repository['full_name']
                comment: dict[str, Any] = webhook_payload['comment']
                comment_text: str = comment['body']
                comment_id: int = comment['id']
                issue: dict[str, Any] = webhook_payload['issue']
                merge_or_pull_req_id: int = issue['number']
            except (KeyError, TypeError):
                raise MissingWebhookDataException

            if any(value is None or value == '' for value in (
                    repo_id_or_name,
                    comment_text,
                    comment_id,
                    merge_or_pull_req_id
            )):
                raise MissingWebhookDataException

            comment_text = comment_text.strip()
            commit_sha: str = get_last_commit_sha_github(repo_id_or_name, merge_or_pull_req_id)
            commit_short_sha: str = commit_sha[:8]

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


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:  # noqa:
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
