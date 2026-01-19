"""Pytest fixtures for COLA Cloud SDK tests."""

import pytest

# Sample API responses for testing

SAMPLE_COLA_SUMMARY = {
    "ttb_id": "12345678",
    "brand_name": "Test Brand",
    "product_name": "Test Product",
    "product_type": "distilled spirits",
    "class_name": "Whiskey",
    "origin_name": "Kentucky",
    "domestic_or_imported": "domestic",
    "permit_number": "KY-I-12345",
    "application_type": "label approval",
    "application_status": "approved",
    "application_date": "2024-01-01",
    "approval_date": "2024-01-15",
    "expiration_date": "2027-01-15",
    "abv": 40.0,
    "volume": 750.0,
    "volume_unit": "ml",
    "llm_category": "Bourbon",
    "llm_category_path": "Whiskey > Bourbon",
    "image_count": 2,
    "main_image_url": "https://example.com/image.jpg",
}

SAMPLE_COLA_DETAIL = {
    **SAMPLE_COLA_SUMMARY,
    "class_id": "CLS123",
    "origin_id": "ORG456",
    "latest_update_date": "2024-01-15",
    "is_distinctive_container": False,
    "for_distinctive_capacity": None,
    "is_resubmission": False,
    "for_resubmission_ttb_id": None,
    "for_exemption_state": None,
    "address_recipient": "Test Distillery",
    "address_zip_code": "40001",
    "address_state": "KY",
    "grape_varietals": None,
    "wine_vintage_year": None,
    "wine_appellation": None,
    "llm_container_type": "bottle",
    "llm_product_description": "A smooth bourbon whiskey",
    "llm_brand_established_year": 1890,
    "llm_tasting_note_flavors": ["vanilla", "caramel", "oak"],
    "llm_artwork_credit": None,
    "llm_wine_designation": None,
    "llm_beer_ibu": None,
    "llm_beer_hops_varieties": None,
    "llm_liquor_aged_years": 4,
    "llm_liquor_finishing_process": None,
    "llm_liquor_grains": ["corn", "rye", "barley"],
    "barcode_type": "UPC-A",
    "barcode_value": "012345678901",
    "qrcode_url": None,
    "has_front_image": True,
    "has_back_image": True,
    "has_neck_image": False,
    "has_strip_image": False,
    "images": [
        {
            "ttb_image_id": "IMG001",
            "image_index": 0,
            "container_position": "front",
            "extension_type": "jpg",
            "width_pixels": 1200,
            "height_pixels": 1800,
            "width_inches": 4.0,
            "height_inches": 6.0,
            "file_size_mb": 0.5,
            "barcode_count": 1,
            "qrcode_count": 0,
            "image_url": "https://example.com/front.jpg",
        },
        {
            "ttb_image_id": "IMG002",
            "image_index": 1,
            "container_position": "back",
            "extension_type": "jpg",
            "width_pixels": 1200,
            "height_pixels": 1800,
            "width_inches": 4.0,
            "height_inches": 6.0,
            "file_size_mb": 0.4,
            "barcode_count": 0,
            "qrcode_count": 0,
            "image_url": "https://example.com/back.jpg",
        },
    ],
    "barcodes": [
        {
            "barcode_type": "UPC-A",
            "barcode_value": "012345678901",
            "ttb_image_id": "IMG001",
            "width_pixels": 200,
            "height_pixels": 100,
            "orientation": "horizontal",
            "relative_image_position": "bottom",
        }
    ],
}

SAMPLE_PERMITTEE_SUMMARY = {
    "permit_number": "KY-I-12345",
    "company_name": "Test Distillery Inc.",
    "company_state": "KY",
    "company_zip_code": "40001",
    "permittee_type": "distiller",
    "is_active": True,
    "active_reason": None,
    "colas": 150,
    "colas_approved": 148,
    "last_cola_application_date": "2024-01-01",
}

SAMPLE_PERMITTEE_DETAIL = {
    **SAMPLE_PERMITTEE_SUMMARY,
    "recent_colas": [SAMPLE_COLA_SUMMARY],
}

SAMPLE_BARCODE_LOOKUP = {
    "barcode_value": "012345678901",
    "barcode_type": "UPC-A",
    "colas": [SAMPLE_COLA_SUMMARY],
    "total_colas": 1,
}

SAMPLE_USAGE = {
    "tier": "starter",
    "monthly_limit": 10000,
    "current_period": "2024-01",
    "requests_used": 500,
    "requests_remaining": 9500,
    "per_minute_limit": 60,
}


@pytest.fixture
def sample_cola_summary():
    """Return a sample COLA summary dict."""
    return SAMPLE_COLA_SUMMARY.copy()


@pytest.fixture
def sample_cola_detail():
    """Return a sample COLA detail dict."""
    return SAMPLE_COLA_DETAIL.copy()


@pytest.fixture
def sample_permittee_summary():
    """Return a sample permittee summary dict."""
    return SAMPLE_PERMITTEE_SUMMARY.copy()


@pytest.fixture
def sample_permittee_detail():
    """Return a sample permittee detail dict."""
    return SAMPLE_PERMITTEE_DETAIL.copy()


@pytest.fixture
def sample_barcode_lookup():
    """Return a sample barcode lookup result dict."""
    return SAMPLE_BARCODE_LOOKUP.copy()


@pytest.fixture
def sample_usage():
    """Return a sample usage info dict."""
    return SAMPLE_USAGE.copy()


@pytest.fixture
def cola_list_response(sample_cola_summary):
    """Return a sample COLA list response."""
    return {
        "data": [sample_cola_summary],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 1,
            "pages": 1,
        },
    }


@pytest.fixture
def cola_detail_response(sample_cola_detail):
    """Return a sample COLA detail response."""
    return {"data": sample_cola_detail}


@pytest.fixture
def permittee_list_response(sample_permittee_summary):
    """Return a sample permittee list response."""
    return {
        "data": [sample_permittee_summary],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 1,
            "pages": 1,
        },
    }


@pytest.fixture
def permittee_detail_response(sample_permittee_detail):
    """Return a sample permittee detail response."""
    return {"data": sample_permittee_detail}


@pytest.fixture
def barcode_lookup_response(sample_barcode_lookup):
    """Return a sample barcode lookup response."""
    return {"data": sample_barcode_lookup}


@pytest.fixture
def usage_response(sample_usage):
    """Return a sample usage response."""
    return {"data": sample_usage}
