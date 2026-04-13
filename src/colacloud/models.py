"""Pydantic models for COLA Cloud API responses."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class Pagination(BaseModel):
    """Pagination information for list endpoints."""

    page: int
    per_page: int
    total: int | None = None
    pages: int | None = None
    has_more: bool | None = None
    mode: str | None = None


class QuotaInfo(BaseModel):
    """Quota information parsed from response headers."""

    meter: str = Field(description="Which meter: 'detail_views' or 'list_records'")
    limit: int = Field(description="Quota limit for the current billing period")
    remaining: int = Field(description="Remaining quota in the current billing period")
    reset: int = Field(description="Unix timestamp when quotas reset (first of next month)")

    model_config = ConfigDict(extra="ignore")


# COLA Models


class ColaImage(BaseModel):
    """A single image associated with a COLA."""

    ttb_image_id: str
    image_index: int
    container_position: str
    extension_type: str
    width_pixels: int | None = None
    height_pixels: int | None = None
    width_inches: float | None = None
    height_inches: float | None = None
    file_size_mb: float | None = None
    barcode_count: int | None = None
    qrcode_count: int | None = None
    image_url: str | None = None

    model_config = ConfigDict(extra="ignore")


class ColaBarcode(BaseModel):
    """A barcode extracted from a COLA image."""

    barcode_type: str
    barcode_value: str
    ttb_image_id: str
    width_pixels: int | None = None
    height_pixels: int | None = None
    orientation: str | None = None
    relative_image_position: str | None = None

    model_config = ConfigDict(extra="ignore")


class ColaSummary(BaseModel):
    """Summary COLA information returned in list responses."""

    ttb_id: str
    brand_name: str
    product_name: str | None = None
    product_type: str
    class_name: str | None = None
    origin_name: str | None = None
    permit_number: str
    approval_date: date | None = None
    image_count: int = 0
    has_barcode: bool = False

    model_config = ConfigDict(extra="ignore")


class ColaDetail(BaseModel):
    """Detailed COLA information returned for single item requests."""

    # Core fields
    ttb_id: str
    brand_name: str
    product_name: str | None = None
    product_type: str
    class_id: str | None = None
    class_name: str | None = None
    origin_id: str | None = None
    origin_name: str | None = None
    domestic_or_imported: str | None = None
    permit_number: str

    # Application info
    application_type: str | None = None
    application_status: str | None = None
    application_date: date | None = None
    approval_date: date | None = None
    expiration_date: date | None = None
    latest_update_date: date | None = None

    # Container info
    is_distinctive_container: bool | None = None
    for_distinctive_capacity: str | None = None
    is_resubmission: bool | None = None
    for_resubmission_ttb_id: str | None = None
    for_exemption_state: str | None = None

    # OCR data
    abv: float | None = None
    volume: float | None = None
    volume_unit: str | None = None

    # Address
    address_recipient: str | None = None
    address_zip_code: str | None = None
    address_state: str | None = None

    # Wine specific
    grape_varietals: list[str] | None = None
    wine_vintage_year: int | None = None
    wine_appellation: str | None = None

    # LLM enrichment
    llm_container_type: str | None = None
    llm_product_description: str | None = None
    llm_brand_established_year: int | None = None
    llm_category: str | None = None
    llm_category_path: str | None = None
    llm_tasting_note_flavors: list[str] | None = None
    llm_artwork_credit: str | None = None
    llm_wine_designation: str | None = None
    llm_beer_ibu: str | None = None
    llm_beer_hops_varieties: list[str] | None = None
    llm_liquor_aged_years: int | None = None
    llm_liquor_finishing_process: str | None = None
    llm_liquor_grains: list[str] | None = None

    # Barcode info
    barcode_type: str | None = None
    barcode_value: str | None = None
    qrcode_url: str | None = None

    # Image info
    image_count: int = 0
    has_front_image: bool | None = None
    has_back_image: bool | None = None
    has_neck_image: bool | None = None
    has_strip_image: bool | None = None
    main_image_url: str | None = None

    # Related data
    images: list[ColaImage] = Field(default_factory=list)
    barcodes: list[ColaBarcode] = Field(default_factory=list)

    model_config = ConfigDict(extra="ignore")


# Permittee Models


class PermitteeSummary(BaseModel):
    """Summary permittee information returned in list responses."""

    permit_number: str
    company_name: str | None = None
    company_state: str | None = None
    company_zip_code: str | None = None
    permittee_type: str | None = None
    is_active: bool
    active_reason: str | None = None
    colas: int | None = None  # Paid plans only (starter/pro)
    colas_approved: int | None = None  # Paid plans only (starter/pro)
    last_cola_application_date: date | None = None  # Paid plans only (starter/pro)

    model_config = ConfigDict(extra="ignore")


class PermitteeDetail(PermitteeSummary):
    """Detailed permittee information with recent COLAs."""

    recent_colas: list[ColaSummary] = Field(default_factory=list)


# Barcode Lookup Models


class BarcodeLookupResult(BaseModel):
    """Result of a barcode lookup."""

    barcode_value: str
    barcode_type: str | None = None
    colas: list[ColaSummary] = Field(default_factory=list)
    total_colas: int

    model_config = ConfigDict(extra="ignore")


# Usage Models


class UsageQuota(BaseModel):
    """Usage quota for a single meter."""

    used: int
    limit: int
    remaining: int

    model_config = ConfigDict(extra="ignore")


class UsageInfo(BaseModel):
    """API usage statistics."""

    tier: str
    current_period: str
    detail_views: UsageQuota
    list_records: UsageQuota
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


# Reference Data Models


class MetaInfo(BaseModel):
    """Meta information for reference data endpoints."""

    total: int
    page: int | None = None
    per_page: int | None = None
    has_more: bool | None = None

    model_config = ConfigDict(extra="ignore")


class ProcessingTimeRecord(BaseModel):
    """A single processing time record."""

    model_config = ConfigDict(extra="allow")


class ProductionReportRecord(BaseModel):
    """A single production report record."""

    model_config = ConfigDict(extra="allow")


class AVARecord(BaseModel):
    """A single American Viticultural Area (AVA) record."""

    model_config = ConfigDict(extra="allow")


class ReferenceDataResponse(BaseModel):
    """Response from reference data endpoints (processing-times, avas, production-reports)."""

    data: list[dict]
    meta: MetaInfo

    model_config = ConfigDict(extra="ignore")


class ReferenceDataDetailResponse(BaseModel):
    """Response from reference data detail endpoints (e.g., avas/{id})."""

    data: dict

    model_config = ConfigDict(extra="ignore")
