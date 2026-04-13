"""Tests for the synchronous ColaCloud client."""

import pytest
from pytest_httpx import HTTPXMock

from colacloud import (
    AuthenticationError,
    ColaCloud,
    ColaDetail,
    NotFoundError,
    PermitteeDetail,
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
            client.colas.list(
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

        with ColaCloud(api_key="test-key") as client, pytest.raises(NotFoundError) as exc_info:
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
            client.permittees.list(
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

        with ColaCloud(api_key="test-key") as client, pytest.raises(NotFoundError):
            client.barcode.lookup("000000000000")


class TestUsage:
    """Tests for the usage endpoint."""

    def test_get_usage(self, httpx_mock: HTTPXMock, usage_response):
        httpx_mock.add_response(json=usage_response)

        with ColaCloud(api_key="test-key") as client:
            usage = client.get_usage()

        assert usage.tier == "starter"
        assert usage.detail_views.used == 100
        assert usage.list_records.limit == 100000


class TestErrorHandling:
    """Tests for error handling."""

    def test_authentication_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=401,
            json={"error": {"message": "Invalid API key"}},
        )

        with (
            ColaCloud(api_key="invalid-key") as client,
            pytest.raises(AuthenticationError) as exc_info,
        ):
            client.colas.list()

        assert exc_info.value.status_code == 401

    def test_rate_limit_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=429,
            json={"error": {"message": "Rate limit exceeded"}},
            headers={"Retry-After": "60"},
        )

        with ColaCloud(api_key="test-key") as client, pytest.raises(RateLimitError) as exc_info:
            client.colas.list()

        assert exc_info.value.status_code == 429
        assert exc_info.value.retry_after == 60

    def test_validation_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=400,
            json={"error": {"message": "Invalid date format"}},
        )

        with ColaCloud(api_key="test-key") as client, pytest.raises(ValidationError):
            client.colas.list(approval_date_from="invalid")

    def test_server_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=500,
            json={"error": {"message": "Internal server error"}},
        )

        with ColaCloud(api_key="test-key") as client, pytest.raises(ServerError) as exc_info:
            client.colas.list()

        assert exc_info.value.status_code == 500


class TestQuotaHeaders:
    """Tests for quota header parsing."""

    def test_detail_view_quota_parsed(self, httpx_mock: HTTPXMock, cola_list_response):
        httpx_mock.add_response(
            json=cola_list_response,
            headers={
                "X-Detail-Views-Limit": "200",
                "X-Detail-Views-Remaining": "150",
                "X-Quota-Reset": "1704067200",
            },
        )

        with ColaCloud(api_key="test-key") as client:
            client.colas.list()
            quota = client.quota_info

        assert quota is not None
        assert quota.meter == "detail_views"
        assert quota.limit == 200
        assert quota.remaining == 150
        assert quota.reset == 1704067200

    def test_list_record_quota_parsed(self, httpx_mock: HTTPXMock, cola_list_response):
        httpx_mock.add_response(
            json=cola_list_response,
            headers={
                "X-List-Records-Limit": "10000",
                "X-List-Records-Remaining": "9500",
                "X-Quota-Reset": "1704067200",
            },
        )

        with ColaCloud(api_key="test-key") as client:
            client.colas.list()
            quota = client.quota_info

        assert quota is not None
        assert quota.meter == "list_records"
        assert quota.limit == 10000
        assert quota.remaining == 9500

    def test_quota_info_before_request(self):
        with ColaCloud(api_key="test-key") as client:
            assert client.quota_info is None


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


