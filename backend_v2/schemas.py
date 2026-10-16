"""Bounded input models. Money and revisions are strict integers."""
from datetime import date
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Positive = Annotated[int, Field(gt=0, strict=True)]
Status = Literal['available', 'reserved', 'sold']
EnquiryStatus = Literal['new', 'contacted', 'closed']


class Input(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)


class VehicleCreate(Input):
    make: str = Field(min_length=1, max_length=60)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1900, le=2100, strict=True)
    price_pence: int = Field(ge=0, le=100000000, strict=True)
    approved_facts: list[Annotated[str, Field(min_length=1, max_length=200)]] = Field(default_factory=list, max_length=20)


class VehicleUpdate(Input):
    revision: Positive
    make: str | None = Field(default=None, min_length=1, max_length=60)
    model: str | None = Field(default=None, min_length=1, max_length=80)
    year: int | None = Field(default=None, ge=1900, le=2100, strict=True)
    price_pence: int | None = Field(default=None, ge=0, le=100000000, strict=True)
    approved_facts: list[Annotated[str, Field(min_length=1, max_length=200)]] | None = Field(default=None, max_length=20)
    status: Status | None = None
    archived: bool | None = Field(default=None, strict=True)

    @model_validator(mode='after')
    def changes_required(self):
        changed = self.model_fields_set - {'revision'}
        if not changed or any(getattr(self, key) is None for key in changed):
            raise ValueError('Provide at least one non-null change')
        return self


class EnquiryCreate(Input):
    vehicle_id: Positive
    customer: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=1000)


class EnquiryUpdate(Input):
    revision: Positive
    status: EnquiryStatus


class TaskCreate(Input):
    enquiry_id: Positive
    due_date: date
    note: str = Field(default='', max_length=300)


class TaskUpdate(Input):
    revision: Positive
    due_date: date | None = None
    note: str | None = Field(default=None, max_length=300)
    completed: bool | None = Field(default=None, strict=True)

    @model_validator(mode='after')
    def changes_required(self):
        changed = self.model_fields_set - {'revision'}
        if not changed or any(getattr(self, key) is None for key in changed):
            raise ValueError('Provide at least one non-null change')
        return self
