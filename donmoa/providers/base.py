"""
기관별 API 연동 모듈의 기본 인터페이스
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from ..utils.logger import logger


class BaseProvider(ABC):
    """기관별 API 연동을 위한 기본 클래스"""

    def __init__(self, name: str, provider_type: str, credentials: Dict[str, str], endpoints: Dict[str, str]):
        self.name = name
        self.provider_type = provider_type
        self.credentials = credentials
        self.endpoints = endpoints
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Donmoa/1.0',
            'Accept': 'application/json'
        })

    @abstractmethod
    def authenticate(self) -> bool:
        """인증을 수행합니다."""
        pass

    @abstractmethod
    def get_balances(self) -> List[Dict[str, Any]]:
        """잔고 정보를 가져옵니다."""
        pass

    @abstractmethod
    def get_transactions(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """거래 내역을 가져옵니다."""
        pass

    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """보유 포지션을 가져옵니다."""
        pass

    def _make_request(self, method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
        """HTTP 요청을 수행합니다."""
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name} API 요청 실패: {e}")
            return None

    def _format_date(self, date: datetime) -> str:
        """날짜를 API 요청에 맞는 형식으로 변환합니다."""
        return date.strftime('%Y-%m-%d')

    def _parse_date(self, date_str: str) -> datetime:
        """API 응답의 날짜 문자열을 datetime 객체로 변환합니다."""
        formats = ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y%m%d', '%Y/%m/%d', '%d/%m/%Y']

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        logger.warning(f"{self.name} 날짜 파싱 실패: {date_str}")
        return datetime.now()

    def collect_all_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """모든 데이터를 수집합니다."""
        if not self.authenticate():
            logger.error(f"{self.name} 인증 실패")
            return {}

        data = {}
        try:
            balances = self.get_balances()
            if balances:
                data['balances'] = balances
                logger.info(f"{self.name} 잔고 수집 완료: {len(balances)}건")

            transactions = self.get_transactions()
            if transactions:
                data['transactions'] = transactions
                logger.info(f"{self.name} 거래내역 수집 완료: {len(transactions)}건")

            positions = self.get_positions()
            if positions:
                data['positions'] = positions
                logger.info(f"{self.name} 포지션 수집 완료: {len(positions)}건")

        except Exception as e:
            logger.error(f"{self.name} 데이터 수집 오류: {e}")

        return data

    def __str__(self):
        return f"{self.name} ({self.provider_type})"
