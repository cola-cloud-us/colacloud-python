"""Tests for custom exceptions."""

import pytest

from colacloud.exceptions import (
    APIConnectionError,
    AuthenticationError,
    ColaCloudError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestColaCloudError:
    """Tests for the base ColaCloudError exception."""

    def test_basic_error(self):
        error = ColaCloudError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"
        assert error.status_code is None
        assert error.response_body is None

    def test_error_with_status_code(self):
        error = ColaCloudError("Error", status_code=400)
        assert str(error) == "[400] Error"
        assert error.status_code == 400

    def test_error_with_response_body(self):
        body = {"error": {"code": "test_error", "message": "Test"}}
        error = ColaCloudError("Error", status_code=400, response_body=body)
        assert error.response_body == body

    def test_repr(self):
        error = ColaCloudError("Test error", status_code=500)
        assert "ColaCloudError" in repr(error)
        assert "Test error" in repr(error)
        assert "500" in repr(error)


class TestAuthenticationError:
    """Tests for AuthenticationError exception."""

    def test_default_message(self):
        error = AuthenticationError()
        assert "Authentication failed" in str(error)
        assert error.status_code == 401

    def test_custom_message(self):
        error = AuthenticationError(message="Invalid API key")
        assert str(error) == "[401] Invalid API key"

    def test_inheritance(self):
        error = AuthenticationError()
        assert isinstance(error, ColaCloudError)


class TestRateLimitError:
    """Tests for RateLimitError exception."""

    def test_default_message(self):
        error = RateLimitError()
        assert "Rate limit exceeded" in str(error)
        assert error.status_code == 429
        assert error.retry_after is None

    def test_with_retry_after(self):
        error = RateLimitError(retry_after=60)
        assert "retry after 60 seconds" in str(error)
        assert error.retry_after == 60

    def test_custom_message_with_retry(self):
        error = RateLimitError(message="Too many requests", retry_after=30)
        assert "[429] Too many requests" in str(error)
        assert "retry after 30 seconds" in str(error)


class TestNotFoundError:
    """Tests for NotFoundError exception."""

    def test_default_message(self):
        error = NotFoundError()
        assert "not found" in str(error).lower()
        assert error.status_code == 404

    def test_custom_message(self):
        error = NotFoundError(message="COLA 12345678 not found")
        assert str(error) == "[404] COLA 12345678 not found"


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_default_message(self):
        error = ValidationError()
        assert "Invalid" in str(error)
        assert error.status_code == 400

    def test_custom_message(self):
        error = ValidationError(message="Invalid date format")
        assert str(error) == "[400] Invalid date format"


class TestServerError:
    """Tests for ServerError exception."""

    def test_default_message(self):
        error = ServerError()
        assert "Server error" in str(error)
        assert error.status_code == 500

    def test_custom_status_code(self):
        error = ServerError(message="Service unavailable", status_code=503)
        assert str(error) == "[503] Service unavailable"
        assert error.status_code == 503


class TestAPIConnectionError:
    """Tests for APIConnectionError exception."""

    def test_default_message(self):
        error = APIConnectionError()
        assert "connect" in str(error).lower()
        assert error.status_code is None

    def test_custom_message(self):
        error = APIConnectionError(message="DNS resolution failed")
        assert str(error) == "DNS resolution failed"


class TestExceptionHierarchy:
    """Tests for exception hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        exceptions = [
            AuthenticationError(),
            RateLimitError(),
            NotFoundError(),
            ValidationError(),
            ServerError(),
            APIConnectionError(),
        ]

        for exc in exceptions:
            assert isinstance(exc, ColaCloudError)

    def test_catching_base_exception(self):
        """Verify that catching ColaCloudError catches all specific exceptions."""
        exceptions = [
            AuthenticationError(),
            RateLimitError(),
            NotFoundError(),
            ValidationError(),
            ServerError(),
            APIConnectionError(),
        ]

        for exc in exceptions:
            try:
                raise exc
            except ColaCloudError:
                pass  # Expected
            except Exception:
                pytest.fail(f"{type(exc).__name__} was not caught by ColaCloudError")
