"""
Provider 기본 클래스
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import re
import pandas as pd

from ..utils.logger import logger
from ..utils.config import config_manager


class BaseProvider(ABC):
    """모든 Provider의 기본 클래스"""

    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Provider 초기화

        Args:
            name: Provider 이름
            config: donmoa에서 로드한 전체 설정
        """
        self.name = name
        self.enabled = True
        self.account_mapping = {}
        self.config = config or config_manager.config
        self.provider_config = self._load_provider_config()

    def _load_provider_config(self) -> Dict[str, Any]:
        """Provider 설정을 로드합니다."""
        try:
            providers = self.config.get("providers", {})
            return providers.get(self.name, {})
        except Exception as e:
            logger.warning(f"Provider 설정 로드 실패: {e}")
            return {}

    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 목록을 반환합니다."""
        pass

    @abstractmethod
    def parse_cash(self, file_path: Path) -> List[Dict[str, Any]]:
        """현금 데이터를 파싱합니다."""
        pass

    @abstractmethod
    def parse_positions(self, file_path: Path) -> List[Dict[str, Any]]:
        """포지션 데이터를 파싱합니다."""
        pass

    @abstractmethod
    def parse_transactions(self, file_path: Path) -> List[Dict[str, Any]]:
        """거래 데이터를 파싱합니다."""
        pass

    def collect_all(self, input_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        모든 데이터를 수집하고 공통 스키마로 변환합니다.
        하위 클래스에서 추상화 함수만 구현하면 자동으로 동작합니다.
        """
        result = {
            "cash": [],
            "positions": [],
            "transactions": []
        }

        try:
            # 지원하는 파일 찾기
            file_path = self._find_input_file(input_dir)
            if not file_path:
                logger.warning(f"{self.name}: 지원하는 파일을 찾을 수 없습니다")
                return result

            logger.info(f"{self.name}: 파일 발견 - {file_path.name}")

            # 각 데이터 타입별로 파싱 (하위 클래스의 추상화 함수 호출)
            result["cash"] = self._normalize_cash(self.parse_cash(file_path))
            result["positions"] = self._normalize_positions(self.parse_positions(file_path))
            result["transactions"] = self._normalize_transactions(self.parse_transactions(file_path))

            logger.info(f"{self.name}: 데이터 수집 완료 - 현금:{len(result['cash'])}건, "
                       f"포지션:{len(result['positions'])}건, 거래:{len(result['transactions'])}건")

        except Exception as e:
            logger.error(f"{self.name} 데이터 수집 실패: {e}")

        return result

    def _find_input_file(self, input_dir: Path) -> Optional[Path]:
        """입력 파일을 찾습니다."""
        if not input_dir.exists():
            return None

        extensions = self.get_supported_extensions()
        files = []
        for ext in extensions:
            files.extend(input_dir.glob(f"*.{ext}"))

        if not files:
            return None

        # 가장 최근 파일 반환
        return max(files, key=lambda f: f.stat().st_mtime)

    def _normalize_cash(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """현금 데이터를 정규화합니다."""
        normalized = []
        for item in raw_data:
            try:
                normalized.append({
                    'account': str(item.get('account', '')),
                    'balance': self._convert_to_number(item.get('balance', 0)),
                    'currency': item.get('currency', 'KRW'),
                    'provider': self.name,
                    'collected_at': item.get('collected_at', datetime.now().isoformat()),
                })
            except Exception as e:
                logger.warning(f"현금 데이터 정규화 실패: {e}")
        return normalized

    def _normalize_positions(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """포지션 데이터를 정규화합니다."""
        normalized = []
        for item in raw_data:
            try:
                normalized.append({
                    'account': str(item.get('account', '')),
                    'name': item.get('name', ''),
                    'ticker': item.get('ticker', ''),
                    'quantity': self._convert_to_number(item.get('quantity', 0)),
                    'average_price': self._convert_to_number(item.get('average_price', 0)),
                    'currency': item.get('currency', 'KRW'),
                    'provider': self.name,
                    'collected_at': item.get('collected_at', datetime.now().isoformat()),
                })
            except Exception as e:
                logger.warning(f"포지션 데이터 정규화 실패: {e}")
        return normalized

    def _normalize_transactions(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """거래 데이터를 정규화합니다."""
        normalized = []
        for item in raw_data:
            try:
                normalized.append({
                    'date': self._format_date(item.get('date', '')),
                    'transaction_type': item.get('transaction_type', '기타'),
                    'category': item.get('category', ''),
                    'category_detail': item.get('category_detail', ''),
                    'amount': self._convert_to_number(item.get('amount', 0)),
                    'account': str(item.get('account', '')),
                    'currency': item.get('currency', 'KRW'),
                    'note': item.get('note', ''),
                    'provider': self.name,
                    'collected_at': item.get('collected_at', datetime.now().isoformat()),
                })
            except Exception as e:
                logger.warning(f"거래 데이터 정규화 실패: {e}")
        return normalized

    # 공통 유틸리티 메서드들
    def _convert_to_number(self, value: Any) -> float:
        """값을 숫자로 변환합니다."""
        try:
            if pd.isna(value) or value is None:
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = re.sub(r'[^\d.-]', '', value.replace(',', ''))
                return float(cleaned) if cleaned else 0.0
            return 0.0
        except (ValueError, TypeError):
            return 0.0

    def _format_date(self, date_value: Any) -> str:
        """날짜를 YYYY-MM-DD 형식으로 변환합니다."""
        try:
            if pd.isna(date_value) or not date_value:
                return ""
            if isinstance(date_value, str):
                return date_value
            elif hasattr(date_value, 'strftime'):
                return date_value.strftime("%Y-%m-%d")
            else:
                return str(date_value)
        except Exception:
            return ""

    def _extract_number_from_text(self, text: str) -> float:
        """텍스트에서 숫자를 추출합니다."""
        try:
            if not text:
                return 0.0
            cleaned = re.sub(r'[^\d.-]', '', str(text))
            return float(cleaned) if cleaned else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _determine_transaction_type(self, description: str, amount: float) -> str:
        """거래 유형을 판별합니다."""
        if not description:
            return "기타"

        description_lower = description.lower()

        if any(keyword in description_lower for keyword in ["입금", "급여", "월급", "수익"]):
            return "입금"
        elif any(keyword in description_lower for keyword in ["출금", "이체", "송금", "결제", "수수료"]):
            return "출금"
        elif any(keyword in description_lower for keyword in ["이자", "배당"]):
            return "이자"
        else:
            return "입금" if amount > 0 else "출금"

    # 계좌 매핑 관련
    def set_account_mapping(self, mapping: Dict[str, str]) -> None:
        """계좌 매핑을 설정합니다."""
        self.account_mapping = mapping

    def get_account_mapping(self) -> Dict[str, str]:
        """계좌 매핑을 반환합니다."""
        return self.account_mapping

    def get_data_statistics(self) -> Dict[str, Any]:
        """데이터 통계를 반환합니다."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "mapping_count": len(self.account_mapping),
            "supported_extensions": self.get_supported_extensions(),
            "config": self.provider_config
        }
