"""Pydantic models for COLA Cloud API responses."""

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Pagination(BaseModel):
    """Pagination information for list endpoints."""

    page: int
    per_page: int
    total: int
    pages: int


class RateLimitInfo(BaseModel):
    """Rate limit information from response headers."""

    limit: int = Field(description="Maximum requests per minute")
    remaining: int = Field(description="Remaining requests in current minute window")
    reset: int = Field(description="Unix timestamp when the rate limit resets")
    monthly_limit: int = Field(description="Maximum requests per month")
    monthly_remaining: int = Field(description="Remaining requests this month")

    model_config = ConfigDict(extra="ignore")


# COLA Models


class ColaImage(BaseModel):
    """A single image associated with a COLA."""

    ttb_image_id: str
    image_index: int
    container_position: str
    extension_type: str
    width_pixels: Optional[int] = None
    height_pixels: Optional[int] = None
    width_inches: Optional[float] = None
    height_inches: Optional[float] = None
    file_size_mb: Optional[float] = None
    barcode_count: Optional[int] = None
    qrcode_count: Optional[int] = None
    image_url: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class ColaBarcode(BaseModel):
    """A barcode extracted from a COLA image."""

    barcode_type: str
    barcode_value: str
    ttb_image_id: str
    width_pixels: Optional[int] = None
    height_pixels: Optional[int] = None
    orientation: Optional[str] = None
    relative_image_position: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class ColaSummary(BaseModel):
    """Summary COLA information returned in list responses."""

    ttb_id: str
    brand_name: str
    product_name: Optional[str] = None
    product_type: str
    class_name: Optional[str] = None
    origin_name: Optional[str] = None
    domestic_or_imported: Optional[str] = None
    permit_number: str
    application_type: Optional[str] = None
    application_status: Optional[str] = None
    application_date: Optional[date] = None
    approval_date: Optional[date] = None
    expiration_date: Optional[date] = None
    abv: Optional[float] = None
    volume: Optional[float] = None
    volume_unit: Optional[str] = None
    llm_category: Optional[str] = None
    llm_category_path: Optional[str] = None
    image_count: int = 0
    main_image_url: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class ColaDetail(BaseModel):
    """Detailed COLA information returned for single item requests."""

    # Core fields
    ttb_id: str
    brand_name: str
    product_name: Optional[str] = None
    product_type: str
    class_id: Optional[str] = None
    class_name: Optional[str] = None
    origin_id: Optional[str] = None
    origin_name: Optional[str] = None
    domestic_or_imported: Optional[str] = None
    permit_number: str

    # Application info
    application_type: Optional[str] = None
    application_status: Optional[str] = None
    application_date: Optional[date] = None
    approval_date: Optional[date] = None
    expiration_date: Optional[date] = None
    latest_update_date: Optional[date] = None

    # Container info
    is_distinctive_container: Optional[bool] = None
    for_distinctive_capacity: Optional[str] = None
    is_resubmission: Optional[bool] = None
    for_resubmission_ttb_id: Optional[str] = None
    for_exemption_state: Optional[str] = None

    # OCR data
    abv: Optional[float] = None
    volume: Optional[float] = None
    volume_unit: Optional[str] = None

    # Address
    address_recipient: Optional[str] = None
    address_zip_code: Optional[str] = None
    address_state: Optional[str] = None

    # Wine specific
    grape_varietals: Optional[list[str]] = None
    wine_vintage_year: Optional[int] = None
    wine_appellation: Optional[str] = None

    # LLM enrichment
    llm_container_type: Optional[str] = None
    llm_product_description: Optional[str] = None
    llm_brand_established_year: Optional[int] = None
    llm_category: Optional[str] = None
    llm_category_path: Optional[str] = None
    llm_tasting_note_flavors: Optional[list[str]] = None
    llm_artwork_credit: Optional[str] = None
    llm_wine_designation: Optional[str] = None
    llm_beer_ibu: Optional[str] = None
    llm_beer_hops_varieties: Optional[list[str]] = None
    llm_liquor_aged_years: Optional[int] = None
    llm_liquor_finishing_process: Optional[str] = None
    llm_liquor_grains: Optional[list[str]] = None

    # Barcode info
    barcode_type: Optional[str] = None
    barcode_value: Optional[str] = None
    qrcode_url: Optional[str] = None

    # Image info
    image_count: int = 0
    has_front_image: Optional[bool] = None
    has_back_image: Optional[bool] = None
    has_neck_image: Optional[bool] = None
    has_strip_image: Optional[bool] = None
    main_image_url: Optional[str] = None

    # Related data
    images: list[ColaImage] = Field(default_factory=list)
    barcodes: list[ColaBarcode] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


# Permittee Models


class PermitteeSummary(BaseModel):
    """Summary permittee information returned in list responses."""

    permit_number: str
    company_name: Optional[str] = None
    company_state: Optional[str] = None
    company_zip_code: Optional[str] = None
    permittee_type: Optional[str] = None
    is_active: bool
    active_reason: Optional[str] = None
    colas: Optional[int] = None
    colas_approved: Optional[int] = None
    last_cola_application_date: Optional[date] = None

    model_config = ConfigDict(extra="ignore")


class PermitteeDetail(PermitteeSummary):
    """Detailed permittee information with recent COLAs."""

    recent_colas: list[ColaSummary] = Field(default_factory=list)


# Barcode Lookup Models


class BarcodeLookupResult(BaseModel):
    """Result of a barcode lookup."""

    barcode_value: str
    barcode_type: Optional[str] = None
    colas: list[ColaSummary] = Field(default_factory=list)
    total_colas: int

    model_config = ConfigDict(extra="ignore")


# Usage Models


class UsageInfo(BaseModel):
    """API usage statistics."""

    tier: str
    monthly_limit: int
    current_period: str
    requests_used: int
    requests_remaining: int
    per_minute_limit: int

    model_config = ConfigDict(extra="ignore")


# Response Wrappers


class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""

    pagination: Pagination

    model_config = ConfigDict(extra="ignore")


class ColaListResponse(PaginatedResponse):
    """Response from list COLAs endpoint."""

    data: list[ColaSummary]


class ColaDetailResponse(BaseModel):
    """Response from get COLA endpoint."""

    data: ColaDetail

    model_config = ConfigDict(extra="ignore")


class PermitteeListResponse(PaginatedResponse):
    """Response from list permittees endpoint."""

    data: list[PermitteeSummary]


class PermitteeDetailResponse(BaseModel):
    """Response from get permittee endpoint."""

    data: PermitteeDetail

    model_config = ConfigDict(extra="ignore")


class BarcodeLookupResponse(BaseModel):
    """Response from barcode lookup endpoint."""

    data: BarcodeLookupResult

    model_config = ConfigDict(extra="ignore")


class UsageResponse(BaseModel):
    """Response from usage endpoint."""

    data: UsageInfo

    model_config = ConfigDict(extra="ignore")
