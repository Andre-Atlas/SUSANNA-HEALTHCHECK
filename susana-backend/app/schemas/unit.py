import uuid

from pydantic import BaseModel, ConfigDict, Field


class UnitBase(BaseModel):
    source_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=250)
    type: str = Field(min_length=1, max_length=80)
    ra: str | None = Field(default=None, max_length=100)
    address: str = Field(min_length=1)
    cep: str | None = Field(default=None, max_length=20)
    phone: str | None = Field(default=None, max_length=80)
    opening_hours: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class UnitCreate(UnitBase):
    external_id: str | None = None


class UnitUpdate(UnitBase):
    external_id: str | None = None


class UnitRead(UnitBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    external_id: str | None = None
