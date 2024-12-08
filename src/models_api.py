from typing import Optional

from pydantic import BaseModel, Field


class CurrencyRequest(BaseModel):
    name: str = Field(None, title="Name of the currency ISO 4217", example="United States dollar")
    code: str = Field(None, title="Code of the currency ISO 4217", example="USD")
    num: int = Field(None, title="Numeric code of the currency ISO 4217", example=840)


class CurrencyResponse(CurrencyRequest):
    id: int

    class Config:
        orm_mode = True


class PaginatedCurrencyResponse(BaseModel):
    items: list[CurrencyResponse]
    total: int
    next_page: Optional[str] = None
    previous_page: Optional[str] = None


class StockRequest(BaseModel):
    currency_id: Optional[int] = Field(None, title="ID of the currency")
    stock_price: Optional[float] = Field(None, title="Price of the stock")
    open_price: Optional[float] = Field(None, title="Price of the stock in the morning")
    close_price: Optional[float] = Field(None, title="Price of the stock in the evening")
    date_of_price: Optional[str] = Field(None, title="Date of the price")


class StockResponse(StockRequest):
    id: int
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True


class CrossCurrencyRequest(BaseModel):
    source_id: int
    destination_id: int
    cross_price: float
    open_price: float
    close_price: float
