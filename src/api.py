from typing import List

from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.models_db import Base, Currency
from src.models_api import CurrencyRequest, CurrencyResponse

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


@app.post("/api/v1/currency")
def add_currency(currency: CurrencyRequest, db: Session = Depends(get_db)):
    if currency.name is None or currency.code is None:
        raise HTTPException(status_code=400, detail="Name and code are required")

    db_currency = Currency(name=currency.name, code=currency.code)
    db.add(db_currency)
    db.commit()
    db.refresh(db_currency)

    return db_currency


@app.get("/api/v1/currency", response_model=List[CurrencyResponse])
def get_currencies(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    currencies = db.query(Currency).offset(offset).limit(limit).all()
    return currencies


@app.get("/api/v1/currency/{currency_id}", response_model=CurrencyResponse)
def get_currency(currency_id: int, db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return CurrencyResponse.from_orm(currency)


@app.put("/api/v1/currency/{currency_id}")
def update_currency(currency_id: int, currency: CurrencyRequest, db: Session = Depends(get_db)):
    db_currency = db.query(Currency).filter(Currency.id == currency_id).first()

    if not db_currency:
        return {"error": "Currency not found"}

    if currency.code is not None:
        db_currency.code = currency.code
    if currency.name is not None:
        db_currency.name = currency.name

    db.commit()
    db.refresh(db_currency)

    return CurrencyResponse.from_orm(db_currency)


@app.delete("/api/v1/currency/{currency_id}")
def delete_currency(currency_id: int, db: Session = Depends(get_db)):
    db_currency = db.query(Currency).filter(Currency.id == currency_id).first()

    if not db_currency:
        return {"error": "Currency not found"}

    db.delete(db_currency)
    db.commit()

    return {"message": "Currency deleted successfully"}
