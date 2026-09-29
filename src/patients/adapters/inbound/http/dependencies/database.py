from collections.abc import Generator

from sqlalchemy.orm import Session

from patients.adapters.outbound.database.session import SessionLocal


def get_db() -> Generator[Session]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
