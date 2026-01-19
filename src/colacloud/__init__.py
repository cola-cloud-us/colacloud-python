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

from .async_client import AsyncColaCloud
from .client import ColaCloud
from .exceptions import (
    AuthenticationError,
    ColaCloudError,
    ConnectionError,
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
    Pagination,
    PaginatedResponse,
    PermitteeDetail,
    PermitteeDetailResponse,
    PermitteeListResponse,
    PermitteeSummary,
    RateLimitInfo,
    UsageInfo,
    UsageResponse,
)
from .pagination import AsyncPaginatedIterator, PaginatedIterator

__version__ = "0.1.0"

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
    "ConnectionError",
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
