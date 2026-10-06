import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class SourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    url: HttpUrl
    source_type: str = Field(default="official", min_length=1, max_length=50)
    description: str | None = None


class SourceUpdate(SourceCreate):
    pass


class SourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    url: str
    source_type: str
    description: str | None
    created_at: datetime
    updated_at: datetime