class TestProcessingTimesResource:
    """Tests for the processing times resource."""

    def test_list_processing_times(self, httpx_mock: HTTPXMock, processing_times_response):
        httpx_mock.add_response(json=processing_times_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.processing_times.list()

        assert len(response.data) == 1
        assert response.meta.total == 1

    def test_list_processing_times_with_commodity(
        self, httpx_mock: HTTPXMock, processing_times_response
    ):
        httpx_mock.add_response(json=processing_times_response)

        with ColaCloud(api_key="test-key") as client:
            client.processing_times.list(commodity="Wine")

        request = httpx_mock.get_request()
        assert "commodity=Wine" in str(request.url)

    def test_formula_processing_times(
        self, httpx_mock: HTTPXMock, processing_times_formula_response
    ):
        httpx_mock.add_response(json=processing_times_formula_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.processing_times.formula()

        assert len(response.data) == 1
        assert response.meta.total == 1

    def test_formula_processing_times_with_filters(
        self, httpx_mock: HTTPXMock, processing_times_formula_response
    ):
        httpx_mock.add_response(json=processing_times_formula_response)

        with ColaCloud(api_key="test-key") as client:
            client.processing_times.formula(formula_type="distilled spirits", commodity="Whiskey")

        request = httpx_mock.get_request()
        assert "formula_type=distilled" in str(request.url)
        assert "commodity=Whiskey" in str(request.url)

    def test_registration_processing_times(
        self, httpx_mock: HTTPXMock, processing_times_registration_response
    ):
        httpx_mock.add_response(json=processing_times_registration_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.processing_times.registration()

        assert len(response.data) == 1
        assert response.meta.total == 1

    def test_registration_processing_times_with_filters(
        self, httpx_mock: HTTPXMock, processing_times_registration_response
    ):
        httpx_mock.add_response(json=processing_times_registration_response)

        with ColaCloud(api_key="test-key") as client:
            client.processing_times.registration(category="Beverage", application_type="new")

        request = httpx_mock.get_request()
        assert "category=Beverage" in str(request.url)
        assert "application_type=new" in str(request.url)


class TestProductionReportsResource:
    """Tests for the production reports resource."""

    def test_list_production_reports(self, httpx_mock: HTTPXMock, production_reports_response):
        httpx_mock.add_response(json=production_reports_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.production_reports.list()

        assert len(response.data) == 1
        assert response.meta.total == 1
        assert response.meta.has_more is False

    def test_list_production_reports_with_filters(
        self, httpx_mock: HTTPXMock, production_reports_response
    ):
        httpx_mock.add_response(json=production_reports_response)

        with ColaCloud(api_key="test-key") as client:
            client.production_reports.list(
                commodity="Wine",
                year=2024,
                month=1,
                report_type="production",
                statistical_group="Table Wine",
                page=2,
                per_page=50,
            )

        request = httpx_mock.get_request()
        assert "commodity=Wine" in str(request.url)
        assert "year=2024" in str(request.url)
        assert "month=1" in str(request.url)
        assert "report_type=production" in str(request.url)
        assert "page=2" in str(request.url)
        assert "per_page=50" in str(request.url)

    def test_list_production_reports_caps_per_page(
        self, httpx_mock: HTTPXMock, production_reports_response
    ):
        httpx_mock.add_response(json=production_reports_response)

        with ColaCloud(api_key="test-key") as client:
            client.production_reports.list(per_page=500)

        request = httpx_mock.get_request()
        assert "per_page=100" in str(request.url)


class TestAVAsResource:
    """Tests for the AVAs resource."""

    def test_list_avas(self, httpx_mock: HTTPXMock, avas_response):
        httpx_mock.add_response(json=avas_response)

        with ColaCloud(api_key="test-key") as client:
            response = client.avas.list()

        assert len(response.data) == 1
        assert response.meta.total == 1

    def test_list_avas_with_filters(self, httpx_mock: HTTPXMock, avas_response):
        httpx_mock.add_response(json=avas_response)

        with ColaCloud(api_key="test-key") as client:
            client.avas.list(state="CA", q="Napa")

        request = httpx_mock.get_request()
        assert "state=CA" in str(request.url)
        assert "q=Napa" in str(request.url)

    def test_get_ava(self, httpx_mock: HTTPXMock, ava_detail_response):
        httpx_mock.add_response(json=ava_detail_response)

        with ColaCloud(api_key="test-key") as client:
            ava = client.avas.get("napa-valley")

        assert ava["name"] == "Napa Valley"
        assert ava["state"] == "CA"

    def test_get_ava_not_found(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=404,
            json={"error": {"message": "AVA not-real not found"}},
        )

        with ColaCloud(api_key="test-key") as client, pytest.raises(NotFoundError):
            client.avas.get("not-real")
