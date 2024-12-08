from typing import List

from fastapi import FastAPI, HTTPException, APIRouter, Depends, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.models_db import Base, Currency, Stock
from src.models_api import (
    CurrencyRequest,
    CurrencyResponse,
    PaginatedCurrencyResponse,
    StockRequest,
    StockResponse,
)

# Define the database connection details
DATABASE_URL = "postgresql://postgres:postgres@localhost/stocks"
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)


# Dependency: get a database session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Create a FastAPI instance
app = FastAPI()
currency_router = APIRouter()
stock_router = APIRouter()


# Define the routes for the currency API
@currency_router.get(
    "/api/v1/currency", response_model=PaginatedCurrencyResponse, tags=["Currency"]
)
def get_currencies(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    total = db.query(Currency).count()
    currencies = db.query(Currency).offset(offset).limit(limit).all()

    next_page = None
    if offset + limit < total:
        next_page = f"/api/v1/currency?limit={limit}&offset={offset + limit}"

    previous_page = None
    if offset > 0:
        previous_offset = max(0, offset - limit)
        previous_page = f"/api/v1/currency?limit={limit}&offset={previous_offset}"

    return PaginatedCurrencyResponse(
        total=total,
        items=[CurrencyResponse.from_orm(currency) for currency in currencies],
        next_page=next_page,
        previous_page=previous_page,
    )


@currency_router.post("/api/v1/currency", response_model=CurrencyResponse, tags=["Currency"])
def add_currency(currency: CurrencyRequest, db: Session = Depends(get_db)):
    if currency.name is None or currency.code is None or currency.num is None:
        raise HTTPException(status_code=400, detail="Name, code and num are required")

    if (
        db.query(Currency)
        .filter(
            (Currency.name == currency.name)
            | (Currency.code == currency.code)
            | (Currency.num == currency.num)
        )
        .first()
    ):
        raise HTTPException(status_code=400, detail="Such currency already exists")

    try:
        db_currency = Currency(name=currency.name, code=currency.code, num=currency.num)
        db.add(db_currency)
        db.commit()
        db.refresh(db_currency)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return CurrencyResponse.from_orm(db_currency)


@currency_router.get(
    "/api/v1/currency/{currency_id}", response_model=CurrencyResponse, tags=["Currency"]
)
def get_currency(currency_id: int, db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return CurrencyResponse.from_orm(currency)


@currency_router.put(
    "/api/v1/currency/{currency_id}", response_model=CurrencyResponse, tags=["Currency"]
)
def update_currency(currency_id: int, currency: CurrencyRequest, db: Session = Depends(get_db)):
    db_currency = db.query(Currency).filter(Currency.id == currency_id).first()

    if not db_currency:
        raise HTTPException(status_code=404, detail="Currency not found")

    if currency.code is not None and db_currency.code != currency.code:
        if db.query(Currency).filter(Currency.code == currency.code).first():
            raise HTTPException(status_code=400, detail="Currency with such code already exists")
        db_currency.code = currency.code
    if currency.name is not None and db_currency.name != currency.name:
        if db.query(Currency).filter(Currency.name == currency.name).first():
            raise HTTPException(status_code=400, detail="Currency with such name already exists")
        db_currency.name = currency.name
    if currency.num is not None and db_currency.num != currency.num:
        if db.query(Currency).filter(Currency.num == currency.num).first():
            raise HTTPException(status_code=400, detail="Currency with such num already exists")
        db_currency.num = currency.num

    db.commit()
    db.refresh(db_currency)

    return CurrencyResponse.from_orm(db_currency)


@currency_router.delete("/api/v1/currency/{currency_id}", tags=["Currency"])
def delete_currency(currency_id: int, db: Session = Depends(get_db)):
    db_currency = db.query(Currency).filter(Currency.id == currency_id).first()

    if not db_currency:
        return {"error": "Currency not found"}

    db.delete(db_currency)
    db.commit()

    return {"message": "Currency deleted successfully"}


# Define the routes for the stock API
@stock_router.get("/api/v1/stock", response_model=List[StockResponse], tags=["Stock"])
def get_stocks(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    return db.query(Stock).offset(offset).limit(limit).all()


@stock_router.post("/api/v1/stock", response_model=StockResponse, tags=["Stock"])
def add_stock(stock: StockRequest, db: Session = Depends(get_db)):
    db_stock = Stock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return StockResponse.from_orm(db_stock)


@stock_router.get("/api/v1/stock/{stock_id}", response_model=StockResponse, tags=["Stock"])
def get_stock(stock_id: int, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")
    return stock


@stock_router.put("/api/v1/stock/{stock_id}", response_model=StockResponse, tags=["Stock"])
def update_stock(stock_id: int, stock: StockRequest, db: Session = Depends(get_db)):
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not db_stock:
        return {"error": "Stock not found"}
    for key, value in stock.dict().items():
        if getattr(db_stock, key) != value:
            setattr(db_stock, key, value)
    db.commit()
    db.refresh(db_stock)
    return StockResponse.from_orm(db_stock)


@stock_router.delete("/api/v1/stock/{stock_id}", response_model=StockResponse, tags=["Stock"])
def delete_stock(stock_id: int, db: Session = Depends(get_db)):
    db_stock = db.query(Stock).filter(Stock.id == stock_id).first()
    if not db_stock:
        return {"error": "Stock not found"}
    db.delete(db_stock)
    db.commit()
    return {"message": "Stock deleted successfully"}


app.include_router(currency_router)
app.include_router(stock_router)
