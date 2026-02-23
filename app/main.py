from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import jurisdictions, ndas
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models.nda import NDA, Jurisdiction  # noqa: F401 — register models with Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    # Seed preset jurisdictions
    from app.services.seed import seed_jurisdictions

    db = SessionLocal()
    try:
        seed_jurisdictions(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ndas.router, prefix="/api/ndas", tags=["NDAs"])
app.include_router(jurisdictions.router, prefix="/api/jurisdictions", tags=["Jurisdictions"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
