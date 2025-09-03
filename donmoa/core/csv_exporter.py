"""
CSV 내보내기 기능 모듈
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from ..utils.config import config_manager
from ..utils.logger import LoggerMixin


class CSVExporter(LoggerMixin):
    """수집된 데이터를 표준화된 CSV 형식으로 내보내는 클래스"""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        CSVExporter 초기화

        Args:
            output_dir: CSV 파일 출력 디렉토리
        """
        self.output_dir = (
            Path(output_dir)
            if output_dir
            else Path(config_manager.get("export.output_dir", "./export"))
        )
        self.encoding = config_manager.get("export.encoding", "utf-8")

        # 출력 디렉토리 생성
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 표준화된 컬럼 매핑 정의
        self.column_mappings = self._define_column_mappings()

    def _define_column_mappings(self) -> Dict[str, Dict[str, str]]:
        """표준화된 컬럼 매핑을 정의합니다."""
        return {
            "transactions": {
                # 공통 거래 내역 컬럼
                "date": "거래일자",
                "time": "거래시간",
                "type": "거래유형",
                "amount": "거래금액",
                "currency": "통화",
                "description": "거래내용",
                "balance": "잔액",
                "account": "계좌번호",
                "provider": "기관명",
                "category": "카테고리",
                "reference": "참조번호",
            },
            "balances": {
                # 잔고 현황 컬럼
                "account": "계좌번호",
                "account_name": "계좌명",
                "balance": "잔액",
                "currency": "통화",
                "available_balance": "사용가능잔액",
                "frozen_balance": "동결잔액",
                "last_updated": "최종갱신일시",
                "provider": "기관명",
                "account_type": "계좌유형",
            },
            "positions": {
                # 보유 포지션 컬럼
                "symbol": "종목코드",
                "symbol_name": "종목명",
                "quantity": "수량",
                "average_price": "평균단가",
                "current_price": "현재가",
                "market_value": "시장가치",
                "unrealized_pnl": "평가손익",
                "currency": "통화",
                "provider": "기관명",
                "account": "계좌번호",
                "last_updated": "최종갱신일시",
            },
        }

    def standardize_data(
        self, data: List[Dict[str, Any]], data_type: str
    ) -> List[Dict[str, Any]]:
        """
        데이터를 표준화된 형식으로 변환합니다.

        Args:
            data: 원본 데이터
            data_type: 데이터 타입 ('transactions', 'balances', 'positions')

        Returns:
            표준화된 데이터
        """
        if data_type not in self.column_mappings:
            self.logger.warning(f"알 수 없는 데이터 타입: {data_type}")
            return data

        standardized_data = []
        column_map = self.column_mappings[data_type]

        for item in data:
            standardized_item = {}

            # 표준화된 컬럼으로 매핑
            for std_col, korean_name in column_map.items():
                # 원본 데이터에서 해당하는 값 찾기
                value = self._find_matching_value(item, std_col)
                standardized_item[korean_name] = value

            # 추가 메타데이터
            standardized_item["원본데이터"] = json.dumps(item, ensure_ascii=False)
            standardized_data.append(standardized_item)

        return standardized_data

    def _find_matching_value(self, item: Dict[str, Any], std_column: str) -> Any:
        """
        원본 데이터에서 표준 컬럼에 해당하는 값을 찾습니다.

        Args:
            item: 원본 데이터 항목
            std_column: 표준 컬럼명

        Returns:
            찾은 값 또는 None
        """
        # 직접 매칭
        if std_column in item:
            return item[std_column]

        # 유사한 컬럼명 찾기
        possible_matches = {
            "date": [
                "date",
                "datetime",
                "trade_date",
                "transaction_date",
                "일자",
                "날짜",
            ],
            "time": ["time", "trade_time", "transaction_time", "시간"],
            "type": ["type", "transaction_type", "거래유형", "유형"],
            "amount": ["amount", "value", "price", "금액", "가격"],
            "currency": ["currency", "curr", "통화", "화폐"],
            "description": ["description", "desc", "memo", "내용", "설명"],
            "balance": ["balance", "잔액", "잔고"],
            "account": ["account", "account_no", "계좌", "계좌번호"],
            "provider": ["provider", "institution", "기관", "기관명"],
            "category": ["category", "cat", "카테고리", "분류"],
            "reference": ["reference", "ref", "ref_no", "참조", "참조번호"],
            "symbol": ["symbol", "code", "ticker", "종목코드", "코드"],
            "symbol_name": ["symbol_name", "name", "종목명", "이름"],
            "quantity": ["quantity", "qty", "amount", "수량"],
            "average_price": ["average_price", "avg_price", "평균단가"],
            "current_price": ["current_price", "price", "현재가"],
            "market_value": ["market_value", "value", "시장가치"],
            "unrealized_pnl": ["unrealized_pnl", "pnl", "손익", "평가손익"],
            "account_name": ["account_name", "account_title", "계좌명"],
            "available_balance": ["available_balance", "available", "사용가능잔액"],
            "frozen_balance": ["frozen_balance", "frozen", "동결잔액"],
            "last_updated": ["last_updated", "updated_at", "최종갱신일시"],
            "account_type": ["account_type", "type", "계좌유형"],
        }

        if std_column in possible_matches:
            for possible_match in possible_matches[std_column]:
                if possible_match in item:
                    return item[possible_match]

        return None

    def export_to_csv(
        self,
        collected_data: Dict[str, Dict[str, List[Dict[str, Any]]]],
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Path]:
        """
        수집된 데이터를 CSV 파일로 내보냅니다.

        Args:
            collected_data: 수집된 데이터
            timestamp: 내보내기 타임스탬프 (None이면 현재 시간)

        Returns:
            생성된 CSV 파일 경로들
        """
        if timestamp is None:
            timestamp = datetime.now()

        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        exported_files = {}

        # 각 데이터 타입별로 CSV 파일 생성
        for data_type in ["transactions", "balances", "positions"]:
            all_data = []

            # 모든 Provider의 해당 데이터 타입 수집
            for provider_name, provider_data in collected_data.items():
                if data_type in provider_data and provider_data[data_type]:
                    # Provider 정보 추가
                    for item in provider_data[data_type]:
                        item_copy = item.copy()
                        item_copy["provider"] = provider_name
                        all_data.append(item_copy)

            if all_data:
                # 데이터 표준화
                standardized_data = self.standardize_data(all_data, data_type)

                # DataFrame 생성
                df = pd.DataFrame(standardized_data)

                # CSV 파일명 생성
                filename = f"{data_type}_{timestamp_str}.csv"
                file_path = self.output_dir / filename

                # CSV 파일로 저장
                df.to_csv(file_path, index=False, encoding=self.encoding)

                exported_files[data_type] = file_path
                self.logger.info(
                    f"{data_type} CSV 내보내기 완료: {file_path} ({len(standardized_data)}건)"
                )
            else:
                self.logger.warning(
                    f"{data_type} 데이터가 없어 CSV 파일을 생성하지 않습니다"
                )

        # 내보내기 요약 파일 생성
        summary_file = self._create_export_summary(
            collected_data, timestamp, exported_files
        )
        exported_files["summary"] = summary_file

        return exported_files

    def _create_export_summary(
        self,
        collected_data: Dict[str, Dict[str, List[Dict[str, Any]]]],
        timestamp: datetime,
        exported_files: Dict[str, Path],
    ) -> Path:
        """
        내보내기 요약 파일을 생성합니다.

        Args:
            collected_data: 수집된 데이터
            timestamp: 내보내기 타임스탬프
            exported_files: 내보낸 파일들

        Returns:
            요약 파일 경로
        """
        summary = {
            "export_timestamp": timestamp.isoformat(),
            "exported_files": {k: str(v) for k, v in exported_files.items()},
            "data_summary": {},
            "total_records": 0,
        }

        # 데이터 요약 정보
        for data_type in ["transactions", "balances", "positions"]:
            type_count = 0
            for provider_data in collected_data.values():
                if data_type in provider_data:
                    type_count += len(provider_data[data_type])

            summary["data_summary"][data_type] = type_count
            summary["total_records"] += type_count

        # 요약 파일 저장
        summary_file = (
            self.output_dir
            / f"export_summary_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        )

        with open(summary_file, "w", encoding=self.encoding) as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

        self.logger.info(f"내보내기 요약 파일 생성 완료: {summary_file}")
        return summary_file

    def export_provider_specific_csv(
        self,
        collected_data: Dict[str, Dict[str, List[Dict[str, Any]]]],
        provider_name: str,
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Path]:
        """
        특정 Provider의 데이터만 별도로 CSV로 내보냅니다.

        Args:
            collected_data: 수집된 데이터
            provider_name: Provider 이름
            timestamp: 내보내기 타임스탬프

        Returns:
            생성된 CSV 파일 경로들
        """
        if timestamp is None:
            timestamp = datetime.now()

        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        exported_files = {}

        if provider_name not in collected_data:
            self.logger.warning(f"Provider '{provider_name}'의 데이터가 없습니다")
            return exported_files

        provider_data = collected_data[provider_name]

        # 각 데이터 타입별로 CSV 파일 생성
        for data_type in ["transactions", "balances", "positions"]:
            if data_type in provider_data and provider_data[data_type]:
                # 데이터 표준화
                standardized_data = self.standardize_data(
                    provider_data[data_type], data_type
                )

                # DataFrame 생성
                df = pd.DataFrame(standardized_data)

                # CSV 파일명 생성 (Provider별)
                filename = f"{provider_name}_{data_type}_{timestamp_str}.csv"
                file_path = self.output_dir / filename

                # CSV 파일로 저장
                df.to_csv(file_path, index=False, encoding=self.encoding)

                exported_files[data_type] = file_path
                self.logger.info(
                    f"{provider_name} {data_type} CSV 내보내기 완료: {file_path} ({len(standardized_data)}건)"
                )

        return exported_files

    def get_export_statistics(self, exported_files: Dict[str, Path]) -> Dict[str, Any]:
        """
        내보내기 통계 정보를 반환합니다.

        Args:
            exported_files: 내보낸 파일들

        Returns:
            내보내기 통계 정보
        """
        stats = {
            "total_files": len(exported_files),
            "file_sizes": {},
            "total_size_bytes": 0,
            "exported_at": datetime.now().isoformat(),
        }

        for file_type, file_path in exported_files.items():
            if file_path.exists():
                file_size = file_path.stat().st_size
                stats["file_sizes"][file_type] = {
                    "path": str(file_path),
                    "size_bytes": file_size,
                    "size_mb": round(file_size / (1024 * 1024), 2),
                }
                stats["total_size_bytes"] += file_size

        stats["total_size_mb"] = round(stats["total_size_bytes"] / (1024 * 1024), 2)

        return stats

    def export_donmoa_format_csv(
        self,
        collected_data: Dict[str, Dict[str, List[Dict[str, Any]]]],
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Path]:
        """
        donmoa 형태의 CSV 파일을 내보냅니다.
        (position.csv와 cash.csv 형태)

        Args:
            collected_data: 수집된 데이터
            timestamp: 내보내기 타임스탬프 (None이면 현재 시간)

        Returns:
            생성된 CSV 파일 경로들
        """
        if timestamp is None:
            timestamp = datetime.now()

        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        date_str = timestamp.strftime("%Y%m%d")
        exported_files = {}

        # 날짜별 폴더 생성
        date_dir = self.output_dir / date_str
        date_dir.mkdir(exist_ok=True)

        # position.csv 생성 (계좌별 자산 보유량)
        position_data = []
        for provider_name, provider_data in collected_data.items():
            if "positions" in provider_data and provider_data["positions"]:
                for item in provider_data["positions"]:
                    position_data.append({
                        '계좌명': item.get('account', ''),
                        '자산명': item.get('symbol_name', ''),
                        '티커': item.get('symbol', ''),
                        '보유량': item.get('quantity', 0),
                        '평단가': item.get('average_price', 0),
                        '수행일시': timestamp_str
                    })

        if position_data:
            # DataFrame 생성
            df_position = pd.DataFrame(position_data)

            # CSV 파일명 생성
            filename = "position.csv"
            file_path = date_dir / filename

            # CSV 파일로 저장
            df_position.to_csv(file_path, index=False, encoding='utf-8-sig')

            exported_files["position"] = file_path
            self.logger.info(
                f"position CSV 내보내기 완료: {file_path} ({len(position_data)}건)"
            )

        # cash.csv 생성 (현금 보유량)
        cash_data = []
        for provider_name, provider_data in collected_data.items():
            if "balances" in provider_data and provider_data["balances"]:
                for item in provider_data["balances"]:
                    # 현금성 자산만 필터링
                    if '현금' in item.get('account', '') or item.get('currency', '') in ['원', '달러', '엔']:
                        cash_data.append({
                            '자산명': item.get('currency', ''),
                            '보유량': item.get('balance', 0),
                            '수행일시': timestamp_str
                        })

        if cash_data:
            # DataFrame 생성
            df_cash = pd.DataFrame(cash_data)

            # CSV 파일명 생성
            filename = "cash.csv"
            file_path = date_dir / filename

            # CSV 파일로 저장
            df_cash.to_csv(file_path, index=False, encoding='utf-8-sig')

            exported_files["cash"] = file_path
            self.logger.info(
                f"cash CSV 내보내기 완료: {file_path} ({len(cash_data)}건)"
            )

        return exported_files
