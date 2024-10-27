from datetime import datetime
from sqlalchemy import String, BigInteger, Index, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("user_username_index", "username"),
        Index("user_created_at_index", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
