"""Custom exceptions for the COLA Cloud SDK."""

from typing import Any, Optional


class ColaCloudError(Exception):
    """Base exception for all COLA Cloud SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, status_code={self.status_code})"


class AuthenticationError(ColaCloudError):
    """Raised when API authentication fails (401 status code).

    This typically means:
    - The API key is missing
    - The API key is invalid or has been revoked
    - The API key has expired
    """

    def __init__(
        self,
        message: str = "Authentication failed. Check your API key.",
        status_code: int = 401,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_body)


class RateLimitError(ColaCloudError):
    """Raised when the API rate limit is exceeded (429 status code).

    This exception includes information about when you can retry.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please slow down your requests.",
        status_code: int = 429,
        response_body: Optional[dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, status_code, response_body)
        self.retry_after = retry_after

    def __str__(self) -> str:
        base = super().__str__()
        if self.retry_after:
            return f"{base} (retry after {self.retry_after} seconds)"
        return base


class NotFoundError(ColaCloudError):
    """Raised when a requested resource is not found (404 status code).

    This is raised when:
    - A COLA with the specified TTB ID doesn't exist
    - A permittee with the specified permit number doesn't exist
    - A barcode lookup returns no results
    """

    def __init__(
        self,
        message: str = "Resource not found.",
        status_code: int = 404,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_body)


class ValidationError(ColaCloudError):
    """Raised when request validation fails (400 status code).

    This is raised when:
    - Required parameters are missing
    - Parameter values are invalid
    """

    def __init__(
        self,
        message: str = "Invalid request parameters.",
        status_code: int = 400,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_body)


class ServerError(ColaCloudError):
    """Raised when the API returns a server error (5xx status codes).

    This indicates a problem on the server side.
    """

    def __init__(
        self,
        message: str = "Server error. Please try again later.",
        status_code: int = 500,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_body)


class APIConnectionError(ColaCloudError):
    """Raised when there's a network connection problem.

    This is raised when:
    - The API server is unreachable
    - DNS resolution fails
    - Connection times out
    """

    def __init__(
        self,
        message: str = "Failed to connect to the COLA Cloud API.",
        status_code: Optional[int] = None,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, response_body)
