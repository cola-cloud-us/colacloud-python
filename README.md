# COLA Cloud Python SDK

Official Python SDK for the [COLA Cloud API](https://colacloud.us) - Access the TTB COLA Registry of alcohol product label approvals.

COLA Cloud is an independent service that turns public TTB label approvals into searchable, enriched data. An approval record is not a unique product or proof of current retail availability. See the [product-data workflow and source limits](https://colacloud.us/product-enrichment) and [California wine recipe](https://colacloud.us/data/california-wine).

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

# One page of California-origin wine approvals in a fixed date scope
colas = client.colas.list(
    product_type="wine",
    origin="California",
    approval_date_from="2026-08-01",
    approval_date_to="2026-08-31",
    per_page=1,
)
print(f"Returned {len(colas.data)} records on this page")
for cola in colas.data:
    print(f"{cola.brand_name}: {cola.product_name}")

# Retrieve a real ID returned by search; an empty page is valid
if colas.data:
    cola = client.colas.get(colas.data[0].ttb_id)
    print(f"ABV: {cola.abv}%")  # May be None
    print(f"Images: {len(cola.images)}")

# Don't forget to close when done
client.close()
```

## Features

- **Sync and Async Clients**: Use `ColaCloud` for synchronous code or `AsyncColaCloud` for async/await
- **Type Hints**: Full type annotations with Pydantic models
- **Automatic Pagination**: Iterate through large result sets effortlessly
- **Quota Tracking**: Access usage quotas for detail views and list records
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
        per_page=50,
    )

    print(f"Returned {len(response.data)} records on this page")
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

The following is a filter reference, not a known matching query: filters are combined. `origin` matches a recorded state/country name, not all domestic records. Use the quickstart for a small verified query.

```python
response = client.colas.list(
    q="search query",  # Brand, product, permit, applicant/company, etc.
    product_type="wine",  # malt beverage, wine, distilled spirits
    category="Wine",  # Beer, Wine, Liquor
    derived_subcategory="Wine > Red Wine",
    origin="France",  # Country or state
    brand_name="Chateau",  # Partial match
    permit_number="CA-I-12345",
    barcode_value="012345678905",
    approval_date_from="2024-01-01",
    approval_date_to="2024-12-31",
    abv_min=10.0,
    abv_max=20.0,
    volume_unit="milliliters",  # Required with volume_min/volume_max
    volume_min=375,
    volume_max=750,
    container_type="bottle,can",
    sort="relevance_desc",  # Or approval_date_desc
    page=1,
    per_page=20,  # Max 100
)

# Access results
for cola in response.data:
    print(cola.ttb_id, cola.brand_name)

# Pagination info
print(f"Returned {len(response.data)} records")
if response.pagination.total is not None:
    print(f"Total results: {response.pagination.total}")
print(f"More pages available: {response.pagination.has_more}")
```

#### Get Single COLA

```python
matches = client.colas.list(product_type="wine", origin="California", per_page=1)
if not matches.data:
    raise SystemExit("No matches in the query scope")
cola = client.colas.get(matches.data[0].ttb_id)

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

Iteration covers the matching query scope, not the entire registry. Without explicit dates the API defaults to the last 365 days. Totals and page counts may be null; the SDK iterator handles continuation. Date eligibility can fall back from approval date to application/latest-update date. Each page uses your plan allowance.

```python
# Automatically handles pagination
for cola in client.colas.iterate(
    q="bourbon",
    per_page=100,
    approval_date_from="2026-08-01",
    approval_date_to="2026-08-31",
):
    print(cola.ttb_id)

# With filters
for cola in client.colas.iterate(product_type="distilled spirits", origin="Kentucky", abv_min=40.0):
    process_cola(cola)
```

### Permittees

#### List/Search Permittees

```python
response = client.permittees.list(
    q="distillery",  # Search by company name
    state="CA",  # Two-letter state code
    is_active=True,  # Active permit status
    sort="relevance_desc",
    page=1,
    per_page=20,
)

for permittee in response.data:
    print(f"{permittee.company_name}: {permittee.colas} COLAs")
```

#### Get Single Permittee

```python
matches = client.permittees.list(state="CA", per_page=1)
if not matches.data:
    raise SystemExit("No permittees found")
permittee = client.permittees.get(matches.data[0].permit_number)

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

Barcode lookup returns matching approval records from decoded label images. Codes may be missing or repeated across approvals; review the candidate records before treating a match as a product identity. The UPC example uses a code from the [existing whiskey evaluation sample](https://colacloud.us/data-packs/whiskey).

```python
result = client.barcode.lookup("869357000220")

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
print(f"Period: {usage.current_period}")
print(f"Detail views: {usage.detail_views.used} / {usage.detail_views.limit}")
print(f"List records: {usage.list_records.used} / {usage.list_records.limit}")
print(f"Burst limit: {usage.per_minute_limit} req/min")
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

ttb_id = input("TTB ID returned by search: ").strip()
try:
    # Replace with an ID returned by your search
    cola = client.colas.get(ttb_id)
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
uv run ruff format .
uv run ruff check --fix .

# Type checking
uv run mypy src/colacloud
```

## License

MIT License covers this SDK; see [LICENSE](LICENSE). Data and label artwork have separate rights and terms.

## Links

- [COLA Cloud Website](https://colacloud.us)
- [API Documentation](https://docs.colacloud.us/api-reference)
- [GitHub Repository](https://github.com/cola-cloud-us/colacloud-python)

Public support: help@colacloud.us
