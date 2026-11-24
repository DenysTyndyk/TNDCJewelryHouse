import json
from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from app.models.enums import EventType

MAX_BATCH_SIZE = 50
MAX_METADATA_BYTES = 1024

SERVER_ONLY_EVENTS = frozenset({EventType.Purchase})

MetadataValue = str | int | float | bool | None


class EventIn(BaseModel):
    model_config = {"extra": "forbid"}

    event_type: EventType
    product_id: int | None = Field(default=None, gt=0)
    variant_id: int | None = Field(default=None, gt=0)
    category_id: int | None = Field(default=None, gt=0)
    metadata: dict[str, MetadataValue] | None = None
    source: str | None = Field(default=None, max_length=50)

    @field_validator("event_type")
    @classmethod
    def _client_event_only(cls, value: EventType) -> EventType:
        if value in SERVER_ONLY_EVENTS:
            raise ValueError(f"{value.value} events are recorded by the server")
        return value

    @field_validator("metadata")
    @classmethod
    def _small_flat_metadata(cls, value: dict | None) -> dict | None:
        if value is None:
            return None
        # allow_nan=False: NaN/Infinity are not valid JSON and PostgreSQL JSONB would reject them with a 500.
        encoded = json.dumps(value, allow_nan=False).encode()
        if len(encoded) > MAX_METADATA_BYTES:
            raise ValueError(f"metadata must be at most {MAX_METADATA_BYTES} bytes")
        return value
    
    @model_validator(mode="after")
    def _click_has_algorithm(self) -> "EventIn":
        if self.event_type == EventType.ClickRecommendation and not (self.product_id and self.source):
            raise ValueError("ClickRecommendation needs product_id and source")
        return self


class EventBatchIn(BaseModel):
    events: list[EventIn] = Field(min_length=1, max_length=MAX_BATCH_SIZE)


class EventCountOut(BaseModel):
    day: date
    event_type: EventType
    count: int


class TopProductOut(BaseModel):
    product_id: int
    slug: str
    count: int
