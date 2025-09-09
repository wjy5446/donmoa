"""
Provider 기본 클래스
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, TypeVar
import re
import pandas as pd
from dataclasses import replace

from ..schemas import CashSchema, PositionSchema, TransactionSchema
from ..utils.logger import logger
from ..utils.config import config_manager

# 제네릭 타입 정의
T = TypeVar('T', CashSchema, PositionSchema)


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
    def parse_raw(self, file_path: Path) -> Dict[str, pd.DataFrame]:
        """원본 데이터를 파싱합니다."""
        pass

    @abstractmethod
    def parse_cash(self, data: Dict[str, pd.DataFrame]) -> List[CashSchema]:
        """현금 데이터를 파싱합니다."""
        pass

    @abstractmethod
    def parse_positions(self, data: Dict[str, pd.DataFrame]) -> List[PositionSchema]:
        """포지션 데이터를 파싱합니다."""
        pass

    @abstractmethod
    def parse_transactions(self, data: Dict[str, pd.DataFrame]) -> List[TransactionSchema]:
        """거래 데이터를 파싱합니다."""
        pass

    def collect_all(
        self,
        input_dir: Path
    ) -> Dict[str, Union[List[CashSchema], List[PositionSchema], List[TransactionSchema]]]:
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
                logger.info("")
                logger.info(f"{self.name}: 지원하는 파일을 찾을 수 없습니다 ⚠️")
                logger.info("")
                return result

            logger.info(f"{self.name}: 파일 발견 - {file_path.name}")

            raw_datas = self.parse_raw(file_path)
            # 각 데이터 타입별로 파싱 (하위 클래스의 추상화 함수 호출)
            result["cash"] = self.parse_cash(raw_datas)
            result["positions"] = self.parse_positions(raw_datas)
            result["transactions"] = self.parse_transactions(raw_datas)

            # 계좌 매핑 적용
            result["cash"] = self._apply_account_mapping("cash", result["cash"])
            result["positions"] = self._apply_account_mapping("positions", result["positions"])

            logger.info("")
            logger.info(
                f"데이터 수집 완료 - 현금:{len(result['cash'])}건, "
                f"포지션:{len(result['positions'])}건, 거래:{len(result['transactions'])}건 🟢"
            )
        except Exception as e:
            logger.error(f"데이터 수집 실패 : {e} ❌")
        logger.info("")

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

    # 계좌 매핑 관련
    def add_account_mapping(self, mapping: Dict[str, List[str]]) -> None:
        """계좌 매핑을 설정합니다."""
        self.account_mapping.update(mapping)

    def get_account_mapping(self) -> List[Dict[str, List[str]]]:
        """계좌 매핑을 반환합니다."""
        return self.account_mapping

    def _get_mapped_account_name(self, original_account: str) -> Optional[str]:
        """원본 계좌명을 매핑된 계좌명으로 변환합니다."""
        if not original_account or not self.account_mapping:
            return None

        # 정확한 매칭 시도
        if original_account in self.account_mapping:
            return original_account

        # 부분 매칭 시도 (원본 계좌명이 매핑 키에 포함되는 경우)
        for mapping_key, mapped_names in self.account_mapping.items():
            if original_account in mapped_names:
                return mapping_key

        return None

    def _apply_account_mapping(self, data_type: str, data: List[T]) -> List[T]:
        """데이터에 계좌 매핑을 적용합니다. 매핑되지 않는 데이터는 제외됩니다."""
        if not self.account_mapping:
            logger.info("")
            logger.info(f"{data_type} 계좌 매핑이 설정되지 않아 모든 데이터를 제외합니다 ⚠️")
            return []

        mapped_data = []
        excluded_accounts = set()

        for item in data:
            # 계좌 매핑에서 매칭되는 계좌명 찾기
            mapped_account = self._get_mapped_account_name(item.account)
            if mapped_account:
                mapped_item = replace(item, account=mapped_account)
                mapped_data.append(mapped_item)
            else:
                excluded_accounts.add(item.account)

        if excluded_accounts:
            logger.info("")
            logger.info(f"{data_type} 계좌 매핑되지 않은 데이터 {len(excluded_accounts)}건 제외됨 ⚠️")
            if len(excluded_accounts) <= 2:
                logger.info(f"제외된 계좌명: {', '.join(sorted(excluded_accounts))}")
            else:
                sorted_excluded = sorted(excluded_accounts)
                logger.info(f"제외된 계좌명: {', '.join(sorted_excluded[:2])}, 그외 {len(excluded_accounts) - 2}건")
        return mapped_data

    def get_data_statistics(self) -> Dict[str, Any]:
        """데이터 통계를 반환합니다."""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "mapping_count": len(self.account_mapping),
            "supported_extensions": self.get_supported_extensions(),
            "config": self.provider_config
        }
