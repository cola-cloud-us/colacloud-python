"""Tests for the synchronous ColaCloud client."""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from colacloud import (
    APIConnectionError,
    AuthenticationError,
    ColaCloud,
    ColaDetail,
    ColaSummary,
    NotFoundError,
    PermitteeDetail,
    PermitteeSummary,
    RateLimitError,
    ServerError,
    ValidationError,
)


class TestColaCloudClient:
    """Tests for ColaCloud client initialization and basic functionality."""

    def test_client_initialization(self):
        client = ColaCloud(api_key="test-key")
        assert client._api_key == "test-key"
        assert client._base_url == "https://app.colacloud.us/api/v1"
        assert client._timeout == 30.0
        client.close()

    def test_client_empty_api_key_raises_error(self):
        with pytest.raises(ValueError, match="api_key is required"):
            ColaCloud(api_key="")

    def test_client_whitespace_api_key_raises_error(self):
        with pytest.raises(ValueError, match="api_key is required"):
            ColaCloud(api_key="   ")

    def test_client_custom_base_url(self):
        client = ColaCloud(api_key="test-key", base_url="https://custom.api.com/v1/")
        assert client._base_url == "https://custom.api.com/v1"
        client.close()

    def test_client_custom_timeout(self):
        client = ColaCloud(api_key="test-key", timeout=60.0)
        assert client._timeout == 60.0
        client.close()

    def test_client_context_manager(self):
        with ColaCloud(api_key="test-key") as client:
            assert client._api_key == "test-key"

    def test_client_headers(self):
        client = ColaCloud(api_key="test-key")
        headers = client._get_headers()
        assert headers["X-API-Key"] == "test-key"
        assert headers["Accept"] == "application/json"
        assert "colacloud-python" in headers["User-Agent"]
        client.close()


class TestColasResource:
    """Tests for the COLAs resource."""

    def test_list_colas(self, httpx_mock: HTTPXMock, cola_list_response):
        httpx_mock.add_response(json=cola_list_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.colas.list(q="bourbon")

        assert len(response.data) == 1
        assert response.data[0].ttb_id == "12345678"
        assert response.pagination.total == 1

    def test_list_colas_with_filters(self, httpx_mock: HTTPXMock, cola_list_response):
        httpx_mock.add_response(json=cola_list_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.colas.list(
                q="whiskey",
                product_type="distilled spirits",
                origin="Kentucky",
                brand_name="Test",
                approval_date_from="2024-01-01",
                approval_date_to="2024-12-31",
                abv_min=35.0,
                abv_max=50.0,
                page=1,
                per_page=50,
            )

        request = httpx_mock.get_request()
        assert "q=whiskey" in str(request.url)
        assert "product_type=distilled" in str(request.url)
        assert "abv_min=35" in str(request.url)

    def test_get_cola(self, httpx_mock: HTTPXMock, cola_detail_response):
        httpx_mock.add_response(json=cola_detail_response)

        with ColaCloud(api_key="test-key") as client:
            cola = client.colas.get("12345678")

        assert isinstance(cola, ColaDetail)
        assert cola.ttb_id == "12345678"
        assert len(cola.images) == 2

    def test_get_cola_not_found(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=404,
            json={"error": {"message": "COLA 00000000 not found"}},
        )

        with ColaCloud(api_key="test-key") as client:
            with pytest.raises(NotFoundError) as exc_info:
                client.colas.get("00000000")

        assert "not found" in str(exc_info.value)


class TestPermitteesResource:
    """Tests for the permittees resource."""

    def test_list_permittees(self, httpx_mock: HTTPXMock, permittee_list_response):
        httpx_mock.add_response(json=permittee_list_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.permittees.list(state="KY")

        assert len(response.data) == 1
        assert response.data[0].permit_number == "KY-I-12345"

    def test_list_permittees_with_filters(self, httpx_mock: HTTPXMock, permittee_list_response):
        httpx_mock.add_response(json=permittee_list_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.permittees.list(
                q="distillery",
                state="CA",
                is_active=True,
                page=2,
                per_page=50,
            )

        request = httpx_mock.get_request()
        assert "q=distillery" in str(request.url)
        assert "state=CA" in str(request.url)
        assert "is_active=true" in str(request.url)

    def test_get_permittee(self, httpx_mock: HTTPXMock, permittee_detail_response):
        httpx_mock.add_response(json=permittee_detail_response)

        with ColaCloud(api_key="test-key") as client:
            permittee = client.permittees.get("KY-I-12345")

        assert isinstance(permittee, PermitteeDetail)
        assert permittee.permit_number == "KY-I-12345"
        assert len(permittee.recent_colas) == 1


class TestBarcodeResource:
    """Tests for the barcode resource."""

    def test_lookup_barcode(self, httpx_mock: HTTPXMock, barcode_lookup_response):
        httpx_mock.add_response(json=barcode_lookup_response)

        with ColaCloud(api_key="test-key") as client:
            result = client.barcode.lookup("012345678901")

        assert result.barcode_value == "012345678901"
        assert result.total_colas == 1

    def test_lookup_barcode_not_found(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=404,
            json={"error": {"message": "No COLAs found with barcode 000000000000"}},
        )

        with ColaCloud(api_key="test-key") as client:
            with pytest.raises(NotFoundError):
                client.barcode.lookup("000000000000")


class TestUsage:
    """Tests for the usage endpoint."""

    def test_get_usage(self, httpx_mock: HTTPXMock, usage_response):
        httpx_mock.add_response(json=usage_response)

        with ColaCloud(api_key="test-key") as client:
            usage = client.get_usage()

        assert usage.tier == "starter"
        assert usage.monthly_limit == 10000
        assert usage.requests_used == 500


class TestErrorHandling:
    """Tests for error handling."""

    def test_authentication_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=401,
            json={"error": {"message": "Invalid API key"}},
        )

        with ColaCloud(api_key="invalid-key") as client:
            with pytest.raises(AuthenticationError) as exc_info:
                client.colas.list()

        assert exc_info.value.status_code == 401

    def test_rate_limit_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=429,
            json={"error": {"message": "Rate limit exceeded"}},
            headers={"Retry-After": "60"},
        )

        with ColaCloud(api_key="test-key") as client:
            with pytest.raises(RateLimitError) as exc_info:
                client.colas.list()

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    def test_validation_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"message": "Invalid date format"}},
        )

        with ColaCloud(api_key="test-key") as client:
            with pytest.raises(ValidationError):
                client.colas.list(approval_date_from="invalid")

    def test_server_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=500,
            json={"error": {"message": "Internal server error"}},
        )

        with ColaCloud(api_key="test-key") as client:
            with pytest.raises(ServerError) as exc_info:
                client.colas.list()

        assert exc_info.value.status_code == 500


