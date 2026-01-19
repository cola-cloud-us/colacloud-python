"""Synchronous client for the COLA Cloud API."""

from typing import Any, Optional, cast

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
    RateLimitInfo,
    UsageInfo,
    UsageResponse,
)
from .pagination import PaginatedIterator

DEFAULT_BASE_URL = "https://app.colacloud.us/api/v1"
DEFAULT_TIMEOUT = 30.0


class ColasResource:
    """Resource for interacting with COLA endpoints."""

    def __init__(self, client: "ColaCloud") -> None:
        self._client = client

    def list(
        self,
        *,
        q: Optional[str] = None,
        product_type: Optional[str] = None,
        origin: Optional[str] = None,
        brand_name: Optional[str] = None,
        approval_date_from: Optional[str] = None,
        approval_date_to: Optional[str] = None,
        abv_min: Optional[float] = None,
        abv_max: Optional[float] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> ColaListResponse:
        """List and search COLAs with pagination.

        Args:
            q: Full-text search query.
            product_type: Filter by product type (e.g., "malt beverage", "wine", "distilled spirits").
            origin: Filter by country/state of origin.
            brand_name: Filter by brand name (partial match).
            approval_date_from: Filter by minimum approval date (YYYY-MM-DD).
            approval_date_to: Filter by maximum approval date (YYYY-MM-DD).
            abv_min: Filter by minimum ABV percentage.
            abv_max: Filter by maximum ABV percentage.
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
        if origin:
            params["origin"] = origin
        if brand_name:
            params["brand_name"] = brand_name
        if approval_date_from:
            params["approval_date_from"] = approval_date_from
        if approval_date_to:
            params["approval_date_to"] = approval_date_to
        if abv_min is not None:
            params["abv_min"] = abv_min
        if abv_max is not None:
            params["abv_max"] = abv_max

        data = self._client._request("GET", "/colas", params=params)
        return ColaListResponse.model_validate(data)

    def get(self, ttb_id: str) -> ColaDetail:
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
        data = self._client._request("GET", f"/colas/{ttb_id}")
        response = ColaDetailResponse.model_validate(data)
        return response.data

    def iterate(
        self,
        *,
        q: Optional[str] = None,
        product_type: Optional[str] = None,
        origin: Optional[str] = None,
        brand_name: Optional[str] = None,
        approval_date_from: Optional[str] = None,
        approval_date_to: Optional[str] = None,
        abv_min: Optional[float] = None,
        abv_max: Optional[float] = None,
        per_page: int = 100,
    ) -> PaginatedIterator[ColaSummary]:
        """Iterate through all matching COLAs with automatic pagination.

        This method returns an iterator that automatically fetches additional
        pages as needed.

        Args:
            q: Full-text search query.
            product_type: Filter by product type.
            origin: Filter by country/state of origin.
            brand_name: Filter by brand name (partial match).
            approval_date_from: Filter by minimum approval date (YYYY-MM-DD).
            approval_date_to: Filter by maximum approval date (YYYY-MM-DD).
            abv_min: Filter by minimum ABV percentage.
            abv_max: Filter by maximum ABV percentage.
            per_page: Results per page (default: 100, max: 100).

        Yields:
            ColaSummary objects for each matching COLA.

        Example:
            ```python
            for cola in client.colas.iterate(q="bourbon"):
                print(f"{cola.brand_name}: {cola.product_name}")
            ```
        """

        def fetch_page(page: int) -> tuple[list[ColaSummary], Pagination]:
            response = self.list(
                q=q,
                product_type=product_type,
                origin=origin,
                brand_name=brand_name,
                approval_date_from=approval_date_from,
                approval_date_to=approval_date_to,
                abv_min=abv_min,
                abv_max=abv_max,
                page=page,
                per_page=per_page,
            )
            return response.data, response.pagination

        return PaginatedIterator(fetch_page)


class PermitteesResource:
    """Resource for interacting with permittee endpoints."""

    def __init__(self, client: "ColaCloud") -> None:
        self._client = client

    def list(
        self,
        *,
        q: Optional[str] = None,
        state: Optional[str] = None,
        is_active: Optional[bool] = None,
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

        data = self._client._request("GET", "/permittees", params=params)
        return PermitteeListResponse.model_validate(data)

    def get(self, permit_number: str) -> PermitteeDetail:
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
        data = self._client._request("GET", f"/permittees/{permit_number}")
        response = PermitteeDetailResponse.model_validate(data)
        return response.data

    def iterate(
        self,
        *,
        q: Optional[str] = None,
        state: Optional[str] = None,
        is_active: Optional[bool] = None,
        per_page: int = 100,
    ) -> PaginatedIterator[PermitteeSummary]:
        """Iterate through all matching permittees with automatic pagination.

        This method returns an iterator that automatically fetches additional
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
            for permittee in client.permittees.iterate(state="CA"):
                print(f"{permittee.company_name}: {permittee.colas} COLAs")
            ```
        """

        def fetch_page(page: int) -> tuple[list[PermitteeSummary], Pagination]:
            response = self.list(
                q=q,
                state=state,
                is_active=is_active,
                page=page,
                per_page=per_page,
            )
            return response.data, response.pagination

        return PaginatedIterator(fetch_page)


class BarcodeResource:
    """Resource for barcode lookups."""

    def __init__(self, client: "ColaCloud") -> None:
        self._client = client

    def lookup(self, barcode_value: str) -> BarcodeLookupResult:
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
        data = self._client._request("GET", f"/barcode/{barcode_value}")
        response = BarcodeLookupResponse.model_validate(data)
        return response.data


class ColaCloud:
    """Synchronous client for the COLA Cloud API.

    Example:
        ```python
        from colacloud import ColaCloud

        client = ColaCloud(api_key="your-api-key")

        # Search COLAs
        colas = client.colas.list(q="bourbon", product_type="distilled spirits")
        for cola in colas.data:
            print(f"{cola.brand_name}: {cola.product_name}")

        # Get a single COLA
        cola = client.colas.get("12345678")

        # Iterate through all results
        for cola in client.colas.iterate(q="whiskey"):
            print(cola.ttb_id)

        # Look up by barcode
        result = client.barcode.lookup("012345678901")
        print(f"Found {result.total_colas} COLAs")

        # Check API usage
        usage = client.get_usage()
        print(f"Used {usage.requests_used} of {usage.monthly_limit} requests")
        ```

    Args:
        api_key: Your COLA Cloud API key.
        base_url: Base URL for the API (default: https://app.colacloud.us/api/v1).
        timeout: Request timeout in seconds (default: 30).
        http_client: Optional custom httpx.Client instance.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        http_client: Optional[httpx.Client] = None,
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
            self._client = httpx.Client(timeout=timeout)
            self._owns_client = True

        self._last_rate_limit_info: Optional[RateLimitInfo] = None

        # Initialize resource classes
        self.colas = ColasResource(self)
        self.permittees = PermitteesResource(self)
        self.barcode = BarcodeResource(self)

    def __enter__(self) -> "ColaCloud":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client."""
        if self._owns_client:
            self._client.close()

    def _get_headers(self) -> dict[str, str]:
        """Get default headers for requests."""
        return {
            "X-API-Key": self._api_key,
            "Accept": "application/json",
            "User-Agent": f"colacloud-python/{__version__}",
        }

    def _parse_rate_limit_headers(self, headers: httpx.Headers) -> Optional[RateLimitInfo]:
        """Parse rate limit info from response headers."""
        try:
            return RateLimitInfo(
                limit=int(headers.get("X-RateLimit-Limit", 0)),
                remaining=int(headers.get("X-RateLimit-Remaining", 0)),
                reset=int(headers.get("X-RateLimit-Reset", 0)),
                monthly_limit=int(headers.get("X-RateLimit-Monthly-Limit", 0)),
                monthly_remaining=int(headers.get("X-RateLimit-Monthly-Remaining", 0)),
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

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the API.

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
            response = self._client.request(
                method,
                url,
                headers=self._get_headers(),
                params=params,
                json=json,
            )
        except httpx.ConnectError as e:
            raise APIConnectionError(f"Failed to connect to {url}: {e}")
        except httpx.TimeoutException as e:
            raise APIConnectionError(f"Request timed out: {e}")
        except httpx.RequestError as e:
            raise APIConnectionError(f"Request failed: {e}")

        # Update rate limit info
        self._last_rate_limit_info = self._parse_rate_limit_headers(response.headers)

        if not response.is_success:
            self._handle_error(response)

        return cast(dict[str, Any], response.json())

    def get_usage(self) -> UsageInfo:
        """Get current API usage statistics.

        Returns:
            UsageInfo with current usage and limits.

        Raises:
            AuthenticationError: If the API key is invalid.
            ColaCloudError: For other API errors.
        """
        data = self._request("GET", "/usage")
        response = UsageResponse.model_validate(data)
        return response.data

    @property
    def rate_limit_info(self) -> Optional[RateLimitInfo]:
        """Get rate limit info from the last API response.

        Returns:
            RateLimitInfo if available, None if no requests have been made yet.
        """
        return self._last_rate_limit_info
