"""
CSV 내보내기 클래스
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from ..utils.logger import logger
from ..utils.config import config_manager


class CSVExporter:
    """CSV 내보내기 클래스"""

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            output_dir_str = config_manager.get("export.output_dir", "data/export")
            output_dir = Path(output_dir_str)

        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_to_csv(self, integrated_data: Dict[str, List[Dict[str, Any]]], timestamp: Optional[datetime] = None) -> Dict[str, Path]:
        """통합된 데이터를 CSV 파일로 내보냅니다."""
        if timestamp is None:
            timestamp = datetime.now()

        # 타임스탬프 디렉토리 생성
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / timestamp_str
        output_path.mkdir(exist_ok=True)

        exported_files = {}

        # 각 데이터 타입별로 CSV 파일 생성
        for data_type, records in integrated_data.items():
            if records:  # 데이터가 있는 경우만 처리
                filename = f"{data_type}.csv"
                file_path = output_path / filename

                # DataFrame으로 변환하여 저장
                df = pd.DataFrame(records)
                df.to_csv(file_path, index=False, encoding='utf-8')
                exported_files[data_type] = file_path
                logger.info(f"{data_type} CSV 저장: {len(records)}행")

        return exported_files

    def export_provider_data_to_csv(self, collected_data: Dict[str, Dict[str, List[Dict[str, Any]]]], timestamp: Optional[datetime] = None) -> Dict[str, Path]:
        """Provider별 원본 데이터를 CSV 파일로 내보냅니다."""
        if timestamp is None:
            timestamp = datetime.now()

        # 타임스탬프 디렉토리 생성
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / timestamp_str
        output_path.mkdir(exist_ok=True)

        exported_files = {}

        # Provider별 데이터 처리
        for provider_name, provider_data in collected_data.items():
            for data_type, records in provider_data.items():
                if records:  # 데이터가 있는 경우만 처리
                    filename = f"{provider_name}_{data_type}.csv"
                    file_path = output_path / filename

                    # DataFrame으로 변환하여 저장
                    df = pd.DataFrame(records)
                    df.to_csv(file_path, index=False, encoding='utf-8')
                    exported_files[f"{provider_name}_{data_type}"] = file_path
                    logger.info(f"{provider_name} {data_type} CSV 저장: {len(records)}행")

        return exported_files
