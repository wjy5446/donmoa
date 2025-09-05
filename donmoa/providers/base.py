"""
기관별 데이터 수집 모듈의 기본 인터페이스
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from ..utils.logger import logger


class BaseProvider(ABC):
    """기관별 데이터 수집을 위한 기본 클래스"""

    def __init__(
        self, name: str, provider_type: str, credentials: Dict[str, str] = None
    ):
        self.name = name
        self.provider_type = provider_type
        self.credentials = credentials or {}
        self.account_mapping = {}
        self.enabled = True

        # 데이터 검증을 위한 통계
        self.data_statistics = {
            "total_assets": 0,
            "total_balance": 0,
            "total_positions": 0,
            "last_updated": None,
        }

    @abstractmethod
    def get_file_patterns(self) -> Dict[str, str]:
        """
        Provider가 지원하는 파일 패턴을 반환합니다.

        Returns:
            데이터 타입별 파일 패턴 (예: {'balances': '*.mhtml', 'positions': '*.mhtml'})
        """
        pass

    @abstractmethod
    def parse_raw_data(self, file_paths: Dict[str, Path]) -> Dict[str, pd.DataFrame]:
        """
        raw 데이터 파일을 파싱하여 pandas DataFrame으로 변환합니다.

        Args:
            file_paths: 파싱할 파일 경로들

        Returns:
            데이터 타입별 pandas DataFrame
        """
        pass

    def get_dataframes(self, input_dir: Path) -> Dict[str, pd.DataFrame]:
        """
        입력 디렉토리에서 파일을 찾아 DataFrame으로 변환합니다.

        Args:
            input_dir: 입력 파일이 있는 디렉토리

        Returns:
            데이터 타입별 pandas DataFrame
        """
        try:
            # 1단계: 파일 패턴 가져오기
            file_patterns = self.get_file_patterns()

            # 2단계: 파일 찾기
            found_files = self._find_files(input_dir, file_patterns)

            if not found_files:
                logger.warning(f"{self.name}에서 파일을 찾을 수 없습니다")
                return {}

            # 3단계: raw 데이터 파싱
            logger.info(f"{self.name} raw 데이터 파싱 시작")
            dataframes = self.parse_raw_data(found_files)

            # 4단계: 계좌 매핑 적용
            for data_type, df in dataframes.items():
                if data_type in ["balances", "transactions"] and not df.empty:
                    dataframes[data_type] = self._apply_account_mapping(df, data_type)

            # 5단계: 데이터 검증
            self._validate_dataframes(dataframes)

            logger.info(f"{self.name} DataFrame 변환 완료: {list(dataframes.keys())}")
            return dataframes

        except Exception as e:
            logger.error(f"{self.name} DataFrame 변환 실패: {e}")
            return {}

    def _find_files(self, input_dir: Path, file_patterns: Dict[str, str]) -> Dict[str, Path]:
        """파일 패턴에 맞는 파일들을 찾습니다."""
        found_files = {}

        if not input_dir.exists():
            logger.warning(f"입력 디렉토리가 존재하지 않습니다: {input_dir}")
            return found_files

        for data_type, pattern in file_patterns.items():
            matching_files = list(input_dir.glob(pattern))
            if matching_files:
                # 가장 최근 파일 선택
                latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                found_files[data_type] = latest_file
                logger.info(f"{data_type} 파일 발견: {latest_file}")
            else:
                logger.warning(f"{data_type} 패턴에 맞는 파일을 찾을 수 없습니다: {pattern}")

        return found_files

    def _apply_account_mapping(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """DataFrame에 계좌 매핑을 적용합니다."""
        if not self.account_mapping or df.empty:
            return df

        df = df.copy()

        if "account" in df.columns:
            # 계좌명 매핑 적용
            df["unified_account"] = df["account"].map(
                {v: k for k, v in self.account_mapping.items()}
            ).fillna("미매핑")

        return df

    def _validate_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> None:
        """DataFrame 데이터를 검증합니다."""
        try:
            # 잔고 데이터 검증
            if "balances" in dataframes and not dataframes["balances"].empty:
                balance_total = dataframes["balances"]["balance"].sum()
                self.data_statistics["total_balance"] = balance_total
                logger.info(f"{self.name} 잔고 총합: {balance_total:,.0f}원")

            # 포지션 데이터 검증
            if "positions" in dataframes and not dataframes["positions"].empty:
                if "market_value" in dataframes["positions"].columns:
                    position_total = dataframes["positions"]["market_value"].sum()
                    self.data_statistics["total_positions"] = position_total
                    logger.info(f"{self.name} 포지션 총합: {position_total:,.0f}원")

            # 마지막 업데이트 시간 기록
            self.data_statistics["last_updated"] = datetime.now()

        except Exception as e:
            logger.error(f"{self.name} 데이터 검증 오류: {e}")

    def export_to_csv(self, dataframes: Dict[str, pd.DataFrame], output_dir: Path) -> Dict[str, Path]:
        """
        DataFrame들을 CSV 파일로 내보냅니다.

        Args:
            dataframes: 내보낼 DataFrame들
            output_dir: 출력 디렉토리

        Returns:
            생성된 CSV 파일 경로들
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        exported_files = {}

        for data_type, df in dataframes.items():
            if df.empty:
                continue

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name}_{data_type}_{timestamp}.csv"
            file_path = output_dir / filename

            try:
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                exported_files[data_type] = file_path
                logger.info(f"{self.name} {data_type} CSV 내보내기 완료: {file_path}")
            except Exception as e:
                logger.error(f"{self.name} {data_type} CSV 내보내기 실패: {e}")

        return exported_files

    def get_data_statistics(self) -> Dict[str, Any]:
        """
        데이터 통계를 가져옵니다.

        Returns:
            데이터 통계
        """
        return self.data_statistics.copy()

    def set_account_mapping(self, mapping: Dict[str, str]) -> None:
        """
        계좌 매핑을 설정합니다.

        Args:
            mapping: 계좌 매핑 (통합 계좌명: 원본 계좌명)
        """
        self.account_mapping = mapping
        logger.info(f"{self.name} 계좌 매핑 설정 완료: {len(mapping)}개")

    def is_enabled(self) -> bool:
        """
        Provider가 활성화되어 있는지 확인합니다.

        Returns:
            활성화 여부
        """
        return self.enabled

    def enable(self) -> None:
        """Provider를 활성화합니다."""
        self.enabled = True
        logger.info(f"{self.name} Provider 활성화")

    def disable(self) -> None:
        """Provider를 비활성화합니다."""
        self.enabled = False
        logger.info(f"{self.name} Provider 비활성화")
