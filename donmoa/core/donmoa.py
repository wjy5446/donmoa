"""
Donmoa 메인 클래스
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..providers.base import BaseProvider
from ..utils.logger import logger
from ..utils.config import config_manager
from .data_collector import DataCollector
from .csv_exporter import CSVExporter


class Donmoa:
    """Donmoa 메인 클래스"""

    def __init__(self):
        self.data_collector = DataCollector()
        self.csv_exporter = CSVExporter()

        self._register_default_providers()

    def run_full_workflow(self, input_dir: str = "data/input", output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """전체 워크플로우를 실행합니다."""
        logger.info("✅ Donmoa 워크플로우 시작")

        try:
            # 1. 데이터 수집 (통합된 데이터)
            collected_data = self.collect(input_dir)

            if not collected_data:
                return {"status": "error", "message": "수집된 데이터가 없습니다"}

            # 2. CSV 내보내기
            exported_files = self.export_to_csv(collected_data, output_dir)

            # 결과 요약
            summary = self.data_collector.get_collection_summary(collected_data)
            total_records = summary.get("total_records", 0)

            result = {
                "status": "success",
                "providers": self.list_providers(),
                "total_records": total_records,
                "exported_files": {k: str(v) for k, v in exported_files.items()},
                "collection_summary": summary
            }

            logger.info(f"✅ 워크플로우 완료: {total_records}개 레코드, {len(exported_files)}개 파일")
            return result

        except Exception as e:
            logger.error(f"❌ 워크플로우 실행 실패: {e}")
            return {"status": "error", "message": str(e)}

    def get_status(self) -> Dict[str, Any]:
        """현재 상태를 반환합니다."""
        return {
            "providers": {
                "total": len(self.data_collector.providers),
                "names": self.list_providers()
            },
            "configuration": {
                "output_directory": str(self.csv_exporter.output_dir),
                "input_directory": "data/input"
            },
            "timestamp": datetime.now().isoformat()
        }

    def collect(
        self,
        input_dir: str = "data/input",
        provider: Union[str, None] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        데이터를 수집합니다.

        Args:
            input_dir: 입력 파일 디렉토리
            provider: 'all' 또는 특정 provider 이름. None이면 'all'로 처리

        Returns:
            통합된 데이터 (provider='all' 또는 None) 또는 특정 provider 데이터
        """
        input_path = Path(input_dir)
        collected_data = self.data_collector.collect(input_path, provider)

        return collected_data

    def export_to_csv(
        self,
        data: Optional[Dict[str, List[Dict[str, Any]]]] = None,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Path]:
        """데이터를 CSV로 내보냅니다."""

        if output_dir:
            self.csv_exporter.output_dir = output_dir

        return self.csv_exporter.export_to_csv(data)

    def _register_default_providers(self) -> None:
        """설정에서 기본 Provider들을 등록합니다."""
        try:
            # 전체 설정을 Provider들에게 전달
            full_config = config_manager.config

            # 도미노 Provider 등록
            from ..providers.domino import DominoProvider
            domino_provider = DominoProvider("domino", full_config)
            self.add_provider(domino_provider)

            # 뱅크샐러드 Provider 등록
            from ..providers.banksalad import BanksaladProvider
            banksalad_provider = BanksaladProvider("banksalad", full_config)
            self.add_provider(banksalad_provider)

        except Exception as e:
            logger.warning(f"기본 Provider 등록 실패: {e}")

    def add_provider(self, provider: BaseProvider) -> None:
        """Provider를 추가합니다."""
        self.data_collector.add_provider(provider)

    def remove_provider(self, provider_name: str) -> None:
        """Provider를 제거합니다."""
        self.data_collector.remove_provider(provider_name)

    def list_providers(self) -> List[str]:
        """등록된 Provider 목록을 반환합니다."""
        return [p.name for p in self.data_collector.providers]
