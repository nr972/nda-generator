from datetime import date
from pathlib import Path

from docxtpl import DocxTemplate
from sqlalchemy.orm import Session

from nda_app.config import settings
from nda_app.models.nda import Jurisdiction, NDA
from nda_app.schemas.nda import NDACreate


def _build_context(nda_data: NDACreate, jurisdiction: Jurisdiction | None) -> dict:
    """Build the template context dictionary from the NDA creation data."""
    return {
        "effective_date": nda_data.effective_date.strftime("%B %d, %Y"),
        "disclosing_party_name": nda_data.disclosing_party_name,
        "disclosing_party_address": nda_data.disclosing_party_address,
        "disclosing_party_signer_name": nda_data.disclosing_party_signer_name,
        "disclosing_party_signer_title": nda_data.disclosing_party_signer_title,
        "receiving_party_name": nda_data.receiving_party_name,
        "receiving_party_address": nda_data.receiving_party_address,
        "receiving_party_signer_name": nda_data.receiving_party_signer_name,
        "receiving_party_signer_title": nda_data.receiving_party_signer_title,
        "purpose": nda_data.purpose,
        "term_years": nda_data.term_years,
        "survival_years": nda_data.survival_years,
        "jurisdiction_display_name": (
            jurisdiction.display_name if jurisdiction else "_______________"
        ),
    }


def _generate_filename(nda_data: NDACreate) -> str:
    """Generate a descriptive filename for the NDA document."""
    safe_name = (
        nda_data.receiving_party_name.replace(" ", "_").replace("/", "-")[:50]
    )
    date_str = nda_data.effective_date.strftime("%Y%m%d")
    return f"NDA_{safe_name}_{date_str}.docx"


def _calculate_expiry(effective_date: date, term_years: int) -> date:
    """Calculate expiry date, handling leap year edge case."""
    try:
        return effective_date.replace(year=effective_date.year + term_years)
    except ValueError:
        # Feb 29 in a non-leap year → use Feb 28
        return effective_date.replace(
            year=effective_date.year + term_years, day=28
        )


def generate_nda(db: Session, nda_data: NDACreate) -> NDA:
    """Generate an NDA document and create a database record.

    1. Look up the jurisdiction (if provided)
    2. Render the .docx template with context variables
    3. Save the rendered file to the output directory
    4. Create and return an NDA database record
    """
    # Look up jurisdiction
    jurisdiction = None
    if nda_data.jurisdiction_id:
        jurisdiction = db.get(Jurisdiction, nda_data.jurisdiction_id)
        if jurisdiction:
            jurisdiction.usage_count += 1

    # Build context and render template
    context = _build_context(nda_data, jurisdiction)
    template_path = settings.templates_dir / "mutual_nda.docx"
    doc = DocxTemplate(str(template_path))
    doc.render(context)

    # Save rendered document
    filename = _generate_filename(nda_data)
    output_path = settings.output_dir / filename
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))

    # Calculate expiry date
    expiry = _calculate_expiry(nda_data.effective_date, nda_data.term_years)

    # Create database record
    nda = NDA(
        disclosing_party_name=nda_data.disclosing_party_name,
        disclosing_party_address=nda_data.disclosing_party_address,
        disclosing_party_signer_name=nda_data.disclosing_party_signer_name,
        disclosing_party_signer_title=nda_data.disclosing_party_signer_title,
        receiving_party_name=nda_data.receiving_party_name,
        receiving_party_address=nda_data.receiving_party_address,
        receiving_party_signer_name=nda_data.receiving_party_signer_name,
        receiving_party_signer_title=nda_data.receiving_party_signer_title,
        nda_type=nda_data.nda_type,
        effective_date=nda_data.effective_date,
        term_years=nda_data.term_years,
        survival_years=nda_data.survival_years,
        purpose=nda_data.purpose,
        jurisdiction_id=nda_data.jurisdiction_id,
        status="draft",
        expiry_date=expiry,
        file_path=str(output_path.relative_to(settings.output_dir.parent)),
        notes=nda_data.notes,
    )
    db.add(nda)
    db.commit()
    db.refresh(nda)
    return nda
