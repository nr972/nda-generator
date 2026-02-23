import enum
from datetime import UTC, date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NDAStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    EXECUTED = "executed"
    EXPIRED = "expired"


class NDAType(str, enum.Enum):
    MUTUAL = "mutual"


class NDA(Base):
    __tablename__ = "ndas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Parties
    disclosing_party_name: Mapped[str] = mapped_column(String(255))
    disclosing_party_address: Mapped[str] = mapped_column(Text, default="")
    disclosing_party_signer_name: Mapped[str] = mapped_column(String(255), default="")
    disclosing_party_signer_title: Mapped[str] = mapped_column(String(255), default="")
    receiving_party_name: Mapped[str] = mapped_column(String(255))
    receiving_party_address: Mapped[str] = mapped_column(Text, default="")
    receiving_party_signer_name: Mapped[str] = mapped_column(String(255), default="")
    receiving_party_signer_title: Mapped[str] = mapped_column(String(255), default="")

    # NDA specifics
    nda_type: Mapped[NDAType] = mapped_column(Enum(NDAType), default=NDAType.MUTUAL)
    effective_date: Mapped[date] = mapped_column(Date)
    term_years: Mapped[int] = mapped_column(Integer, default=2)
    survival_years: Mapped[int] = mapped_column(Integer, default=2)
    purpose: Mapped[str] = mapped_column(
        Text,
        default="evaluating a potential business relationship between the parties",
    )

    # Jurisdiction
    jurisdiction_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("jurisdictions.id"), nullable=True
    )
    jurisdiction: Mapped["Jurisdiction"] = relationship(back_populates="ndas")

    # Tracking / registry
    status: Mapped[NDAStatus] = mapped_column(
        Enum(NDAStatus), default=NDAStatus.DRAFT
    )
    execution_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )


class Jurisdiction(Base):
    __tablename__ = "jurisdictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    country: Mapped[str] = mapped_column(String(100))
    subdivision: Mapped[str | None] = mapped_column(String(100), nullable=True)
    display_name: Mapped[str] = mapped_column(String(200), unique=True)
    is_preset: Mapped[bool] = mapped_column(Boolean, default=False)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)

    ndas: Mapped[list["NDA"]] = relationship(back_populates="jurisdiction")
