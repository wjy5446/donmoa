"""
공통 데이터 스키마 정의
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CashSchema:
    """현금 데이터 스키마"""
    date: str
    category: str
    account: str
    balance: float
    currency: str = "KRW"
    provider: Optional[str] = None
    collected_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "category": self.category,
            "account": self.account,
            "balance": self.balance,
            "currency": self.currency,
            "provider": self.provider,
            "collected_at": self.collected_at
        }


@dataclass
class PositionSchema:
    """포지션 데이터 스키마"""
    date: str
    account: str
    name: str
    ticker: str
    quantity: float
    average_price: float
    currency: str = "KRW"
    provider: Optional[str] = None
    collected_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "account": self.account,
            "name": self.name,
            "ticker": self.ticker,
            "quantity": self.quantity,
            "average_price": self.average_price,
            "currency": self.currency,
            "provider": self.provider,
            "collected_at": self.collected_at
        }


@dataclass
class TransactionSchema:
    """거래 데이터 스키마"""
    date: str
    account: str
    transaction_type: str
    amount: float
    category: str
    category_detail: Optional[str] = None
    currency: str = "KRW"
    note: Optional[str] = None
    provider: Optional[str] = None
    collected_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "account": self.account,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "category": self.category,
            "category_detail": self.category_detail,
            "currency": self.currency,
            "note": self.note,
            "provider": self.provider,
            "collected_at": self.collected_at
        }
