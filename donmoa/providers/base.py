"""
기관별 데이터 수집 모듈의 기본 인터페이스
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

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
    def download_data(self, output_dir: Path) -> Dict[str, Path]:
        """
        수동 파일에서 데이터를 읽습니다.

        Args:
            output_dir: 파일이 있는 디렉토리

        Returns:
            읽은 파일 경로들
        """
        pass

    def read_manual_files(
        self, input_dir: Path, file_patterns: Dict[str, str]
    ) -> Dict[str, Path]:
        """
        수동으로 다운로드한 파일들을 읽습니다.

        Args:
            input_dir: 파일이 있는 디렉토리
            file_patterns: 파일 타입별 패턴 (예: {'balances': '*.csv', 'positions': '*.html'})

        Returns:
            파일 타입별 파일 경로들
        """
        found_files = {}

        if not input_dir.exists():
            logger.warning(f"입력 디렉토리가 존재하지 않습니다: {input_dir}")
            return found_files

        for data_type, pattern in file_patterns.items():
            matching_files = list(input_dir.glob(pattern))
            if matching_files:
                # 가장 최근 파일 선택 (수정 시간 기준)
                latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                found_files[data_type] = latest_file
                logger.info(f"{data_type} 파일 발견: {latest_file}")
            else:
                msg = f"{data_type} 패턴에 맞는 파일을 찾을 수 없습니다: {pattern}"
                logger.warning(msg)

        return found_files

    def collect_data_from_files(
        self, input_dir: Path, file_patterns: Dict[str, str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        수동 파일에서 데이터를 수집합니다.

        Args:
            input_dir: 파일이 있는 디렉토리
            file_patterns: 파일 타입별 패턴

        Returns:
            수집된 데이터
        """
        try:
            # 1단계: 파일 읽기
            logger.info(f"{self.name} 수동 파일 읽기 시작")
            found_files = self.read_manual_files(input_dir, file_patterns)

            if not found_files:
                logger.error(f"{self.name} 수동 파일을 찾을 수 없습니다")
                return {}

            # 2단계: 데이터 파싱
            logger.info(f"{self.name} 데이터 파싱 시작")
            parsed_data = self.parse_data(found_files)

            if not parsed_data:
                logger.error(f"{self.name} 데이터 파싱 실패")
                return {}

            # 3단계: 계좌 매핑 적용
            for data_type, data_list in parsed_data.items():
                if data_type in ["balances", "transactions"]:
                    parsed_data[data_type] = self.apply_account_mapping(data_list)

            # 4단계: 데이터 검증
            validation_result = self.validate_data(parsed_data)
            logger.info(f"{self.name} 데이터 검증 완료: {validation_result['status']}")

            # 검증 결과를 데이터에 포함
            parsed_data["_validation"] = validation_result

            return parsed_data

        except Exception as e:
            logger.error(f"{self.name} 수동 파일 데이터 수집 실패: {e}")
            return {}

    def collect_all_data(self, output_dir: Path) -> Dict[str, List[Dict[str, Any]]]:
        """
        모든 데이터를 수집합니다.

        Args:
            output_dir: 데이터 다운로드 및 임시 저장 디렉토리

        Returns:
            수집된 데이터
        """
        try:
            # 1단계: 데이터 다운로드
            logger.info(f"{self.name} 데이터 다운로드 시작")
            downloaded_files = self.download_data(output_dir)

            if not downloaded_files:
                logger.error(f"{self.name} 데이터 다운로드 실패")
                return {}

            # 2단계: 데이터 파싱
            logger.info(f"{self.name} 데이터 파싱 시작")
            parsed_data = self.parse_data(downloaded_files)

            if not parsed_data:
                logger.error(f"{self.name} 데이터 파싱 실패")
                return {}

            # 3단계: 계좌 매핑 적용
            for data_type, data_list in parsed_data.items():
                if data_type in ["balances", "transactions"]:
                    parsed_data[data_type] = self.apply_account_mapping(data_list)

            # 4단계: 데이터 검증
            validation_result = self.validate_data(parsed_data)
            logger.info(f"{self.name} 데이터 검증 완료: {validation_result['status']}")

            # 검증 결과를 데이터에 포함
            parsed_data["_validation"] = validation_result

            return parsed_data

        except Exception as e:
            logger.error(f"{self.name} 데이터 수집 실패: {e}")
            return {}

    @abstractmethod
    def parse_data(
        self, file_paths: Dict[str, Path]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        파일을 파싱하여 구조화된 데이터로 변환합니다.

        Args:
            file_paths: 파싱할 파일 경로들

        Returns:
            파싱된 데이터
        """
        pass

    def apply_account_mapping(
        self, data_list: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        계좌 매핑을 적용합니다.

        Args:
            data_list: 원본 데이터 리스트

        Returns:
            계좌 매핑이 적용된 데이터 리스트
        """
        if not self.account_mapping:
            return data_list

        mapped_data = []
        for item in data_list:
            mapped_item = item.copy()

            # 계좌명 매핑 적용
            if "account_name" in mapped_item:
                original_account = mapped_item["account_name"]
                for unified_account, mapped_account in self.account_mapping.items():
                    if original_account == mapped_account:
                        mapped_item["unified_account"] = unified_account
                        break
                else:
                    mapped_item["unified_account"] = "미매핑"

            mapped_data.append(mapped_item)

        return mapped_data

    def validate_data(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        데이터를 검증합니다.

        Args:
            data: 검증할 데이터

        Returns:
            검증 결과
        """
        validation_result = {
            "status": "success",
            "errors": [],
            "warnings": [],
            "total_records": 0,
            "total_assets": 0,
        }

        try:
            # 총 레코드 수 계산
            for data_type, data_list in data.items():
                if data_type != "_validation":
                    validation_result["total_records"] += len(data_list)

            # 잔고 데이터 검증
            if "balances" in data:
                balances = data["balances"]
                total_balance = sum(
                    float(item.get("balance", 0))
                    for item in balances
                    if item.get("balance")
                )
                validation_result["total_assets"] = total_balance
                self.data_statistics["total_balance"] = total_balance

            # 포지션 데이터 검증
            if "positions" in data:
                positions = data["positions"]
                total_positions = sum(
                    float(item.get("market_value", 0))
                    for item in positions
                    if item.get("market_value")
                )
                validation_result["total_positions"] = total_positions
                self.data_statistics["total_positions"] = total_positions

            # 데이터 일관성 검증
            if (
                validation_result["total_assets"] > 0
                and validation_result["total_positions"] > 0
            ):
                difference = abs(
                    validation_result["total_assets"]
                    - validation_result["total_positions"]
                )
                if difference > 1000:  # 1000원 이상 차이나면 경고
                    validation_result["warnings"].append(
                        f"잔고와 포지션 총액 차이: {difference:,.0f}원"
                    )

            # 마지막 업데이트 시간 기록
            self.data_statistics["last_updated"] = datetime.now()

        except Exception as e:
            validation_result["status"] = "error"
            validation_result["errors"].append(f"데이터 검증 오류: {e}")

        return validation_result

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
