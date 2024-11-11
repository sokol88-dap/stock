from typing import Optional

from pydantic import BaseModel, Field


class CurrencyRequest(BaseModel):
    name: Optional[str] = Field(None, title="Name of the currency")
    code: Optional[str] = Field(None, title="Code of the currency")


class StockRequest(BaseModel):
    currency_id: int
    stock_price: float
    open_price: float
    close_price: float


class CurrencyResponse(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True


class CrossCurrencyRequest(BaseModel):
    source_id: int
    destination_id: int
    cross_price: float
    open_price: float
    close_price: float
