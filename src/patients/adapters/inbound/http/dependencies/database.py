from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from patients.adapters.outbound.database.session import SessionLocal


def get_db() -> Generator[Session]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def check_db_health(db: Session = Depends(get_db)) -> str:
    try:
        db.execute(text("SELECT 1"))
        return "connected"
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "service": "patients-microservice",
                "database": "disconnected",
            },
        ) from exc
