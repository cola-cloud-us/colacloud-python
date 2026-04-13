"""Tests for the asynchronous AsyncColaCloud client."""

import pytest
from pytest_httpx import HTTPXMock

from colacloud import (
    AsyncColaCloud,
    AuthenticationError,
    ColaDetail,
    NotFoundError,
    PermitteeDetail,
    RateLimitError,
    ReferenceDataResponse,
)


@pytest.mark.asyncio
class TestAsyncColaCloudClient:
    """Tests for AsyncColaCloud client initialization."""

    async def test_client_initialization(self):
        client = AsyncColaCloud(api_key="test-key")
        assert client._api_key == "test-key"
        assert client._base_url == "https://app.colacloud.us/api/v1"
        await client.close()

    async def test_client_empty_api_key_raises_error(self):
        with pytest.raises(ValueError, match="api_key is required"):
            AsyncColaCloud(api_key="")

    async def test_client_whitespace_api_key_raises_error(self):
        with pytest.raises(ValueError, match="api_key is required"):
            AsyncColaCloud(api_key="   ")

    async def test_client_context_manager(self):
        async with AsyncColaCloud(api_key="test-key") as client:
            assert client._api_key == "test-key"


@pytest.mark.asyncio
class TestAsyncColasResource:
    """Tests for the async COLAs resource."""

    async def test_list_colas(self, httpx_mock: HTTPXMock, cola_list_response):
        httpx_mock.add_response(json=cola_list_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            response = await client.colas.list(q="bourbon")

        assert len(response.data) == 1
        assert response.data[0].ttb_id == "12345678"

    async def test_get_cola(self, httpx_mock: HTTPXMock, cola_detail_response):
        httpx_mock.add_response(json=cola_detail_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            cola = await client.colas.get("12345678")

        assert isinstance(cola, ColaDetail)
        assert cola.ttb_id == "12345678"

    async def test_get_cola_not_found(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=404,
            json={"error": {"message": "COLA 00000000 not found"}},
        )

        async with AsyncColaCloud(api_key="test-key") as client:
            with pytest.raises(NotFoundError):
                await client.colas.get("00000000")


@pytest.mark.asyncio
class TestAsyncPermitteesResource:
    """Tests for the async permittees resource."""

    async def test_list_permittees(self, httpx_mock: HTTPXMock, permittee_list_response):
        httpx_mock.add_response(json=permittee_list_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            response = await client.permittees.list(state="KY")

        assert len(response.data) == 1
        assert response.data[0].permit_number == "KY-I-12345"

    async def test_get_permittee(self, httpx_mock: HTTPXMock, permittee_detail_response):
        httpx_mock.add_response(json=permittee_detail_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            permittee = await client.permittees.get("KY-I-12345")

        assert isinstance(permittee, PermitteeDetail)
        assert permittee.permit_number == "KY-I-12345"


@pytest.mark.asyncio
class TestAsyncBarcodeResource:
    """Tests for the async barcode resource."""

    async def test_lookup_barcode(self, httpx_mock: HTTPXMock, barcode_lookup_response):
        httpx_mock.add_response(json=barcode_lookup_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            result = await client.barcode.lookup("012345678901")

        assert result.barcode_value == "012345678901"
        assert result.total_colas == 1


@pytest.mark.asyncio
class TestAsyncUsage:
    """Tests for the async usage endpoint."""

    async def test_get_usage(self, httpx_mock: HTTPXMock, usage_response):
        httpx_mock.add_response(json=usage_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            usage = await client.get_usage()

        assert usage.tier == "starter"
        assert usage.detail_views.used == 100


@pytest.mark.asyncio
class TestAsyncErrorHandling:
    """Tests for async error handling."""

    async def test_authentication_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=401,
            json={"error": {"message": "Invalid API key"}},
        )

        async with AsyncColaCloud(api_key="invalid-key") as client:
            with pytest.raises(AuthenticationError):
                await client.colas.list()

    async def test_rate_limit_error(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=429,
            json={"error": {"message": "Rate limit exceeded"}},
            headers={"Retry-After": "30"},
        )

        async with AsyncColaCloud(api_key="test-key") as client:
            with pytest.raises(RateLimitError) as exc_info:
                await client.colas.list()

        assert exc_info.value.retry_after == 30


@pytest.mark.asyncio
class TestAsyncPagination:
    """Tests for async pagination helpers."""

    async def test_iterate_colas(self, httpx_mock: HTTPXMock, sample_cola_summary):
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

        async with AsyncColaCloud(api_key="test-key") as client:
            colas = []
            async for cola in client.colas.iterate(q="test", per_page=1):
                colas.append(cola)

        assert len(colas) == 2
        assert colas[0].ttb_id == "12345678"
        assert colas[1].ttb_id == "87654321"

    async def test_iterate_permittees(self, httpx_mock: HTTPXMock, sample_permittee_summary):
        httpx_mock.add_response(
            json={
                "data": [sample_permittee_summary],
                "pagination": {"page": 1, "per_page": 1, "total": 1, "pages": 1},
            }
        )

        async with AsyncColaCloud(api_key="test-key") as client:
            permittees = []
            async for permittee in client.permittees.iterate(state="KY", per_page=1):
                permittees.append(permittee)

        assert len(permittees) == 1
        assert permittees[0].permit_number == "KY-I-12345"


@pytest.mark.asyncio
class TestAsyncQuotaHeaders:
    """Tests for async quota header parsing."""

    async def test_detail_view_quota_parsed(self, httpx_mock: HTTPXMock, cola_list_response):
        httpx_mock.add_response(
            json=cola_list_response,
            headers={
                "X-Detail-Views-Limit": "200",
                "X-Detail-Views-Remaining": "150",
                "X-Quota-Reset": "1704067200",
            },
        )

        async with AsyncColaCloud(api_key="test-key") as client:
            await client.colas.list()
            quota = client.quota_info

        assert quota is not None
        assert quota.meter == "detail_views"
        assert quota.limit == 200
        assert quota.remaining == 150


@pytest.mark.asyncio
class TestAsyncProcessingTimesResource:
    """Tests for the async processing times resource."""

    async def test_list_processing_times(self, httpx_mock: HTTPXMock, processing_times_response):
        httpx_mock.add_response(json=processing_times_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            response = await client.processing_times.list()

        assert isinstance(response, ReferenceDataResponse)
        assert len(response.data) == 1
        assert response.meta.total == 1

    async def test_list_processing_times_with_commodity(
        self, httpx_mock: HTTPXMock, processing_times_response
    ):
        httpx_mock.add_response(json=processing_times_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            await client.processing_times.list(commodity="Wine")

        request = httpx_mock.get_request()
        assert "commodity=Wine" in str(request.url)

    async def test_formula_processing_times(
        self, httpx_mock: HTTPXMock, processing_times_formula_response
    ):
        httpx_mock.add_response(json=processing_times_formula_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            response = await client.processing_times.formula()

        assert len(response.data) == 1

    async def test_formula_processing_times_with_filters(
        self, httpx_mock: HTTPXMock, processing_times_formula_response
    ):
        httpx_mock.add_response(json=processing_times_formula_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            await client.processing_times.formula(
                formula_type="distilled spirits", commodity="Whiskey"
            )

        request = httpx_mock.get_request()
        assert "formula_type=distilled" in str(request.url)
        assert "commodity=Whiskey" in str(request.url)

    async def test_registration_processing_times(
        self, httpx_mock: HTTPXMock, processing_times_registration_response
    ):
        httpx_mock.add_response(json=processing_times_registration_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            response = await client.processing_times.registration()

        assert len(response.data) == 1

    async def test_registration_processing_times_with_filters(
        self, httpx_mock: HTTPXMock, processing_times_registration_response
    ):
        httpx_mock.add_response(json=processing_times_registration_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            await client.processing_times.registration(category="Beverage", application_type="new")

        request = httpx_mock.get_request()
        assert "category=Beverage" in str(request.url)
        assert "application_type=new" in str(request.url)


@pytest.mark.asyncio
class TestAsyncProductionReportsResource:
    """Tests for the async production reports resource."""

    async def test_list_production_reports(
        self, httpx_mock: HTTPXMock, production_reports_response
    ):
        httpx_mock.add_response(json=production_reports_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            response = await client.production_reports.list()

        assert isinstance(response, ReferenceDataResponse)
        assert len(response.data) == 1
        assert response.meta.total == 1
        assert response.meta.has_more is False

    async def test_list_production_reports_with_filters(
        self, httpx_mock: HTTPXMock, production_reports_response
    ):
        httpx_mock.add_response(json=production_reports_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            await client.production_reports.list(
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


@pytest.mark.asyncio
class TestAsyncAVAsResource:
    """Tests for the async AVAs resource."""

    async def test_list_avas(self, httpx_mock: HTTPXMock, avas_response):
        httpx_mock.add_response(json=avas_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            response = await client.avas.list()

        assert isinstance(response, ReferenceDataResponse)
        assert len(response.data) == 1
        assert response.meta.total == 1

    async def test_list_avas_with_filters(self, httpx_mock: HTTPXMock, avas_response):
        httpx_mock.add_response(json=avas_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            await client.avas.list(state="CA", q="Napa")

        request = httpx_mock.get_request()
        assert "state=CA" in str(request.url)
        assert "q=Napa" in str(request.url)

    async def test_get_ava(self, httpx_mock: HTTPXMock, ava_detail_response):
        httpx_mock.add_response(json=ava_detail_response)

        async with AsyncColaCloud(api_key="test-key") as client:
            ava = await client.avas.get("napa-valley")

        assert ava["name"] == "Napa Valley"
        assert ava["state"] == "CA"

    async def test_get_ava_not_found(self, httpx_mock: HTTPXMock):
        httpx_mock.add_response(
            status_code=404,
            json={"error": {"message": "AVA not-real not found"}},
        )

        async with AsyncColaCloud(api_key="test-key") as client:
            with pytest.raises(NotFoundError):
                await client.avas.get("not-real")
