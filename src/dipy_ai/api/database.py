from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session
from dipy_ai.api.db.base import Base
from dipy_ai.api.model.conversation import Conversation  # noqa: F401
from dipy_ai.api.model.message import Message  # noqa: F401


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

class Base(DeclarativeBase):
    pass

engine = create_engine(
    "sqlite:///var/dipy_ai.db",
    connect_args={"check_same_thread": False},
    echo=False,
)

Base.metadata.create_all(engine)
