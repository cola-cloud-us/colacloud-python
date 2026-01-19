# COLA Cloud Python SDK

Official Python SDK for the [COLA Cloud API](https://colacloud.us) - Access the TTB COLA Registry of alcohol product label approvals.

## Installation

```bash
pip install colacloud
```

Or with `uv`:

```bash
uv add colacloud
```

## Quick Start

```python
from colacloud import ColaCloud

# Initialize the client
client = ColaCloud(api_key="your-api-key")

# Search COLAs
colas = client.colas.list(q="bourbon", product_type="distilled spirits")
for cola in colas.data:
    print(f"{cola.brand_name}: {cola.product_name}")

# Get a single COLA by TTB ID
cola = client.colas.get("12345678")
print(f"ABV: {cola.abv}%")
print(f"Images: {len(cola.images)}")

# Iterate through all results with automatic pagination
for cola in client.colas.iterate(q="whiskey"):
    print(cola.ttb_id)

# Don't forget to close when done
client.close()
```

## Features

- **Sync and Async Clients**: Use `ColaCloud` for synchronous code or `AsyncColaCloud` for async/await
- **Type Hints**: Full type annotations with Pydantic models
- **Automatic Pagination**: Iterate through large result sets effortlessly
- **Rate Limit Handling**: Access rate limit info from response headers
- **Custom Exceptions**: Specific exceptions for different error types

## Synchronous Client

```python
from colacloud import ColaCloud

# Using context manager (recommended)
with ColaCloud(api_key="your-api-key") as client:
    # Search COLAs
    response = client.colas.list(
        q="cabernet",
        product_type="wine",
        origin="California",
        abv_min=12.0,
        abv_max=15.0,
        page=1,
        per_page=50
    )

    print(f"Found {response.pagination.total} COLAs")
    for cola in response.data:
        print(f"- {cola.brand_name}: {cola.product_name}")

# Or manage lifecycle manually
client = ColaCloud(api_key="your-api-key")
try:
    colas = client.colas.list(q="bourbon")
finally:
    client.close()
```

## Asynchronous Client

```python
import asyncio
from colacloud import AsyncColaCloud

async def main():
    async with AsyncColaCloud(api_key="your-api-key") as client:
        # Search COLAs
        response = await client.colas.list(q="bourbon")

        # Async iteration
        async for cola in client.colas.iterate(q="whiskey"):
            print(cola.ttb_id)

asyncio.run(main())
```

## API Reference

### COLAs

#### List/Search COLAs

```python
response = client.colas.list(
    q="search query",              # Full-text search
    product_type="wine",           # malt beverage, wine, distilled spirits
    origin="France",               # Country or state
    brand_name="Chateau",          # Partial match
    approval_date_from="2024-01-01",
    approval_date_to="2024-12-31",
    abv_min=10.0,
    abv_max=20.0,
    page=1,
    per_page=20                    # Max 100
)

# Access results
for cola in response.data:
    print(cola.ttb_id, cola.brand_name)

# Pagination info
print(f"Page {response.pagination.page} of {response.pagination.pages}")
print(f"Total results: {response.pagination.total}")
```

#### Get Single COLA

```python
cola = client.colas.get("12345678")

# Basic info
print(cola.ttb_id)
print(cola.brand_name)
print(cola.product_name)
print(cola.product_type)
print(cola.abv)

# Images
for image in cola.images:
    print(f"{image.container_position}: {image.image_url}")

# Barcodes
for barcode in cola.barcodes:
    print(f"{barcode.barcode_type}: {barcode.barcode_value}")

# LLM-enriched data
print(cola.llm_product_description)
print(cola.llm_category_path)
print(cola.llm_tasting_note_flavors)
```

#### Iterate All Results

```python
# Automatically handles pagination
for cola in client.colas.iterate(q="bourbon", per_page=100):
    print(cola.ttb_id)

# With filters
for cola in client.colas.iterate(
    product_type="distilled spirits",
    origin="Kentucky",
    abv_min=40.0
):
    process_cola(cola)
```

### Permittees

#### List/Search Permittees

```python
response = client.permittees.list(
    q="distillery",    # Search by company name
    state="CA",        # Two-letter state code
    is_active=True,    # Active permit status
    page=1,
    per_page=20
)

for permittee in response.data:
    print(f"{permittee.company_name}: {permittee.colas} COLAs")
```

#### Get Single Permittee

```python
permittee = client.permittees.get("CA-I-12345")

print(permittee.company_name)
print(permittee.company_state)
print(permittee.colas)  # Total COLAs
print(permittee.is_active)

# Recent COLAs from this permittee
for cola in permittee.recent_colas:
    print(f"- {cola.brand_name}")
```

#### Iterate All Permittees

```python
for permittee in client.permittees.iterate(state="NY"):
    print(f"{permittee.permit_number}: {permittee.company_name}")
```

### Barcode Lookup

```python
result = client.barcode.lookup("012345678901")

print(f"Barcode: {result.barcode_value}")
print(f"Type: {result.barcode_type}")
print(f"Found {result.total_colas} COLAs")

for cola in result.colas:
    print(f"- {cola.brand_name}")
```

### API Usage

```python
usage = client.get_usage()

print(f"Tier: {usage.tier}")
print(f"Monthly limit: {usage.monthly_limit}")
print(f"Requests used: {usage.requests_used}")
print(f"Remaining: {usage.requests_remaining}")
print(f"Per-minute limit: {usage.per_minute_limit}")
```

### Rate Limit Info

```python
# After any request, access rate limit headers
client.colas.list(q="test")
rate_limit = client.rate_limit_info

if rate_limit:
    print(f"Remaining this minute: {rate_limit.remaining}")
    print(f"Monthly remaining: {rate_limit.monthly_remaining}")
```

## Error Handling

```python
from colacloud import (
    ColaCloud,
    ColaCloudError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError,
    ServerError,
)

client = ColaCloud(api_key="your-api-key")

try:
    cola = client.colas.get("12345678")
except AuthenticationError:
    print("Invalid API key")
except NotFoundError:
    print("COLA not found")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after {e.retry_after} seconds")
except ValidationError as e:
    print(f"Invalid request: {e.message}")
except ServerError:
    print("Server error, try again later")
except ColaCloudError as e:
    print(f"API error: {e}")
```

## Configuration

```python
from colacloud import ColaCloud

# Custom configuration
client = ColaCloud(
    api_key="your-api-key",
    base_url="https://custom.api.com/v1",  # For testing
    timeout=60.0,  # Request timeout in seconds
)

# Or bring your own HTTP client
import httpx

custom_client = httpx.Client(
    timeout=httpx.Timeout(60.0),
    limits=httpx.Limits(max_connections=10),
)

client = ColaCloud(
    api_key="your-api-key",
    http_client=custom_client,
)
```

## Models

All responses are fully typed with Pydantic models:

- `ColaSummary` - Summary COLA info (list responses)
- `ColaDetail` - Full COLA info with images and barcodes
- `ColaImage` - Image metadata
- `ColaBarcode` - Barcode data
- `PermitteeSummary` - Summary permittee info
- `PermitteeDetail` - Full permittee info with recent COLAs
- `BarcodeLookupResult` - Barcode lookup results
- `UsageInfo` - API usage statistics
- `Pagination` - Pagination metadata
- `RateLimitInfo` - Rate limit information

## Development

```bash
# Clone the repository
git clone https://github.com/cola-cloud-us/colacloud-python.git
cd colacloud-python

# Install dependencies with uv
uv sync --dev

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/colacloud

# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy src/colacloud
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Links

- [COLA Cloud Website](https://colacloud.us)
- [API Documentation](https://colacloud.us/docs/api)
- [GitHub Repository](https://github.com/cola-cloud-us/colacloud-python)
