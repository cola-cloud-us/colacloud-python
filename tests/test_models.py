"""Tests for Pydantic models."""

from datetime import date

import pytest

from colacloud.models import (
    BarcodeLookupResponse,
    BarcodeLookupResult,
    ColaBarcode,
    ColaDetail,
    ColaDetailResponse,
    ColaImage,
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


class TestPagination:
    """Tests for Pagination model."""

    def test_pagination_from_dict(self):
        data = {"page": 1, "per_page": 20, "total": 100, "pages": 5}
        pagination = Pagination.model_validate(data)

        assert pagination.page == 1
        assert pagination.per_page == 20
        assert pagination.total == 100
        assert pagination.pages == 5


class TestRateLimitInfo:
    """Tests for RateLimitInfo model."""

    def test_rate_limit_info_from_dict(self):
        data = {
            "limit": 60,
            "remaining": 55,
            "reset": 1704067200,
            "monthly_limit": 10000,
            "monthly_remaining": 9500,
        }
        rate_limit = RateLimitInfo.model_validate(data)

        assert rate_limit.limit == 60
        assert rate_limit.remaining == 55
        assert rate_limit.reset == 1704067200
        assert rate_limit.monthly_limit == 10000
        assert rate_limit.monthly_remaining == 9500


class TestColaSummary:
    """Tests for ColaSummary model."""

    def test_cola_summary_from_dict(self, sample_cola_summary):
        cola = ColaSummary.model_validate(sample_cola_summary)

        assert cola.ttb_id == "12345678"
        assert cola.brand_name == "Test Brand"
        assert cola.product_name == "Test Product"
        assert cola.product_type == "distilled spirits"
        assert cola.class_name == "Whiskey"
        assert cola.origin_name == "Kentucky"
        assert cola.permit_number == "KY-I-12345"
        assert cola.abv == 40.0
        assert cola.volume == 750.0
        assert cola.image_count == 2
        assert cola.approval_date == date(2024, 1, 15)

    def test_cola_summary_optional_fields(self):
        data = {
            "ttb_id": "12345678",
            "brand_name": "Test Brand",
            "product_type": "wine",
            "permit_number": "CA-I-12345",
        }
        cola = ColaSummary.model_validate(data)

        assert cola.ttb_id == "12345678"
        assert cola.product_name is None
        assert cola.abv is None
        assert cola.main_image_url is None


class TestColaDetail:
    """Tests for ColaDetail model."""

    def test_cola_detail_from_dict(self, sample_cola_detail):
        cola = ColaDetail.model_validate(sample_cola_detail)

        assert cola.ttb_id == "12345678"
        assert cola.brand_name == "Test Brand"
        assert cola.llm_container_type == "bottle"
        assert cola.llm_liquor_aged_years == 4
        assert cola.llm_liquor_grains == ["corn", "rye", "barley"]
        assert len(cola.images) == 2
        assert len(cola.barcodes) == 1

    def test_cola_detail_images(self, sample_cola_detail):
        cola = ColaDetail.model_validate(sample_cola_detail)

        front_image = cola.images[0]
        assert isinstance(front_image, ColaImage)
        assert front_image.ttb_image_id == "IMG001"
        assert front_image.container_position == "front"
        assert front_image.width_pixels == 1200

    def test_cola_detail_barcodes(self, sample_cola_detail):
        cola = ColaDetail.model_validate(sample_cola_detail)

        barcode = cola.barcodes[0]
        assert isinstance(barcode, ColaBarcode)
        assert barcode.barcode_type == "UPC-A"
        assert barcode.barcode_value == "012345678901"


class TestColaImage:
    """Tests for ColaImage model."""

    def test_cola_image_from_dict(self):
        data = {
            "ttb_image_id": "IMG001",
            "image_index": 0,
            "container_position": "front",
            "extension_type": "jpg",
            "width_pixels": 1200,
            "height_pixels": 1800,
            "image_url": "https://example.com/image.jpg",
        }
        image = ColaImage.model_validate(data)

        assert image.ttb_image_id == "IMG001"
        assert image.container_position == "front"
        assert image.image_url == "https://example.com/image.jpg"


class TestColaBarcode:
    """Tests for ColaBarcode model."""

    def test_cola_barcode_from_dict(self):
        data = {
            "barcode_type": "UPC-A",
            "barcode_value": "012345678901",
            "ttb_image_id": "IMG001",
            "orientation": "horizontal",
        }
        barcode = ColaBarcode.model_validate(data)

        assert barcode.barcode_type == "UPC-A"
        assert barcode.barcode_value == "012345678901"


class TestPermitteeSummary:
    """Tests for PermitteeSummary model."""

    def test_permittee_summary_from_dict(self, sample_permittee_summary):
        permittee = PermitteeSummary.model_validate(sample_permittee_summary)

        assert permittee.permit_number == "KY-I-12345"
        assert permittee.company_name == "Test Distillery Inc."
        assert permittee.company_state == "KY"
        assert permittee.is_active is True
        assert permittee.colas == 150


class TestPermitteeDetail:
    """Tests for PermitteeDetail model."""

    def test_permittee_detail_from_dict(self, sample_permittee_detail):
        permittee = PermitteeDetail.model_validate(sample_permittee_detail)

        assert permittee.permit_number == "KY-I-12345"
        assert len(permittee.recent_colas) == 1
        assert permittee.recent_colas[0].ttb_id == "12345678"


class TestBarcodeLookupResult:
    """Tests for BarcodeLookupResult model."""

    def test_barcode_lookup_from_dict(self, sample_barcode_lookup):
        result = BarcodeLookupResult.model_validate(sample_barcode_lookup)

        assert result.barcode_value == "012345678901"
        assert result.barcode_type == "UPC-A"
        assert result.total_colas == 1
        assert len(result.colas) == 1


class TestUsageInfo:
    """Tests for UsageInfo model."""

    def test_usage_info_from_dict(self, sample_usage):
        usage = UsageInfo.model_validate(sample_usage)

        assert usage.tier == "starter"
        assert usage.monthly_limit == 10000
        assert usage.requests_used == 500
        assert usage.requests_remaining == 9500
        assert usage.per_minute_limit == 60


class TestResponseModels:
    """Tests for response wrapper models."""

    def test_cola_list_response(self, cola_list_response):
        response = ColaListResponse.model_validate(cola_list_response)

        assert len(response.data) == 1
        assert response.data[0].ttb_id == "12345678"
        assert response.pagination.total == 1

    def test_cola_detail_response(self, cola_detail_response):
        response = ColaDetailResponse.model_validate(cola_detail_response)

        assert response.data.ttb_id == "12345678"
        assert len(response.data.images) == 2

    def test_permittee_list_response(self, permittee_list_response):
        response = PermitteeListResponse.model_validate(permittee_list_response)

        assert len(response.data) == 1
        assert response.data[0].permit_number == "KY-I-12345"

    def test_permittee_detail_response(self, permittee_detail_response):
        response = PermitteeDetailResponse.model_validate(permittee_detail_response)

        assert response.data.permit_number == "KY-I-12345"

    def test_barcode_lookup_response(self, barcode_lookup_response):
        response = BarcodeLookupResponse.model_validate(barcode_lookup_response)

        assert response.data.barcode_value == "012345678901"

    def test_usage_response(self, usage_response):
        response = UsageResponse.model_validate(usage_response)

        assert response.data.tier == "starter"
