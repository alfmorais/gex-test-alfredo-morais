from datetime import datetime

from sqlmodel import Field, SQLModel


class Lead(SQLModel, table=True):
    __tablename__ = "leads"

    id: int | None = Field(
        default=None,
        primary_key=True,
    )

    name: str
    email: str = Field(
        unique=True,
        index=True,
    )
    phone: str | None = None

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
