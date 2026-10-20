from collections.abc import Generator
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

class Base(DeclarativeBase):
    pass

DATABASE_PATH = Path(__file__).resolve().parents[3] / "var" / "dipy_ai.db"

engine = create_engine(
    f"sqlite:///{DATABASE_PATH}",
    connect_args={"check_same_thread": False},
    echo=False,
)


def init_db():
    from dipy_ai.api import models  # noqa: F401

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)
