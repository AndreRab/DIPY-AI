from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(
    "sqlite:///dipy_ai.db", connect_args={"check_same_thread": False},
    echo=False,
)
def get_db():
    with Session(engine) as session:
        yield session


