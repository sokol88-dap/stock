from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# Define the database connection details
DATABASE_URL = "postgresql://postgres:postgres@localhost/stocks"
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(bind=engine)

# Create a base class for SQLAlchemy models
Base = declarative_base()


# Define a stock model
class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)


Stock.metadata.create_all(bind=engine)


# Define a request model for adding a new stock
class StockRequest(BaseModel):
    symbol: str
    name: str
    sector: str
    industry: str


# Dependency: get a database session
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


# Create a FastAPI instance
app = FastAPI()


# Create an endpoint for adding a new stock
@app.post("/api/v1/stock")
def add_stock(stock: StockRequest):
    # Create a new stock object
    db_stock = Stock(
        symbol=stock.symbol, name=stock.name, sector=stock.sector, industry=stock.industry
    )

    # Add the stock to the database
    db = SessionLocal()
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)

    # Return the new stock
    return db_stock


@app.get("/api/v1/stock/{symbol}")
def get_stock(symbol: str, db: Session = Depends(get_db)):
    stock = db.query(Stock).filter(Stock.symbol == symbol).first()
    if not stock:
        return {"error": f"Stock with symbol {symbol} not found"}
    return stock
