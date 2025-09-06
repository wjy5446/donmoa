"""
공통 데이터 스키마 정의
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class CashSchema:
    """현금 데이터 스키마"""
    account: str
    balance: float
    currency: str = "KRW"
    provider: Optional[str] = None
    collected_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "account": self.account,
            "balance": self.balance,
            "currency": self.currency,
            "provider": self.provider,
            "collected_at": self.collected_at
        }


@dataclass
class PositionSchema:
    """포지션 데이터 스키마"""
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
    transaction_type: str
    category: str
    category_detail: str
    amount: float
    currency: str = "KRW"
    note: Optional[str] = None
    provider: Optional[str] = None
    collected_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "account": self.account,
            "transaction_type": self.transaction_type,
            "category": self.category,
            "category_detail": self.category_detail,
            "amount": self.amount,
            "currency": self.currency,
            "note": self.note,
            "provider": self.provider,
            "collected_at": self.collected_at
        }


class DataSchema:
    """공통 데이터 스키마 클래스"""

    @staticmethod
    def validate_cash(data: Dict[str, Any]) -> bool:
        """현금 데이터 검증"""
        required_fields = ["account", "balance", "currency"]
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_position(data: Dict[str, Any]) -> bool:
        """포지션 데이터 검증"""
        required_fields = ["account", "name", "ticker", "quantity", "average_price"]
        return all(field in data for field in required_fields)

    @staticmethod
    def validate_transaction(data: Dict[str, Any]) -> bool:
        """거래 데이터 검증"""
        required_fields = ["date", "transaction_type", "category", "category_detail", "amount", "account"]
        return all(field in data for field in required_fields)

    @staticmethod
    def normalize_cash(data: Dict[str, Any]) -> CashSchema:
        """현금 데이터 정규화"""
        return CashSchema(
            account=data["account"],
            balance=float(data["balance"]),
            currency=data.get("currency", "KRW"),
            provider=data.get("provider"),
            collected_at=data.get("collected_at")
        )

    @staticmethod
    def normalize_position(data: Dict[str, Any]) -> PositionSchema:
        """포지션 데이터 정규화"""
        return PositionSchema(
            account=data["account"],
            name=data["name"],
            ticker=data["ticker"],
            quantity=float(data["quantity"]),
            average_price=float(data.get("average_price", 0)),
            currency=data.get("currency", "KRW"),
            provider=data.get("provider"),
            collected_at=data.get("collected_at")
        )

    @staticmethod
    def normalize_transaction(data: Dict[str, Any]) -> TransactionSchema:
        """거래 데이터 정규화"""
        return TransactionSchema(
            date=data["date"],
            transaction_type=data["transaction_type"],
            category=data["category"],
            category_detail=data["category_detail"],
            amount=float(data["amount"]),
            note=data.get("note"),
            currency=data.get("currency", "KRW"),
            provider=data.get("provider"),
            collected_at=data.get("collected_at")
        )
