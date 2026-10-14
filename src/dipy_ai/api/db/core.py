from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from dipy_ai.api.db.base import Base
from dipy_ai.api.model.conversation import Conversation  # noqa: F401
from dipy_ai.api.model.message import Message  # noqa: F401

engine = create_engine(
    "sqlite:///dipy_ai.db",
    connect_args={"check_same_thread": False},
    echo=False,
)
Base.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