class TestRateLimitHeaders:
    """Tests for rate limit header parsing."""

    def test_rate_limit_info_parsed(self, httpx_mock: HTTPXMock, cola_list_response):
        httpx_mock.add_response(
            json=cola_list_response,
            headers={
                "X-RateLimit-Limit": "60",
                "X-RateLimit-Remaining": "55",
                "X-RateLimit-Reset": "1704067200",
                "X-RateLimit-Monthly-Limit": "10000",
                "X-RateLimit-Monthly-Remaining": "9500",
            },
        )

        with ColaCloud(api_key="test-key") as client:
            client.colas.list()
            rate_limit = client.rate_limit_info

        assert rate_limit is not None
        assert rate_limit.limit == 60
        assert rate_limit.remaining == 55
        assert rate_limit.monthly_limit == 10000

    def test_rate_limit_info_before_request(self):
        with ColaCloud(api_key="test-key") as client:
            assert client.rate_limit_info is None


class TestPagination:
    """Tests for pagination helpers."""

    def test_iterate_colas(self, httpx_mock: HTTPXMock, sample_cola_summary):
        # Page 1
        httpx_mock.add_response(
            json={
                "data": [sample_cola_summary],
                "pagination": {"page": 1, "per_page": 1, "total": 2, "pages": 2},
            }
        )
        # Page 2
        modified_cola = sample_cola_summary.copy()
        modified_cola["ttb_id"] = "87654321"
        httpx_mock.add_response(
            json={
                "data": [modified_cola],
                "pagination": {"page": 2, "per_page": 1, "total": 2, "pages": 2},
            }
        )

        with ColaCloud(api_key="test-key") as client:
            colas = list(client.colas.iterate(q="test", per_page=1))

        assert len(colas) == 2
        assert colas[0].ttb_id == "12345678"
        assert colas[1].ttb_id == "87654321"

    def test_iterate_permittees(self, httpx_mock: HTTPXMock, sample_permittee_summary):
        httpx_mock.add_response(
            json={
                "data": [sample_permittee_summary],
                "pagination": {"page": 1, "per_page": 1, "total": 1, "pages": 1},
            }
        )

        with ColaCloud(api_key="test-key") as client:
            permittees = list(client.permittees.iterate(state="KY", per_page=1))

        assert len(permittees) == 1
        assert permittees[0].permit_number == "KY-I-12345"
