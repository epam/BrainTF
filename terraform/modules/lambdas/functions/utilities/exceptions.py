class InvalidTokenException(Exception):
    """Exception raised when the provided token is invalid."""


class MissingTokenException(Exception):
    """Exception raised when the expected token is missing from the request."""


class MissingWebhookDataException(Exception):
    """Exception raised when required data is missing from the webhook payload."""


class MissingCommentContextException(Exception):
    """Exception indicating that a required command context in comments is missing."""


class InvalidEventMetadata(Exception):
    """Exception indicating that the event metadata is invalid."""


class HTTPException(Exception):
    """Exception for HTTP-related errors with status code and detail message."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"HTTP status {status_code}: {detail}")
