from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from datetime import datetime
from typing import List

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    urls: Mapped[List["Url"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Url(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url: Mapped[str] = mapped_column(nullable=False)
    token: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    owner: Mapped["User"] = relationship(back_populates="urls")

    visits: Mapped[List["Visit"]] = relationship(back_populates="url", cascade="all, delete-orphan")

class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    url_id: Mapped[int] = mapped_column(ForeignKey("urls.id", ondelete="CASCADE"))
    url: Mapped["Url"] = relationship(back_populates="visits")