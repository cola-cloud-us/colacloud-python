"""Asynchronous client for the COLA Cloud API."""

from typing import Any, cast

import httpx

from ._version import __version__
from .exceptions import (
    APIConnectionError,
    AuthenticationError,
    ColaCloudError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)
from .models import (
    BarcodeLookupResponse,
    BarcodeLookupResult,
    ColaDetail,
    ColaDetailResponse,
    ColaListResponse,
    ColaSummary,
    Pagination,
    PermitteeDetail,
    PermitteeDetailResponse,
    PermitteeListResponse,
    PermitteeSummary,
    QuotaInfo,
    ReferenceDataDetailResponse,
    ReferenceDataResponse,
    UsageInfo,
    UsageResponse,
)
from .pagination import AsyncPaginatedIterator

DEFAULT_BASE_URL = "https://app.colacloud.us/api/v1"
DEFAULT_TIMEOUT = 30.0


class AsyncColasResource:
    """Async resource for interacting with COLA endpoints."""

    def __init__(self, client: "AsyncColaCloud") -> None:
        self._client = client

    async def list(
        self,
        *,
        q: str | None = None,
        product_type: str | None = None,
        category: str | None = None,
        derived_subcategory: str | None = None,
        origin: str | None = None,
        domestic_or_imported: str | None = None,
        status: str | None = None,
        brand_name: str | None = None,
        permit_number: str | None = None,
        barcode_value: str | None = None,
        approval_date_from: str | None = None,
        approval_date_to: str | None = None,
        abv_min: float | None = None,
        abv_max: float | None = None,
        volume_unit: str | None = None,
        volume_min: float | None = None,
        volume_max: float | None = None,
        container_type: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> ColaListResponse:
        """List and search COLAs with pagination.

        Args:
            q: Text search query, including applicant/company names.
            product_type: Filter by one or more TTB product types.
            category: Filter by derived top-level category.
            derived_subcategory: Filter by derived category path prefix.
            origin: Filter by country/state of origin.
            domestic_or_imported: Filter by domestic/imported origin.
            status: Filter by application status.
            brand_name: Filter by brand name (partial match).
            permit_number: Filter by exact permit number.
            barcode_value: Filter by exact main barcode value.
            approval_date_from: Filter by minimum approval date (YYYY-MM-DD).
            approval_date_to: Filter by maximum approval date (YYYY-MM-DD).
            abv_min: Filter by minimum ABV percentage.
            abv_max: Filter by maximum ABV percentage.
            volume_unit: Filter by volume unit. Required with volume_min/volume_max.
            volume_min: Filter by minimum package volume.
            volume_max: Filter by maximum package volume.
            container_type: Filter by one or more derived container types.
            page: Page number (default: 1).
            per_page: Results per page (default: 20, max: 100).

        Returns:
            ColaListResponse containing data and pagination info.

        Raises:
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
            ValidationError: If request parameters are invalid.
            ColaCloudError: For other API errors.
        """
        params: dict[str, Any] = {"page": page, "per_page": min(per_page, 100)}

        if q:
            params["q"] = q
        if product_type:
            params["product_type"] = product_type
        if category:
            params["category"] = category
        if derived_subcategory:
            params["derived_subcategory"] = derived_subcategory
        if origin:
            params["origin"] = origin
        if domestic_or_imported:
            params["domestic_or_imported"] = domestic_or_imported
        if status:
            params["status"] = status
        if brand_name:
            params["brand_name"] = brand_name
        if permit_number:
            params["permit_number"] = permit_number
        if barcode_value:
            params["barcode_value"] = barcode_value
        if approval_date_from:
            params["approval_date_from"] = approval_date_from
        if approval_date_to:
            params["approval_date_to"] = approval_date_to
        if abv_min is not None:
            params["abv_min"] = abv_min
        if abv_max is not None:
            params["abv_max"] = abv_max
        if volume_unit:
            params["volume_unit"] = volume_unit
        if volume_min is not None:
            params["volume_min"] = volume_min
        if volume_max is not None:
            params["volume_max"] = volume_max
        if container_type:
            params["container_type"] = container_type

        data = await self._client._request("GET", "/colas", params=params)
        return ColaListResponse.model_validate(data)

    async def get(self, ttb_id: str) -> ColaDetail:
        """Get a single COLA by TTB ID.

        Args:
            ttb_id: The TTB ID of the COLA (e.g., "12345678").

        Returns:
            ColaDetail with full information including images and barcodes.

        Raises:
            NotFoundError: If the COLA doesn't exist.
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
            ColaCloudError: For other API errors.
        """
        data = await self._client._request("GET", f"/colas/{ttb_id}")
        response = ColaDetailResponse.model_validate(data)
        return response.data

    def iterate(
        self,
        *,
        q: str | None = None,
        product_type: str | None = None,
        category: str | None = None,
        derived_subcategory: str | None = None,
        origin: str | None = None,
        domestic_or_imported: str | None = None,
        status: str | None = None,
        brand_name: str | None = None,
        permit_number: str | None = None,
        barcode_value: str | None = None,
        approval_date_from: str | None = None,
        approval_date_to: str | None = None,
        abv_min: float | None = None,
        abv_max: float | None = None,
        volume_unit: str | None = None,
        volume_min: float | None = None,
        volume_max: float | None = None,
        container_type: str | None = None,
        per_page: int = 100,
    ) -> AsyncPaginatedIterator[ColaSummary]:
        """Iterate through all matching COLAs with automatic pagination.

        This method returns an async iterator that automatically fetches additional
        pages as needed.

        Args:
            q: Text search query, including applicant/company names.
            product_type: Filter by one or more TTB product types.
            category: Filter by derived top-level category.
            derived_subcategory: Filter by derived category path prefix.
            origin: Filter by country/state of origin.
            domestic_or_imported: Filter by domestic/imported origin.
            status: Filter by application status.
            brand_name: Filter by brand name (partial match).
            permit_number: Filter by exact permit number.
            barcode_value: Filter by exact main barcode value.
            approval_date_from: Filter by minimum approval date (YYYY-MM-DD).
            approval_date_to: Filter by maximum approval date (YYYY-MM-DD).
            abv_min: Filter by minimum ABV percentage.
            abv_max: Filter by maximum ABV percentage.
            volume_unit: Filter by volume unit. Required with volume_min/volume_max.
            volume_min: Filter by minimum package volume.
            volume_max: Filter by maximum package volume.
            container_type: Filter by one or more derived container types.
            per_page: Results per page (default: 100, max: 100).

        Yields:
            ColaSummary objects for each matching COLA.

        Example:
            ```python
            async for cola in client.colas.iterate(q="bourbon"):
                print(f"{cola.brand_name}: {cola.product_name}")
            ```
        """

        async def fetch_page(page: int) -> tuple[list[ColaSummary], Pagination]:
            response = await self.list(
                q=q,
                product_type=product_type,
                category=category,
                derived_subcategory=derived_subcategory,
                origin=origin,
                domestic_or_imported=domestic_or_imported,
                status=status,
                brand_name=brand_name,
                permit_number=permit_number,
                barcode_value=barcode_value,
                approval_date_from=approval_date_from,
                approval_date_to=approval_date_to,
                abv_min=abv_min,
                abv_max=abv_max,
                volume_unit=volume_unit,
                volume_min=volume_min,
                volume_max=volume_max,
                container_type=container_type,
                page=page,
                per_page=per_page,
            )
            return response.data, response.pagination

        return AsyncPaginatedIterator(fetch_page)


class AsyncPermitteesResource:
    """Async resource for interacting with permittee endpoints."""

    def __init__(self, client: "AsyncColaCloud") -> None:
        self._client = client

    async def list(
        self,
        *,
        q: str | None = None,
        state: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> PermitteeListResponse:
        """List and search permittees with pagination.

        Args:
            q: Search by company name (partial match).
            state: Filter by state (two-letter code, e.g., "CA", "NY").
            is_active: Filter by active status.
            page: Page number (default: 1).
            per_page: Results per page (default: 20, max: 100).

        Returns:
            PermitteeListResponse containing data and pagination info.

        Raises:
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
            ValidationError: If request parameters are invalid.
            ColaCloudError: For other API errors.
        """
        params: dict[str, Any] = {"page": page, "per_page": min(per_page, 100)}

        if q:
            params["q"] = q
        if state:
            params["state"] = state
        if is_active is not None:
            params["is_active"] = "true" if is_active else "false"

        data = await self._client._request("GET", "/permittees", params=params)
        return PermitteeListResponse.model_validate(data)

    async def get(self, permit_number: str) -> PermitteeDetail:
        """Get a single permittee by permit number.

        Args:
            permit_number: The permit number (e.g., "NY-I-12345").

        Returns:
            PermitteeDetail with full information and recent COLAs.

        Raises:
            NotFoundError: If the permittee doesn't exist.
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
            ColaCloudError: For other API errors.
        """
        data = await self._client._request("GET", f"/permittees/{permit_number}")
        response = PermitteeDetailResponse.model_validate(data)
        return response.data

    def iterate(
        self,
        *,
        q: str | None = None,
        state: str | None = None,
        is_active: bool | None = None,
        per_page: int = 100,
    ) -> AsyncPaginatedIterator[PermitteeSummary]:
        """Iterate through all matching permittees with automatic pagination.

        This method returns an async iterator that automatically fetches additional
        pages as needed.

        Args:
            q: Search by company name (partial match).
            state: Filter by state (two-letter code).
            is_active: Filter by active status.
            per_page: Results per page (default: 100, max: 100).

        Yields:
            PermitteeSummary objects for each matching permittee.

        Example:
            ```python
            async for permittee in client.permittees.iterate(state="CA"):
                print(f"{permittee.company_name}: {permittee.colas} COLAs")
            ```
        """

        async def fetch_page(page: int) -> tuple[list[PermitteeSummary], Pagination]:
            response = await self.list(
                q=q,
                state=state,
                is_active=is_active,
                page=page,
                per_page=per_page,
            )
            return response.data, response.pagination

        return AsyncPaginatedIterator(fetch_page)


class AsyncBarcodeResource:
    """Async resource for barcode lookups."""

    def __init__(self, client: "AsyncColaCloud") -> None:
        self._client = client

    async def lookup(self, barcode_value: str) -> BarcodeLookupResult:
        """Look up COLAs by barcode (UPC, EAN, etc.).

        Args:
            barcode_value: The barcode value to look up.

        Returns:
            BarcodeLookupResult with matching COLAs.

        Raises:
            NotFoundError: If no COLAs are found with this barcode.
            AuthenticationError: If the API key is invalid.
            RateLimitError: If the rate limit is exceeded.
            ColaCloudError: For other API errors.
        """
        data = await self._client._request("GET", f"/barcode/{barcode_value}")
        response = BarcodeLookupResponse.model_validate(data)
        return response.data


class AsyncProcessingTimesResource:
    """Async resource for interacting with processing times endpoints."""

    def __init__(self, client: "AsyncColaCloud") -> None:
        self._client = client

    async def list(
        self,
        *,
        commodity: str | None = None,
    ) -> ReferenceDataResponse:
        """Get COLA processing times.

        Args:
            commodity: Filter by commodity type.

        Returns:
            ReferenceDataResponse containing data and meta info.

        Raises:
            AuthenticationError: If the API key is invalid.
            ColaCloudError: For other API errors.
        """
        params: dict[str, Any] = {}

        if commodity:
            params["commodity"] = commodity

        data = await self._client._request("GET", "/processing-times", params=params)
        return ReferenceDataResponse.model_validate(data)

    async def formula(
        self,
        *,
        formula_type: str | None = None,
        commodity: str | None = None,
    ) -> ReferenceDataResponse:
        """Get formula processing times.

        Args:
            formula_type: Filter by formula type.
            commodity: Filter by commodity type.

        Returns:
            ReferenceDataResponse containing data and meta info.

        Raises:
            AuthenticationError: If the API key is invalid.
            ColaCloudError: For other API errors.
        """
        params: dict[str, Any] = {}

        if formula_type:
            params["formula_type"] = formula_type
        if commodity:
            params["commodity"] = commodity

        data = await self._client._request("GET", "/processing-times/formula", params=params)
        return ReferenceDataResponse.model_validate(data)

    async def registration(
        self,
        *,
        category: str | None = None,
        application_type: str | None = None,
    ) -> ReferenceDataResponse:
        """Get registration processing times.

        Args:
            category: Filter by category.
            application_type: Filter by application type.

        Returns:
            ReferenceDataResponse containing data and meta info.

        Raises:
            AuthenticationError: If the API key is invalid.
            ColaCloudError: For other API errors.
        """
        params: dict[str, Any] = {}

        if category:
            params["category"] = category
        if application_type:
            params["application_type"] = application_type

        data = await self._client._request("GET", "/processing-times/registration", params=params)
        return ReferenceDataResponse.model_validate(data)


class AsyncProductionReportsResource:
    """Async resource for interacting with production reports endpoints."""

    def __init__(self, client: "AsyncColaCloud") -> None:
        self._client = client

    async def list(
        self,
        *,
        commodity: str | None = None,
        year: int | None = None,
        month: int | None = None,
        report_type: str | None = None,
        statistical_group: str | None = None,
        page: int = 1,
        per_page: int = 100,
    ) -> ReferenceDataResponse:
        """Get production reports.

        Args:
            commodity: Filter by commodity type.
            year: Filter by year.
            month: Filter by month.
            report_type: Filter by report type.
            statistical_group: Filter by statistical group.
            page: Page number (default: 1).
            per_page: Results per page (default: 100, max: 100).

        Returns:
            ReferenceDataResponse containing data and meta info.

        Raises:
            AuthenticationError: If the API key is invalid.
            ColaCloudError: For other API errors.
        """
        params: dict[str, Any] = {"page": page, "per_page": min(per_page, 100)}

        if commodity:
            params["commodity"] = commodity
        if year is not None:
            params["year"] = year
        if month is not None:
            params["month"] = month
        if report_type:
            params["report_type"] = report_type
        if statistical_group:
            params["statistical_group"] = statistical_group

        data = await self._client._request("GET", "/production-reports", params=params)
        return ReferenceDataResponse.model_validate(data)


class AsyncAVAsResource:
    """Async resource for interacting with AVA endpoints."""

    def __init__(self, client: "AsyncColaCloud") -> None:
        self._client = client

    async def list(
        self,
        *,
        state: str | None = None,
        q: str | None = None,
    ) -> ReferenceDataResponse:
        """List American Viticultural Areas.

        Args:
            state: Filter by state (two-letter code, e.g., "CA", "OR").
            q: Search by AVA name (partial match).

        Returns:
            ReferenceDataResponse containing data and meta info.

        Raises:
            AuthenticationError: If the API key is invalid.
            ColaCloudError: For other API errors.
        """
        params: dict[str, Any] = {}

        if state:
            params["state"] = state
        if q:
            params["q"] = q

        data = await self._client._request("GET", "/avas", params=params)
        return ReferenceDataResponse.model_validate(data)

    async def get(self, ava_id: str) -> dict[str, Any]:
        """Get a single AVA by ID.

        Args:
            ava_id: The AVA identifier.

        Returns:
            Dict with AVA details.

        Raises:
            NotFoundError: If the AVA doesn't exist.
            AuthenticationError: If the API key is invalid.
            ColaCloudError: For other API errors.
        """
        data = await self._client._request("GET", f"/avas/{ava_id}")
        response = ReferenceDataDetailResponse.model_validate(data)
        return response.data


class AsyncColaCloud:
    """Asynchronous client for the COLA Cloud API.

    Example:
        ```python
        import asyncio
        from colacloud import AsyncColaCloud

        async def main():
            async with AsyncColaCloud(api_key="your-api-key") as client:
                # Search COLAs
                colas = await client.colas.list(q="bourbon", product_type="distilled spirits")
                for cola in colas.data:
                    print(f"{cola.brand_name}: {cola.product_name}")

                # Get a single COLA
                cola = await client.colas.get("12345678")

                # Iterate through all results
                async for cola in client.colas.iterate(q="whiskey"):
                    print(cola.ttb_id)

                # Look up by barcode
                result = await client.barcode.lookup("012345678901")
                print(f"Found {result.total_colas} COLAs")

                # Check API usage
                usage = await client.get_usage()
                print(f"Detail views: {usage.detail_views.used} / {usage.detail_views.limit}")

        asyncio.run(main())
        ```

    Args:
        api_key: Your COLA Cloud API key.
        base_url: Base URL for the API (default: https://app.colacloud.us/api/v1).
        timeout: Request timeout in seconds (default: 30).
        http_client: Optional custom httpx.AsyncClient instance.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required and cannot be empty")
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

        if http_client:
            self._client = http_client
            self._owns_client = False
        else:
            self._client = httpx.AsyncClient(timeout=timeout)
            self._owns_client = True

        self._last_quota_info: QuotaInfo | None = None

        # Initialize resource classes
        self.colas = AsyncColasResource(self)
        self.permittees = AsyncPermitteesResource(self)
        self.barcode = AsyncBarcodeResource(self)
        self.processing_times = AsyncProcessingTimesResource(self)
        self.production_reports = AsyncProductionReportsResource(self)
        self.avas = AsyncAVAsResource(self)

    async def __aenter__(self) -> "AsyncColaCloud":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._owns_client:
            await self._client.aclose()

    def _get_headers(self) -> dict[str, str]:
        """Get default headers for requests."""
        return {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
            "User-Agent": f"colacloud-python/{__version__}",
        }

    def _parse_quota_headers(self, headers: httpx.Headers) -> QuotaInfo | None:
        """Parse quota info from response headers."""
        reset = headers.get("X-Quota-Reset")
        if not reset:
            return None

        # Try detail views first, then list records
        limit = headers.get("X-Detail-Views-Limit")
        remaining = headers.get("X-Detail-Views-Remaining")
        meter = "detail_views"

        if limit is None:
            limit = headers.get("X-List-Records-Limit")
            remaining = headers.get("X-List-Records-Remaining")
            meter = "list_records"

        if limit is None or remaining is None:
            return None

        try:
            return QuotaInfo(
                meter=meter,
                limit=int(limit),
                remaining=int(remaining),
                reset=int(reset),
            )
        except (ValueError, TypeError):
            return None

    def _handle_error(self, response: httpx.Response) -> None:
        """Handle error responses from the API."""
        status_code = response.status_code

        try:
            body = response.json()
            message = body.get("error", {}).get("message", response.text)
        except Exception:
            body = None
            message = response.text

        if status_code == 401:
            raise AuthenticationError(message=message, response_body=body)
        elif status_code == 404:
            raise NotFoundError(message=message, response_body=body)
        elif status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                message=message,
                response_body=body,
                retry_after=int(retry_after) if retry_after else None,
            )
        elif status_code == 400:
            raise ValidationError(message=message, response_body=body)
        elif status_code >= 500:
            raise ServerError(message=message, status_code=status_code, response_body=body)
        else:
            raise ColaCloudError(message=message, status_code=status_code, response_body=body)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an async HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API path (e.g., "/colas").
            params: Query parameters.
            json: JSON body for POST/PUT requests.

        Returns:
            Parsed JSON response.

        Raises:
            ConnectionError: If the request fails due to network issues.
            ColaCloudError: For API errors.
        """
        url = f"{self._base_url}{path}"

        try:
            response = await self._client.request(
                method,
                url,
                headers=self._get_headers(),
                params=params,
                json=json,
            )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to {url}: {e}") from e
        except httpx.TimeoutException as e:
            raise APIConnectionError(f"Request timed out: {e}") from e
        except httpx.RequestError as e:
            raise APIConnectionError(f"Request failed: {e}") from e

        # Update quota info
        self._last_quota_info = self._parse_quota_headers(response.headers)

        if not response.is_success:
            self._handle_error(response)

        return cast(dict[str, Any], response.json())

    async def get_usage(self) -> UsageInfo:
        """Get current API usage statistics.

        Returns:
            UsageInfo with current usage and limits.

        Raises:
            AuthenticationError: If the API key is invalid.
            ColaCloudError: For other API errors.
        """
        data = await self._request("GET", "/usage")
        response = UsageResponse.model_validate(data)
        return response.data

    @property
    def quota_info(self) -> QuotaInfo | None:
        """Get quota info from the last API response.

        Returns:
            QuotaInfo if available, None if no requests have been made yet.
        """
        return self._last_quota_info
