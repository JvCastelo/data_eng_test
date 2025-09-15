from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DataBase(BaseModel):

    ts: datetime
    value: float | None = None


class DataCreate(DataBase):

    signal_id: int


class Data(DataBase):

    signal_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SignalBase(BaseModel):

    name: str = Field(..., max_length=255)


class SignalCreate(SignalBase):

    pass


class Signal(SignalBase):

    id: int

    model_config = ConfigDict(from_attributes=True)


class SignalWithData(Signal):

    data_points: list[Data] = []
