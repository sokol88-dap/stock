from datetime import datetime, timezone
from typing import Type, Any

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base: Type[Any] = declarative_base()


class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)  # e.g. Dollar, Euro, Pound
    code = Column(String(10), nullable=False, unique=True)  # e.g. USD, EUR, GBP

    stocks = relationship("Stock", back_populates="currency")
    cross_currency_sources = relationship(
        "CrossCurrency", foreign_keys="CrossCurrency.source_id", back_populates="source"
    )
    cross_currency_destinations = relationship(
        "CrossCurrency", foreign_keys="CrossCurrency.destination_id", back_populates="destination"
    )

    def __repr__(self):
        return f"<Currency(name={self.name})>"


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    stock_price = Column(Float, nullable=False)
    date_of_price = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
    open_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)

    currency = relationship("Currency", back_populates="stocks")

    def __repr__(self):
        return (
            f"<Stock(currency_id={self.currency_id}, stock_price={self.stock_price}, "
            f"date_of_price={self.date_of_price})>"
        )


class CrossCurrency(Base):
    __tablename__ = "cross_currency"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    destination_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    cross_price = Column(Float, nullable=False)
    date_of_price = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )
    open_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)

    source = relationship(
        "Currency", foreign_keys=[source_id], back_populates="cross_currency_sources"
    )
    destination = relationship(
        "Currency", foreign_keys=[destination_id], back_populates="cross_currency_destinations"
    )

    def __repr__(self):
        return (
            f"<CrossCurrency(source_id={self.source_id}, destination_id={self.destination_id}, "
            f"cross_price={self.cross_price})>"
        )
