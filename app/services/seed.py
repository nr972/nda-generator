from sqlalchemy.orm import Session

from app.models.nda import Jurisdiction

PRESET_JURISDICTIONS = [
    {"country": "Australia", "subdivision": None, "display_name": "Australia", "usage_count": 0},
    {"country": "Germany", "subdivision": None, "display_name": "Germany", "usage_count": 0},
    {"country": "United Kingdom", "subdivision": None, "display_name": "United Kingdom", "usage_count": 0},
    {"country": "United States", "subdivision": "California", "display_name": "California, United States", "usage_count": 1},
    {"country": "United States", "subdivision": "Delaware", "display_name": "Delaware, United States", "usage_count": 3},
    {"country": "United States", "subdivision": "Illinois", "display_name": "Illinois, United States", "usage_count": 0},
    {"country": "United States", "subdivision": "Massachusetts", "display_name": "Massachusetts, United States", "usage_count": 0},
    {"country": "United States", "subdivision": "Nevada", "display_name": "Nevada, United States", "usage_count": 0},
    {"country": "United States", "subdivision": "New York", "display_name": "New York, United States", "usage_count": 2},
    {"country": "United States", "subdivision": "Oregon", "display_name": "Oregon, United States", "usage_count": 0},
    {"country": "United States", "subdivision": "Texas", "display_name": "Texas, United States", "usage_count": 0},
    {"country": "United States", "subdivision": "Washington", "display_name": "Washington, United States", "usage_count": 0},
]


def seed_jurisdictions(db: Session) -> None:
    """Insert preset jurisdictions if the table is empty."""
    existing = db.query(Jurisdiction).count()
    if existing > 0:
        return

    for j in PRESET_JURISDICTIONS:
        db.add(Jurisdiction(**j, is_preset=True))
    db.commit()
