from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base

RARITIES = [
    "Common",
    "Rare",
    "Epic",
    "Legendary",
    "Mythic",
    "Brainrot God",
    "Secret",
    "OG",
]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Brainrot(Base):
    __tablename__ = "brainrots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    rarity: Mapped[str] = mapped_column(String(30), index=True)
    url: Mapped[str] = mapped_column(String(300), default="")
    cost: Mapped[float] = mapped_column(Float, default=0.0)
    income: Mapped[float] = mapped_column(Float, default=0.0)
    event: Mapped[str] = mapped_column(String(80), default="")
    limited: Mapped[bool] = mapped_column(Boolean, default=False)
    added_in_update: Mapped[str] = mapped_column(String(60), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Mutation(Base):
    __tablename__ = "mutations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    multiplier: Mapped[float] = mapped_column(Float)
    permanent: Mapped[bool] = mapped_column(Boolean, default=False)
    event: Mapped[str] = mapped_column(String(80), default="")
    notes: Mapped[str] = mapped_column(Text, default="")


class Trait(Base):
    __tablename__ = "traits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    bonus: Mapped[float] = mapped_column(Float)
    notes: Mapped[str] = mapped_column(Text, default="")


class UpdateLog(Base):
    __tablename__ = "updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    released_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    body: Mapped[str] = mapped_column(Text, default="")
    new_brainrots: Mapped[str] = mapped_column(Text, default="")
    new_mutations: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(300), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class GameEvent(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    event_type: Mapped[str] = mapped_column(String(60), default="")
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str] = mapped_column(Text, default="")
