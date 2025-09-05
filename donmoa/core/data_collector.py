"""
데이터 수집 핵심 클래스 - pandas DataFrame 기반
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from ..providers.base import BaseProvider
from ..utils.config import config_manager
from ..utils.logger import LoggerMixin


class DataCollector(LoggerMixin):
    """여러 기관의 데이터를 수집하고 통합하는 핵심 클래스 - pandas DataFrame 기반"""

    def __init__(self, providers: Optional[List[BaseProvider]] = None):
        """
        DataCollector 초기화

        Args:
            providers: 데이터 수집할 Provider 목록
        """
        self.providers = providers or []
        self.collected_dataframes: Dict[str, Dict[str, pd.DataFrame]] = {}
        self.integrated_dataframes: Dict[str, pd.DataFrame] = {}
        self.collection_stats: Dict[str, Dict[str, Any]] = {}
        self.validation_results: Dict[str, Dict[str, Any]] = {}

        # 설정에서 기본값 로드
        self.retry_count = config_manager.get("providers.retry_count", 3)
        self.timeout = config_manager.get("providers.timeout", 30)

    def add_provider(self, provider: BaseProvider) -> None:
        """
        Provider를 추가합니다.

        Args:
            provider: 추가할 Provider 인스턴스
        """
        self.providers.append(provider)
        self.logger.info(f"Provider 추가: {provider}")

    def remove_provider(self, provider_name: str) -> None:
        """
        Provider를 제거합니다.

        Args:
            provider_name: 제거할 Provider 이름
        """
        self.providers = [p for p in self.providers if p.name != provider_name]
        self.logger.info(f"Provider 제거: {provider_name}")

    def collect_from_provider(
        self, provider: BaseProvider, input_dir: Path
    ) -> Dict[str, pd.DataFrame]:
        """
        단일 Provider에서 DataFrame을 수집합니다.

        Args:
            provider: 데이터를 수집할 Provider
            input_dir: 입력 파일이 있는 디렉토리

        Returns:
            수집된 DataFrame들
        """
        start_time = datetime.now()
        provider_dataframes = {}

        try:
            self.logger.info(f"{provider.name}에서 DataFrame 수집 시작")

            # Provider에서 DataFrame 수집
            provider_dataframes = provider.get_dataframes(input_dir)

            # 수집 통계 기록
            collection_time = datetime.now() - start_time
            total_records = sum(
                len(df) for df in provider_dataframes.values() if not df.empty
            )

            self.collection_stats[provider.name] = {
                "status": "success",
                "collection_time": collection_time.total_seconds(),
                "data_count": total_records,
                "dataframe_types": list(provider_dataframes.keys()),
                "timestamp": datetime.now(),
            }

            self.logger.info(
                f"{provider.name} DataFrame 수집 완료: {collection_time.total_seconds():.2f}초, {total_records}건"
            )

        except Exception as e:
            self.logger.error(f"{provider.name} DataFrame 수집 실패: {e}")
            self.collection_stats[provider.name] = {
                "status": "error",
                "error_message": str(e),
                "collection_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now(),
            }

        return provider_dataframes

    def collect_all_dataframes(
        self, input_dir: Path, use_async: bool = True
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        모든 Provider에서 DataFrame을 수집합니다.

        Args:
            input_dir: 입력 파일이 있는 디렉토리
            use_async: 비동기 수집 사용 여부

        Returns:
            모든 Provider의 수집된 DataFrame들
        """
        if not self.providers:
            self.logger.warning("수집할 Provider가 없습니다")
            return {}

        self.logger.info(f"{len(self.providers)}개 Provider에서 DataFrame 수집 시작")

        if use_async and len(self.providers) > 1:
            self._collect_async(input_dir)
        else:
            self._collect_sync(input_dir)

        return self.collected_dataframes

    def _collect_sync(
        self, input_dir: Path
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """동기적으로 DataFrame을 수집합니다."""
        for provider in self.providers:
            try:
                provider_dataframes = self.collect_from_provider(provider, input_dir)
                if provider_dataframes:
                    self.collected_dataframes[provider.name] = provider_dataframes
            except Exception as e:
                self.logger.error(f"{provider.name} 동기 수집 실패: {e}")

        return self.collected_dataframes

    def _collect_async(
        self, input_dir: Path
    ) -> Dict[str, Dict[str, pd.DataFrame]]:
        """비동기적으로 DataFrame을 수집합니다."""
        with ThreadPoolExecutor(max_workers=min(len(self.providers), 5)) as executor:
            # 각 Provider에 대해 수집 작업 제출
            future_to_provider = {
                executor.submit(
                    self.collect_from_provider, provider, input_dir
                ): provider
                for provider in self.providers
            }

            # 완료된 작업들 처리
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    provider_dataframes = future.result()
                    if provider_dataframes:
                        self.collected_dataframes[provider.name] = provider_dataframes
                except Exception as e:
                    self.logger.error(f"{provider.name} 비동기 수집 실패: {e}")

        return self.collected_dataframes

    def integrate_dataframes(self) -> Dict[str, pd.DataFrame]:
        """
        수집된 모든 DataFrame을 통합하여 최종 balances, transactions, positions를 생성합니다.

        Returns:
            통합된 DataFrame들
        """
        self.logger.info("DataFrame 통합 시작")

        # 각 데이터 타입별로 통합
        for data_type in ["balances", "transactions", "positions"]:
            dataframes_to_merge = []

            for provider_name, provider_dataframes in self.collected_dataframes.items():
                if data_type in provider_dataframes and not provider_dataframes[data_type].empty:
                    dataframes_to_merge.append(provider_dataframes[data_type])

            if dataframes_to_merge:
                # 모든 DataFrame을 하나로 통합
                integrated_df = pd.concat(dataframes_to_merge, ignore_index=True)

                # 데이터 정리 및 정렬
                if data_type == "balances":
                    integrated_df = self._clean_balances_dataframe(integrated_df)
                elif data_type == "transactions":
                    integrated_df = self._clean_transactions_dataframe(integrated_df)
                elif data_type == "positions":
                    integrated_df = self._clean_positions_dataframe(integrated_df)

                self.integrated_dataframes[data_type] = integrated_df
                self.logger.info(f"{data_type} 통합 완료: {len(integrated_df)}건")
            else:
                self.integrated_dataframes[data_type] = pd.DataFrame()
                self.logger.warning(f"{data_type} 데이터가 없습니다")

        return self.integrated_dataframes

    def _clean_balances_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """잔고 DataFrame을 정리합니다."""
        if df.empty:
            return df

        # 중복 제거 (같은 계좌, 같은 통화)
        df = df.drop_duplicates(subset=["account", "currency"], keep="last")

        # 정렬 (계좌명, 통화 순)
        df = df.sort_values(["account", "currency"])

        return df

    def _clean_transactions_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """거래내역 DataFrame을 정리합니다."""
        if df.empty:
            return df

        # 날짜 순 정렬
        if "date" in df.columns:
            df = df.sort_values("date", ascending=False)

        # 중복 제거 (같은 날짜, 시간, 심볼, 수량, 금액)
        df = df.drop_duplicates(subset=["date", "time", "symbol", "quantity", "amount"], keep="first")

        return df

    def _clean_positions_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """포지션 DataFrame을 정리합니다."""
        if df.empty:
            return df

        # 중복 제거 (같은 계좌, 같은 심볼)
        df = df.drop_duplicates(subset=["account", "symbol"], keep="last")

        # 정렬 (계좌명, 심볼 순)
        df = df.sort_values(["account", "symbol"])

        return df

    def export_integrated_data(self, output_dir: Path) -> Dict[str, Path]:
        """
        통합된 데이터를 CSV 파일로 내보냅니다.

        Args:
            output_dir: 출력 디렉토리

        Returns:
            생성된 CSV 파일 경로들
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        exported_files = {}

        for data_type, df in self.integrated_dataframes.items():
            if df.empty:
                continue

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"integrated_{data_type}_{timestamp}.csv"
            file_path = output_dir / filename

            try:
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                exported_files[data_type] = file_path
                self.logger.info(f"통합 {data_type} CSV 내보내기 완료: {file_path}")
            except Exception as e:
                self.logger.error(f"통합 {data_type} CSV 내보내기 실패: {e}")

        return exported_files

    def validate_collected_dataframes(self) -> Dict[str, List[str]]:
        """
        수집된 DataFrame의 유효성을 검증합니다.

        Returns:
            검증 결과 (오류 메시지 목록)
        """
        validation_errors = {}

        for provider_name, provider_dataframes in self.collected_dataframes.items():
            errors = []

            # 필수 데이터 타입 확인
            required_types = ["balances", "transactions", "positions"]
            for data_type in required_types:
                if data_type not in provider_dataframes:
                    errors.append(f"필수 데이터 타입 누락: {data_type}")
                    continue

                if not isinstance(provider_dataframes[data_type], pd.DataFrame):
                    errors.append(f"데이터 타입 오류: {data_type}이 DataFrame이 아님")
                    continue

                # DataFrame 구조 검증
                df = provider_dataframes[data_type]
                if not df.empty:
                    # 필수 컬럼 확인
                    required_columns = self._get_required_columns(data_type)
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    if missing_columns:
                        errors.append(f"필수 컬럼 누락: {missing_columns}")

            if errors:
                validation_errors[provider_name] = errors

        return validation_errors

    def _get_required_columns(self, data_type: str) -> List[str]:
        """데이터 타입별 필수 컬럼을 반환합니다."""
        if data_type == "balances":
            return ["account", "balance", "currency"]
        elif data_type == "transactions":
            return ["date", "type", "symbol", "quantity", "amount"]
        elif data_type == "positions":
            return ["account", "symbol", "quantity", "market_value"]
        else:
            return []

    def validate_cross_provider_dataframes(self) -> Dict[str, Any]:
        """
        Provider 간 DataFrame을 교차 검증합니다.
        도미노와 뱅크샐러드 데이터 간의 자산 총합 비교 검증

        Returns:
            교차 검증 결과
        """
        validation_result = {
            "status": "success",
            "errors": [],
            "warnings": [],
            "comparison_results": {},
            "total_assets_by_provider": {},
        }

        try:
            # 각 Provider의 자산 총합 계산
            for provider_name, provider_dataframes in self.collected_dataframes.items():
                total_assets = 0

                # 잔고 총합
                if "balances" in provider_dataframes and not provider_dataframes["balances"].empty:
                    balance_total = provider_dataframes["balances"]["balance"].sum()
                    total_assets += balance_total

                # 포지션 총합
                if "positions" in provider_dataframes and not provider_dataframes["positions"].empty:
                    position_total = provider_dataframes["positions"]["market_value"].sum()
                    total_assets += position_total

                validation_result["total_assets_by_provider"][
                    provider_name
                ] = total_assets

                self.logger.info(f"{provider_name} 총 자산: {total_assets:,.0f}원")

            # Provider 간 자산 총합 비교
            if len(validation_result["total_assets_by_provider"]) > 1:
                providers = list(validation_result["total_assets_by_provider"].keys())
                base_provider = providers[0]
                base_total = validation_result["total_assets_by_provider"][
                    base_provider
                ]

                for other_provider in providers[1:]:
                    other_total = validation_result["total_assets_by_provider"][
                        other_provider
                    ]
                    difference = abs(base_total - other_total)
                    difference_rate = (
                        (difference / base_total * 100) if base_total > 0 else 0
                    )

                    comparison = {
                        "base_provider": base_provider,
                        "base_total": base_total,
                        "other_provider": other_provider,
                        "other_total": other_total,
                        "difference": difference,
                        "difference_rate": difference_rate,
                    }

                    validation_result["comparison_results"][
                        f"{base_provider}_vs_{other_provider}"
                    ] = comparison

                    # 차이가 5% 이상인 경우 경고
                    if difference_rate > 5:
                        validation_result["warnings"].append(
                            f"{base_provider}와 {other_provider} 간 자산 총합 차이가 "
                            f"{difference_rate:.1f}% ({difference:,.0f}원)입니다"
                        )

                    # 차이가 20% 이상인 경우 오류
                    if difference_rate > 20:
                        validation_result["errors"].append(
                            f"{base_provider}와 {other_provider} 간 자산 총합 차이가 "
                            f"{difference_rate:.1f}% ({difference:,.0f}원)으로 심각합니다"
                        )

            # 검증 결과에 따른 상태 설정
            if validation_result["errors"]:
                validation_result["status"] = "error"
            elif validation_result["warnings"]:
                validation_result["status"] = "warning"

            # 검증 결과 저장
            self.validation_results = validation_result

        except Exception as e:
            validation_result["status"] = "error"
            validation_result["errors"].append(f"교차 검증 중 오류 발생: {str(e)}")
            self.logger.error(f"교차 검증 오류: {e}")

        return validation_result

    def get_collection_summary(self) -> Dict[str, Any]:
        """
        데이터 수집 요약 정보를 반환합니다.

        Returns:
            수집 요약 정보
        """
        total_providers = len(self.providers)
        successful_providers = sum(
            1
            for stats in self.collection_stats.values()
            if stats.get("status") == "success"
        )

        total_data_count = sum(
            stats.get("data_count", 0)
            for stats in self.collection_stats.values()
            if stats.get("status") == "success"
        )

        avg_collection_time = sum(
            stats.get("collection_time", 0)
            for stats in self.collection_stats.values()
            if stats.get("status") == "success"
        ) / max(successful_providers, 1)

        return {
            "total_providers": total_providers,
            "successful_providers": successful_providers,
            "failed_providers": total_providers - successful_providers,
            "success_rate": (
                (successful_providers / total_providers * 100)
                if total_providers > 0
                else 0
            ),
            "total_data_count": total_data_count,
            "average_collection_time": avg_collection_time,
            "collection_timestamp": datetime.now(),
            "provider_details": self.collection_stats,
            "validation_status": self.validation_results.get("status", "unknown"),
        }

    def get_dataframe_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        수집된 DataFrame의 통계 정보를 반환합니다.

        Returns:
            DataFrame 통계 정보
        """
        stats = {}

        for provider_name, provider_dataframes in self.collected_dataframes.items():
            provider_stats = {}

            for data_type, df in provider_dataframes.items():
                if not df.empty:
                    provider_stats[data_type] = {
                        "count": len(df),
                        "columns": list(df.columns),
                        "memory_usage": df.memory_usage(deep=True).sum(),
                        "last_updated": datetime.now(),
                    }
                else:
                    provider_stats[data_type] = {
                        "count": 0,
                        "columns": [],
                        "memory_usage": 0,
                        "last_updated": datetime.now(),
                    }

            stats[provider_name] = provider_stats

        return stats

    def clear_collected_data(self) -> None:
        """수집된 데이터를 초기화합니다."""
        self.collected_dataframes.clear()
        self.integrated_dataframes.clear()
        self.collection_stats.clear()
        self.validation_results.clear()
        self.logger.info("수집된 데이터 초기화 완료")

    def export_data_summary(self, output_path: Optional[Path] = None) -> Path:
        """
        데이터 수집 요약을 파일로 내보냅니다.

        Args:
            output_path: 출력 파일 경로 (None이면 자동 생성)

        Returns:
            출력 파일 경로
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(f"collection_summary_{timestamp}.json")

        summary = {
            "collection_summary": self.get_collection_summary(),
            "dataframe_statistics": self.get_dataframe_statistics(),
            "validation_errors": self.validate_collected_dataframes(),
            "cross_provider_validation": self.validate_cross_provider_dataframes(),
            "export_timestamp": datetime.now().isoformat(),
        }

        try:
            import json

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

            self.logger.info(f"데이터 수집 요약 내보내기 완료: {output_path}")
            return output_path
        except Exception as e:
            self.logger.error(f"데이터 수집 요약 내보내기 실패: {e}")
            raise
