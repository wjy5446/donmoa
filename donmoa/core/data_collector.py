"""
데이터 수집 클래스
"""
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..providers.base import BaseProvider
from ..utils.logger import logger
from ..utils.config import config_manager
from ..utils.date_utils import get_all_date_folders
from ..schemas import CashSchema, PositionSchema, TransactionSchema


class DataCollector:
    """데이터 수집 및 통합 클래스"""

    DATA_TYPES = ['cash', 'positions', 'transactions']

    def __init__(self):
        self.account_mappings: Dict[str, Dict[str, str]] = {}
        self.providers: List[BaseProvider] = []

    def add_provider(self, provider: BaseProvider) -> None:
        """Provider를 추가합니다."""
        self.providers.append(provider)

        # 계좌 매핑이 아직 로드되지 않았다면 로드
        if not self.account_mappings:
            self._set_account_mappings()

        logger.info(f"Provider 추가: {provider.name}")

    def remove_provider(self, provider_name: str) -> None:
        """Provider를 제거합니다."""
        self.providers = [p for p in self.providers if p.name != provider_name]
        self.account_mappings.pop(provider_name, None)
        logger.info(f"Provider 제거: {provider_name}")

    def collect(self, input_dir: Path, provider: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """데이터를 수집합니다."""
        provider = provider or 'all'

        # 입력 디렉토리가 직접 날짜 폴더인지 확인
        from ..utils.date_utils import extract_date_from_folder_name
        folder_date = extract_date_from_folder_name(input_dir)

        if folder_date:
            # 직접 지정된 폴더가 날짜 폴더인 경우
            logger.info(f"지정된 날짜 폴더 사용: {folder_date} ({input_dir})")
            target_folder = input_dir
        else:
            # 가장 최근 날짜 폴더 찾기
            date_folders = get_all_date_folders(input_dir)
            if not date_folders:
                logger.error(f"날짜 폴더를 찾을 수 없습니다: {input_dir}")
                return {data_type: [] for data_type in self.DATA_TYPES}

            latest_date, latest_folder = date_folders[-1]
            logger.info(f"가장 최근 날짜 폴더 선택: {latest_date} ({latest_folder})")
            target_folder = latest_folder
        logger.info("")

        if provider == 'all':
            return self._collect_all_providers(target_folder)
        else:
            return self._collect_single_provider(target_folder, provider)

    def get_collection_summary(self, collected_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """수집 요약 정보를 반환합니다."""

        total_providers = len(self.providers)
        successful_providers = len([p for p in self.providers if p.name in collected_data])
        failed_providers = total_providers - successful_providers

        total_records = sum(
            len(records)
            for records in collected_data.values()
            if isinstance(records, list)
        )
        # 통합된 데이터의 각 데이터 타입별 행 수를 계산하여 summary에 포함
        data_type_counts = {}
        for data_type, records in collected_data.items():
            if isinstance(records, list):
                data_type_counts[data_type] = len(records)
            else:
                data_type_counts[data_type] = 0

        # summary 정보를 로그로 출력
        logger.info("="*50)
        logger.info("🔍 수집 요약")
        logger.info("="*50)

        logger.info(f"✅ Provider {successful_providers}/{total_providers}개 성공, 총 {total_records}개 레코드 📊")
        logger.info(f"💵 현금: {data_type_counts['cash']}건, 📈 포지션: {data_type_counts['positions']}건, 💳 거래: {data_type_counts['transactions']}건")

        return {
            "total_providers": total_providers,
            "successful_providers": successful_providers,
            "failed_providers": failed_providers,
            "success_rate": (successful_providers / total_providers * 100) if total_providers > 0 else 0,
            "total_records": total_records
        }

    def _set_account_mappings(self) -> None:
        """설정에서 계좌 매핑 정보를 로드합니다."""
        try:
            accounts = config_manager.get_accounts()

            for account in accounts:
                account_name = account.get("name")
                mapping_names = account.get("mapping_name", [])

                # 문자열을 리스트로 변환
                if isinstance(mapping_names, str):
                    mapping_names = [mapping_names]

                # 각 매핑명을 모든 Provider에 추가
                for provider in self.providers:
                    provider.add_account_mapping({account_name: mapping_names})
        except Exception as e:
            logger.warning(f"계좌 매핑 설정 실패: {e}")

    def _collect_all_providers(
        self,
        input_dir: Path
    ) -> Dict[str, Union[List[CashSchema], List[PositionSchema], List[TransactionSchema]]]:
        """모든 Provider에서 데이터를 수집하고 통합합니다."""
        collected_data = {}

        # 각 Provider에서 데이터 수집
        for provider in self.providers:
            try:
                logger.info(f"<🔍 {provider.name}: 데이터 수집 시작>")
                provider_data = provider.collect_all(input_dir)

                collected_data[provider.name] = provider_data
            except Exception as e:
                logger.error(f"❌ {provider.name}: {e}")

        # 데이터 통합
        integrated_data = {data_type: [] for data_type in self.DATA_TYPES}

        for provider_data in collected_data.values():
            if provider_data:
                for data_type in self.DATA_TYPES:
                    if data_type in provider_data and provider_data[data_type]:
                        integrated_data[data_type].extend(provider_data[data_type])

        # 폴더 날짜를 스키마에 설정
        self._set_date_for_schemas(integrated_data, input_dir)

        # 통합 결과 로그
        logger.info("데이터 통합 완료")
        logger.info("")

        return integrated_data

    def _collect_single_provider(
        self,
        input_dir: Path,
        provider_name: str
    ) -> Dict[str, Union[List[CashSchema], List[PositionSchema], List[TransactionSchema]]]:
        """특정 Provider에서 데이터를 수집합니다."""
        # Provider 찾기
        target_provider = next((p for p in self.providers if p.name == provider_name), None)

        if target_provider is None:
            logger.error(f"Provider를 찾을 수 없습니다: {provider_name}")
            return {data_type: [] for data_type in self.DATA_TYPES}

        try:
            provider_data = target_provider.collect_all(input_dir)
            if provider_data:
                # 폴더 날짜를 스키마에 설정
                self._set_date_for_schemas(provider_data, input_dir)
                logger.info(f"✅ {provider_name}: {len(provider_data)}개 데이터 타입 수집")
                return provider_data
            else:
                logger.warning(f"⚠️ {provider_name}: 데이터 없음")
        except Exception as e:
            logger.error(f"❌ {provider_name}: {e}")

        return {data_type: [] for data_type in self.DATA_TYPES}

    def _set_date_for_schemas(self, data: Dict[str, List[Any]], input_dir: Path) -> None:
        """폴더 이름에서 추출한 날짜를 스키마의 date 필드에 설정합니다."""
        from ..utils.date_utils import extract_date_from_folder_name

        folder_date = extract_date_from_folder_name(input_dir)

        if not folder_date:
            logger.warning(f"폴더에서 날짜를 추출할 수 없습니다: {input_dir}")
            return

        # 각 데이터 타입별로 date 필드 설정
        for data_type, records in data.items():
            if not records:
                continue
            if data_type == 'transactions':
                continue

            for record in records:
                if hasattr(record, 'date'):
                    record.date = folder_date
                    logger.debug(f"{data_type} 레코드 date 설정: {folder_date}")
