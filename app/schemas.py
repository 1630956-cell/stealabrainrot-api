from datetime import datetime

from pydantic import BaseModel, Field


class BrainrotIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    rarity: str
    cost: float = 0.0
    income: float = 0.0
    event: str = ""
    limited: bool = False
    added_in_update: str = ""
    notes: str = ""
    url: str = ""


class BrainrotOut(BrainrotIn):
    id: int
    slug: str

    model_config = {"from_attributes": True}


class MutationIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    multiplier: float = Field(gt=0)
    permanent: bool = False
    event: str = ""
    notes: str = ""


class MutationOut(MutationIn):
    id: int

    model_config = {"from_attributes": True}


class TraitIn(BaseModel):
    name: str = Field(min_length=1, max_length=60)
    bonus: float
    notes: str = ""


class TraitOut(TraitIn):
    id: int

    model_config = {"from_attributes": True}


class UpdateIn(BaseModel):
    version: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=200)
    body: str = ""
    new_brainrots: str = ""
    new_mutations: str = ""
    source: str = ""
    released_at: str | None = None


class UpdateOut(UpdateIn):
    id: int
    released_at: datetime

    model_config = {"from_attributes": True}


class EventIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    event_type: str = ""
    starts_at: str
    ends_at: str
    active: bool = True
    notes: str = ""


class EventOut(EventIn):
    id: int
    starts_at: datetime
    ends_at: datetime
    active: bool

    model_config = {"from_attributes": True}
