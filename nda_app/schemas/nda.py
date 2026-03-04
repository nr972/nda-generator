from datetime import date, datetime

from pydantic import BaseModel, Field

from nda_app.models.nda import NDAStatus, NDAType


# --- Jurisdiction schemas ---


class JurisdictionBase(BaseModel):
    country: str
    subdivision: str | None = None
    display_name: str


class JurisdictionCreate(JurisdictionBase):
    pass


class JurisdictionResponse(JurisdictionBase):
    id: int
    is_preset: bool
    usage_count: int

    model_config = {"from_attributes": True}


class JurisdictionListResponse(BaseModel):
    top_jurisdictions: list[JurisdictionResponse]
    all_jurisdictions: list[JurisdictionResponse]


# --- NDA schemas ---


class NDACreate(BaseModel):
    """Schema for creating/generating a new NDA."""

    disclosing_party_name: str = Field(min_length=1, max_length=255)
    disclosing_party_address: str = ""
    disclosing_party_signer_name: str = ""
    disclosing_party_signer_title: str = ""
    receiving_party_name: str = Field(min_length=1, max_length=255)
    receiving_party_address: str = ""
    receiving_party_signer_name: str = ""
    receiving_party_signer_title: str = ""

    nda_type: NDAType = NDAType.MUTUAL
    effective_date: date
    term_years: int = Field(default=2, ge=1, le=10)
    survival_years: int = Field(default=2, ge=1, le=10)
    purpose: str = (
        "evaluating a potential business relationship between the parties"
    )

    jurisdiction_id: int | None = None
    notes: str = ""


class NDAUpdate(BaseModel):
    """Schema for updating NDA tracker metadata."""

    status: NDAStatus | None = None
    execution_date: date | None = None
    notes: str | None = None


class NDAResponse(BaseModel):
    """Schema for NDA responses."""

    id: int
    disclosing_party_name: str
    disclosing_party_address: str
    disclosing_party_signer_name: str
    disclosing_party_signer_title: str
    receiving_party_name: str
    receiving_party_address: str
    receiving_party_signer_name: str
    receiving_party_signer_title: str
    nda_type: NDAType
    effective_date: date
    term_years: int
    survival_years: int
    purpose: str
    jurisdiction_id: int | None
    status: NDAStatus
    execution_date: date | None
    expiry_date: date | None
    file_path: str | None
    notes: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NDAListResponse(BaseModel):
    """Paginated list of NDAs."""

    items: list[NDAResponse]
    total: int
