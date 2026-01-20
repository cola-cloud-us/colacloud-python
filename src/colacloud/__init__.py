"""COLA Cloud Python SDK - Access the TTB COLA Registry of alcohol product label approvals.

Example usage:

    Synchronous client:

    ```python
    from colacloud import ColaCloud

    client = ColaCloud(api_key="your-api-key")

    # Search COLAs
    colas = client.colas.list(q="bourbon")
    for cola in colas.data:
        print(f"{cola.brand_name}: {cola.product_name}")

    # Iterate through all results
    for cola in client.colas.iterate(q="whiskey"):
        print(cola.ttb_id)
    ```

    Asynchronous client:

    ```python
    import asyncio
    from colacloud import AsyncColaCloud

    async def main():
        async with AsyncColaCloud(api_key="your-api-key") as client:
            # Search COLAs
            colas = await client.colas.list(q="bourbon")
            for cola in colas.data:
                print(f"{cola.brand_name}: {cola.product_name}")

            # Iterate through all results
            async for cola in client.colas.iterate(q="whiskey"):
                print(cola.ttb_id)

    asyncio.run(main())
    ```
"""

from ._version import __version__
from .async_client import AsyncColaCloud
from .client import ColaCloud
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
    ColaBarcode,
    ColaDetail,
    ColaDetailResponse,
    ColaImage,
    ColaListResponse,
    ColaSummary,
    PaginatedResponse,
    Pagination,
    PermitteeDetail,
    PermitteeDetailResponse,
    PermitteeListResponse,
    PermitteeSummary,
    RateLimitInfo,
    UsageInfo,
    UsageResponse,
)
from .pagination import AsyncPaginatedIterator, PaginatedIterator

__all__ = [
    # Version
    "__version__",
    # Clients
    "ColaCloud",
    "AsyncColaCloud",
    # Exceptions
    "ColaCloudError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
    "ServerError",
    "APIConnectionError",
    # Models
    "ColaSummary",
    "ColaDetail",
    "ColaImage",
    "ColaBarcode",
    "PermitteeSummary",
    "PermitteeDetail",
    "BarcodeLookupResult",
    "UsageInfo",
    "Pagination",
    "RateLimitInfo",
    # Response types
    "ColaListResponse",
    "ColaDetailResponse",
    "PermitteeListResponse",
    "PermitteeDetailResponse",
    "BarcodeLookupResponse",
    "UsageResponse",
    "PaginatedResponse",
    # Iterators
    "PaginatedIterator",
    "AsyncPaginatedIterator",
]
