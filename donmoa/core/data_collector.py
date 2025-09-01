"""
데이터 수집 핵심 클래스
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..providers.base import BaseProvider
from ..utils.config import config_manager
from ..utils.logger import LoggerMixin


class DataCollector(LoggerMixin):
    """여러 기관의 데이터를 수집하는 핵심 클래스"""

    def __init__(self, providers: Optional[List[BaseProvider]] = None):
        """
        DataCollector 초기화

        Args:
            providers: 데이터 수집할 Provider 목록
        """
        self.providers = providers or []
        self.collected_data: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}
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
        self, provider: BaseProvider, output_dir: Path
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        단일 Provider에서 데이터를 수집합니다.

        Args:
            provider: 데이터를 수집할 Provider
            output_dir: 데이터 다운로드 및 임시 저장 디렉토리

        Returns:
            수집된 데이터
        """
        start_time = datetime.now()
        provider_data = {}

        try:
            self.logger.info(f"{provider.name}에서 데이터 수집 시작")

            # Provider에서 모든 데이터 수집 (HTML/CSV 파싱 기반)
            provider_data = provider.collect_all_data(output_dir)

            # 수집 통계 기록
            collection_time = datetime.now() - start_time
            self.collection_stats[provider.name] = {
                "status": "success",
                "collection_time": collection_time.total_seconds(),
                "data_count": sum(
                    len(data)
                    for data in provider_data.values()
                    if isinstance(data, list)
                ),
                "timestamp": datetime.now(),
            }

            self.logger.info(
                f"{provider.name} 데이터 수집 완료: {collection_time.total_seconds():.2f}초"
            )

        except Exception as e:
            self.logger.error(f"{provider.name} 데이터 수집 실패: {e}")
            self.collection_stats[provider.name] = {
                "status": "error",
                "error_message": str(e),
                "collection_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now(),
            }

        return provider_data

    def collect_all_data(
        self, output_dir: Path, use_async: bool = True
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        모든 Provider에서 데이터를 수집합니다.

        Args:
            output_dir: 데이터 다운로드 및 임시 저장 디렉토리
            use_async: 비동기 수집 사용 여부

        Returns:
            모든 Provider의 수집된 데이터
        """
        if not self.providers:
            self.logger.warning("수집할 Provider가 없습니다")
            return {}

        self.logger.info(f"{len(self.providers)}개 Provider에서 데이터 수집 시작")

        if use_async and len(self.providers) > 1:
            return self._collect_async(output_dir)
        else:
            return self._collect_sync(output_dir)

    def _collect_sync(
        self, output_dir: Path
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """동기적으로 데이터를 수집합니다."""
        for provider in self.providers:
            try:
                provider_data = self.collect_from_provider(provider, output_dir)
                if provider_data:
                    self.collected_data[provider.name] = provider_data
            except Exception as e:
                self.logger.error(f"{provider.name} 동기 수집 실패: {e}")

        return self.collected_data

    def _collect_async(
        self, output_dir: Path
    ) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """비동기적으로 데이터를 수집합니다."""
        with ThreadPoolExecutor(max_workers=min(len(self.providers), 5)) as executor:
            # 각 Provider에 대해 수집 작업 제출
            future_to_provider = {
                executor.submit(
                    self.collect_from_provider, provider, output_dir
                ): provider
                for provider in self.providers
            }

            # 완료된 작업들 처리
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    provider_data = future.result()
                    if provider_data:
                        self.collected_data[provider.name] = provider_data
                except Exception as e:
                    self.logger.error(f"{provider.name} 비동기 수집 실패: {e}")

        return self.collected_data

    def validate_collected_data(self) -> Dict[str, List[str]]:
        """
        수집된 데이터의 유효성을 검증합니다.

        Returns:
            검증 결과 (오류 메시지 목록)
        """
        validation_errors = {}

        for provider_name, provider_data in self.collected_data.items():
            errors = []

            # 필수 데이터 타입 확인
            required_types = ["balances", "transactions", "positions"]
            for data_type in required_types:
                if data_type not in provider_data:
                    errors.append(f"필수 데이터 타입 누락: {data_type}")
                    continue

                if not isinstance(provider_data[data_type], list):
                    errors.append(f"데이터 타입 오류: {data_type}이 리스트가 아님")
                    continue

                # 데이터 구조 검증
                if provider_data[data_type]:
                    sample_item = provider_data[data_type][0]
                    if not isinstance(sample_item, dict):
                        errors.append(f"데이터 항목이 딕셔너리가 아님: {data_type}")

            if errors:
                validation_errors[provider_name] = errors

        return validation_errors

    def validate_cross_provider_data(self) -> Dict[str, Any]:
        """
        Provider 간 데이터를 교차 검증합니다.
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
            for provider_name, provider_data in self.collected_data.items():
                total_assets = 0

                # 잔고 총합
                if "balances" in provider_data:
                    balance_total = sum(
                        float(item.get("balance", 0))
                        for item in provider_data["balances"]
                    )
                    total_assets += balance_total

                # 포지션 총합
                if "positions" in provider_data:
                    position_total = sum(
                        float(item.get("quantity", 0))
                        * float(item.get("current_price", 0))
                        for item in provider_data["positions"]
                    )
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

    def get_data_statistics(self) -> Dict[str, Dict[str, Any]]:
        """
        수집된 데이터의 통계 정보를 반환합니다.

        Returns:
            데이터 통계 정보
        """
        stats = {}

        for provider_name, provider_data in self.collected_data.items():
            provider_stats = {}

            for data_type, data_list in provider_data.items():
                if isinstance(data_list, list) and data_list:
                    provider_stats[data_type] = {
                        "count": len(data_list),
                        "sample_keys": list(data_list[0].keys()) if data_list else [],
                        "last_updated": datetime.now(),
                    }
                else:
                    provider_stats[data_type] = {
                        "count": 0,
                        "sample_keys": [],
                        "last_updated": datetime.now(),
                    }

            stats[provider_name] = provider_stats

        return stats

    def clear_collected_data(self) -> None:
        """수집된 데이터를 초기화합니다."""
        self.collected_data.clear()
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
            "data_statistics": self.get_data_statistics(),
            "validation_errors": self.validate_collected_data(),
            "cross_provider_validation": self.validate_cross_provider_data(),
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
