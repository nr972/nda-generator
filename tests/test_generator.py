from datetime import date

from app.schemas.nda import NDACreate
from app.services.generator import generate_nda


def test_generate_nda_creates_file_and_record(db, tmp_path, monkeypatch):
    """Test that generate_nda creates a .docx file and a database record."""
    from app import config

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    nda_data = NDACreate(
        disclosing_party_name="Test Corp",
        receiving_party_name="Sample Inc",
        effective_date=date(2026, 6, 1),
        term_years=2,
        survival_years=2,
        jurisdiction_id=5,
    )

    nda = generate_nda(db, nda_data)

    assert nda.id is not None
    assert nda.disclosing_party_name == "Test Corp"
    assert nda.receiving_party_name == "Sample Inc"
    assert nda.status.value == "draft"
    assert nda.expiry_date == date(2028, 6, 1)
    assert nda.file_path is not None

    generated_files = list(tmp_path.glob("*.docx"))
    assert len(generated_files) == 1
    assert "Sample_Inc" in generated_files[0].name


def test_generate_nda_without_jurisdiction(db, tmp_path, monkeypatch):
    """Test that an NDA can be generated without selecting a jurisdiction."""
    from app import config

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    nda_data = NDACreate(
        disclosing_party_name="Alpha LLC",
        receiving_party_name="Beta Corp",
        effective_date=date(2026, 1, 15),
    )

    nda = generate_nda(db, nda_data)
    assert nda.id is not None
    assert nda.jurisdiction_id is None


def test_generate_nda_increments_jurisdiction_usage(db, tmp_path, monkeypatch):
    """Test that generating an NDA increments the jurisdiction usage count."""
    from app import config
    from app.models.nda import Jurisdiction

    monkeypatch.setattr(config.settings, "output_dir", tmp_path)

    # Get initial usage count for jurisdiction 5 (Delaware)
    jur = db.get(Jurisdiction, 5)
    initial_count = jur.usage_count

    nda_data = NDACreate(
        disclosing_party_name="Corp A",
        receiving_party_name="Corp B",
        effective_date=date(2026, 3, 1),
        jurisdiction_id=5,
    )
    generate_nda(db, nda_data)

    db.refresh(jur)
    assert jur.usage_count == initial_count + 1
