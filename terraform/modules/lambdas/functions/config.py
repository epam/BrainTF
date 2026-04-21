import os
from functools import cached_property
from typing import Any, Dict, Optional

import boto3
from botocore.config import Config


class _ConfigLambda:
    """
    Centralizes loading, validation, and secure retrieval of configuration needed by
    the Lambda entrypoint. Environment variables are normalized and validated eagerly,
    ensuring integrations for VCS, webhooks, artifacts, AI services, DynamoDB, and
    logging fail fast when misconfigured.

    Attributes:
        default_timeout (tuple[float, float]): Default connection and read timeouts for
            boto3 operations.
        boto3_config (Config): boto3 configuration instance initialized with shared
            timeout values.
        vcs_provider (str): Name of the VCS vendor (github, gitlab, bitbucket).
        vcs_token_name (str): SSM parameter name holding the VCS API token.
        vcs_api_endpoint (str): Fully qualified base URL for VCS REST requests.
        webhook_secret_name (str): SSM parameter name containing the webhook secret.
        artifacts_bucket (str): S3 bucket that stores build artifacts.
        path_to_artifacts (str): Folder within the artifacts bucket for uploads.
        ai_api_token_name (str): SSM parameter name for AI service credentials.
        llm_model (str): Identifier of the large language model to invoke.
        ai_api_endpoint (str): Fully qualified URL for the AI service.
        table_name (str): DynamoDB table name for persistent state.
        log_level (str): Logging verbosity level.
        rag_enabled (bool): Feature flag indicating whether RAG is enabled.
        ttl_delta_days (int): Number of days added to compute DynamoDB TTLs.
        git_api_endpoint_version (str): Version suffix appended to the VCS API base URL.

    Environment Variables:
        VCS_PROVIDER: Overrides the active VCS provider.
        VCS_TOKEN_NAME: Points to the SSM parameter storing the VCS token.
        VCS_API_ENDPOINT: Supplies the VCS REST endpoint.
        WEBHOOK_SECRET_NAME: Provides the SSM parameter key for webhook secrets.
        ARTIFACTS_BUCKET: Sets the artifact storage bucket.
        ARTIFACTS_PATH: Specifies the path under the artifact bucket.
        AI_API_TOKEN_NAME: Points to the AI credential parameter.
        LLM_MODEL: Identifies the LLM to use for inference.
        AI_API_ENDPOINT: Supplies the AI service endpoint URL.
        DYNAMODB_TABLE_NAME: Sets the application’s DynamoDB table name.
        LOG_LEVEL: Controls the log verbosity.
        RAG_ENABLED: Toggles Retrieval-Augmented Generation support.
        TTL_DELTA_DAYS: Adjusts the TTL offset in days.

    Notes:
        * URLs must include an explicit scheme (``http`` or ``https``) to pass validation.
        * Boolean flags accept ``true``, ``1``, or ``yes`` (case-insensitive) as truthy.
        * Secrets retrieved from SSM are memoized via ``functools.cached_property`` to
          minimize repeated network calls.
        * Validation raises ``ValueError`` with descriptive messages whenever required
          configuration is missing or malformed.
    """
    def __init__(self) -> None:
        self.default_timeout: tuple[float, float] = (361, 361)
        self.boto3_config: Config = Config(connect_timeout=self.default_timeout[0],
                                           read_timeout=self.default_timeout[1])

        # Load environment variables
        self.vcs_provider: str = os.environ.get("VCS_PROVIDER", "github")
        self.vcs_token_name: str = os.environ.get('VCS_TOKEN_NAME')
        self.vcs_api_endpoint: str = os.environ.get('VCS_API_ENDPOINT')
        self.webhook_secret_name: str = os.environ.get('WEBHOOK_SECRET_NAME')
        self.artifacts_bucket: str = os.environ.get('ARTIFACTS_BUCKET')
        self.path_to_artifacts: str = os.environ.get('ARTIFACTS_PATH', 'artifacts')
        self.ai_api_token_name: str = os.environ.get('AI_API_TOKEN_NAME')
        self.llm_model: str = os.environ.get("LLM_MODEL")
        self.ai_api_endpoint: str = os.environ.get("AI_API_ENDPOINT")
        self.table_name: str = os.environ.get("DYNAMODB_TABLE_NAME")
        self.log_level: str = os.environ.get("LOG_LEVEL", "INFO").upper()
        self.rag_enabled: bool = os.environ.get("RAG_ENABLED", "False").lower() in ("true", "1", "yes")
        self.ttl_delta_days: int = int(os.environ.get("TTL_DELTA_DAYS", 30))
        self.git_api_endpoint_version: str = '/api/v4'

        # Validate all configuration
        self._validate_config()

    def _validate_config(self) -> None:
        """
        Validates all configuration parameters to ensure they are set and have
        the expected format.

        Raises:
            ValueError: If any required configuration is missing or has an invalid format.
        """
        self._validate_vcs_config()
        self._validate_webhook_config()
        self._validate_s3_config()
        self._validate_ai_config()
        self._validate_dynamodb_config()
        self._validate_logging_config()

    def _validate_vcs_config(self) -> None:
        """Validates VCS-related configuration."""
        if self.vcs_provider not in ("github", "gitlab", "bitbucket"):
            raise ValueError(
                f"Invalid VCS_PROVIDER: {self.vcs_provider}. "
                f"Must be one of: github, gitlab, bitbucket"
            )

        if not self.vcs_token_name:
            raise ValueError("VCS_TOKEN_NAME environment variable is required")

        if not self.vcs_api_endpoint:
            raise ValueError("VCS_API_ENDPOINT environment variable is required")

        if not self.vcs_api_endpoint.startswith(('http://', 'https://')):
            raise ValueError(
                f"VCS_API_ENDPOINT must be a valid URL: {self.vcs_api_endpoint}"
            )
        if self.vcs_api_endpoint.endswith(self.git_api_endpoint_version):
            raise ValueError(
                f"VCS_API_ENDPOINT must not end with {self.git_api_endpoint_version}, use base GitLab URL instead")

    def _validate_webhook_config(self) -> None:
        """Validates webhook-related configuration."""
        if not self.webhook_secret_name:
            raise ValueError("WEBHOOK_SECRET_NAME environment variable is required")

    def _validate_s3_config(self) -> None:
        """Validates S3-related configuration."""
        if not self.artifacts_bucket:
            raise ValueError("ARTIFACTS_BUCKET environment variable is required")

        if not self.path_to_artifacts:
            raise ValueError("ARTIFACTS_PATH cannot be empty")

    def _validate_ai_config(self) -> None:
        """Validates AI-related configuration."""
        if not self.ai_api_token_name:
            raise ValueError("AI_API_TOKEN_NAME environment variable is required")

        if not self.llm_model:
            raise ValueError("LLM_MODEL environment variable is required")

        if not self.ai_api_endpoint:
            raise ValueError("AI_API_ENDPOINT environment variable is required")

        if not self.ai_api_endpoint.startswith(('http://', 'https://')):
            raise ValueError(
                f"AI_API_ENDPOINT must be a valid URL: {self.ai_api_endpoint}"
            )

    def _validate_dynamodb_config(self) -> None:
        """Validates DynamoDB-related configuration."""
        if not self.table_name:
            raise ValueError("DYNAMODB_TABLE_NAME environment variable is required")

    def _validate_logging_config(self) -> None:
        """Validates logging-related configuration."""
        valid_log_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
        if self.log_level not in valid_log_levels:
            raise ValueError(
                f"Invalid LOG_LEVEL: {self.log_level}. "
                f"Must be one of: {', '.join(valid_log_levels)}"
            )

    @cached_property
    def vcs_api_token(self) -> str:
        """
        Provides a cached property to retrieve the VCS API token securely from
        AWS SSM parameter store with decryption enabled. This avoids repeated
        calls to fetch the token and improves performance by caching the result.

        Returns:
            str: The decrypted VCS API token.

        Raises:
            botocore.exceptions.ClientError: If there are issues retrieving the
                parameter from AWS SSM, such as access restrictions or if the
                parameter does not exist.
        """
        ssm = boto3.client('ssm', config=self.boto3_config)
        response: Dict[str, Any] = ssm.get_parameter(
            Name=self.vcs_token_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']

    @cached_property
    def webhook_secret(self) -> str:
        ssm = boto3.client('ssm', config=self.boto3_config)
        response: Dict[str, Any] = ssm.get_parameter(
            Name=self.webhook_secret_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']

    @cached_property
    def ai_api_token(self) -> str:
        ssm = boto3.client('ssm', config=self.boto3_config)
        response: Dict[str, Any] = ssm.get_parameter(
            Name=self.ai_api_token_name,
            WithDecryption=True
        )
        return response['Parameter']['Value']


config: _ConfigLambda = _ConfigLambda()

__all__ = ['config']
