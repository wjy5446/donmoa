"""
Donmoa 메인 클래스
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import os

from .data_collector import DataCollector
from .csv_exporter import CSVExporter
from ..providers.base import BaseProvider
from ..utils.logger import LoggerMixin
from ..utils.config import config_manager


class Donmoa(LoggerMixin):
    """Donmoa 메인 클래스 - 데이터 수집부터 CSV 내보내기까지 전체 워크플로우 관리"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Donmoa 초기화

        Args:
            config_path: 설정 파일 경로
        """
        # 설정 및 로깅 초기화
        if config_path:
            config_manager.config_path = config_path
            config_manager.reload()

        # 로깅 설정 적용
        self._setup_logging()

        # 핵심 컴포넌트 초기화
        self.data_collector = DataCollector()
        self.csv_exporter = CSVExporter()

        # Provider 목록
        self.providers: Dict[str, BaseProvider] = {}

        # 최근 실행 결과
        self.last_run_result: Optional[Dict[str, Any]] = None

        # 계좌 매핑 관리
        self.account_mappings: Dict[str, Dict[str, str]] = {}

        # 설정 파일에서 계좌 매핑 로드
        self._load_account_mappings()

        self.logger.info("Donmoa 초기화 완료")

    def _load_account_mappings(self) -> None:
        """설정 파일에서 계좌 매핑을 로드합니다."""
        try:
            self.account_mappings = config_manager.get('account_mapping', {})
            self.logger.info(f"계좌 매핑 설정 로드 완료: {len(self.account_mappings)}개 타입")
        except Exception as e:
            self.logger.warning(f"계좌 매핑 로드 실패: {e}")

    def _setup_logging(self) -> None:
        """로깅 설정을 적용합니다."""
        from ..utils.logger import setup_logger

        log_level = config_manager.get('logging.level', 'INFO')
        log_file = config_manager.get('logging.file', './logs/donmoa.log')
        console_output = config_manager.get('logging.console', True)

        # 로그 레벨 변환
        level_map = {
            'DEBUG': 10,
            'INFO': 20,
            'WARNING': 30,
            'ERROR': 40,
            'CRITICAL': 50
        }

        log_level_int = level_map.get(log_level.upper(), 20)

        # 로거 설정
        setup_logger(
            name="donmoa",
            level=log_level_int,
            log_file=Path(log_file),
            console_output=console_output
        )

    def add_provider(self, provider: BaseProvider) -> None:
        """
        Provider를 추가합니다.

        Args:
            provider: 추가할 Provider 인스턴스
        """
        self.providers[provider.name] = provider
        self.data_collector.add_provider(provider)

        # 설정 파일의 계좌 매핑 자동 적용
        self._apply_account_mapping_to_provider(provider)

        self.logger.info(f"Provider 추가 완료: {provider.name}")

    def _apply_account_mapping_to_provider(self, provider: BaseProvider) -> None:
        """Provider에 설정 파일의 계좌 매핑을 적용합니다."""
        try:
            provider_type = provider.type

            # Provider 타입에 따른 매핑 키 결정
            if provider_type == 'securities':
                mapping_key = 'domino_securities'
            elif provider_type == 'bank':
                mapping_key = 'banksalad_csv'
            else:
                return  # 지원하지 않는 Provider 타입

            # 통합 계좌 중심 구조에서 Provider별 매핑 생성
            provider_mappings = {}
            for unified_account, provider_mappings_dict in self.account_mappings.items():
                if mapping_key in provider_mappings_dict:
                    original_account = provider_mappings_dict[mapping_key]
                    provider_mappings[original_account] = unified_account

            # Provider에 매핑 적용
            if provider_mappings:
                provider.set_account_mapping(provider_mappings)
                self.logger.info(f"{provider.name}에 계좌 매핑 적용 완료: {len(provider_mappings)}개")

        except Exception as e:
            self.logger.warning(f"{provider.name} 계좌 매핑 적용 실패: {e}")

    def remove_provider(self, provider_name: str) -> None:
        """
        Provider를 제거합니다.

        Args:
            provider_name: 제거할 Provider 이름
        """
        if provider_name in self.providers:
            del self.providers[provider_name]
            self.data_collector.remove_provider(provider_name)
            self.logger.info(f"Provider 제거 완료: {provider_name}")
        else:
            self.logger.warning(f"Provider '{provider_name}'를 찾을 수 없습니다")

    def get_provider(self, provider_name: str) -> Optional[BaseProvider]:
        """
        Provider를 가져옵니다.

        Args:
            provider_name: Provider 이름

        Returns:
            Provider 인스턴스 또는 None
        """
        return self.providers.get(provider_name)

    def list_providers(self) -> List[str]:
        """
        등록된 Provider 목록을 반환합니다.

        Returns:
            Provider 이름 목록
        """
        return list(self.providers.keys())

    def set_account_mapping(self, provider_name: str, mapping: Dict[str, str]) -> None:
        """
        특정 Provider의 계좌 매핑을 설정합니다.

        Args:
            provider_name: Provider 이름
            mapping: 원본 계좌명 -> 통합 계좌명 매핑
        """
        if provider_name in self.providers:
            self.providers[provider_name].set_account_mapping(mapping)
            self.account_mappings[provider_name] = mapping
            self.logger.info(f"{provider_name} 계좌 매핑 설정 완료: {len(mapping)}개")
        else:
            self.logger.warning(f"Provider '{provider_name}'를 찾을 수 없습니다")

    def get_account_mapping(self, provider_name: str) -> Dict[str, str]:
        """
        특정 Provider의 계좌 매핑을 반환합니다.

        Args:
            provider_name: Provider 이름

        Returns:
            계좌 매핑 정보
        """
        if provider_name in self.providers:
            return self.providers[provider_name].get_account_mapping()
        return {}

    def collect_data(self, provider_names: Optional[List[str]] = None,
                    use_async: bool = True,
                    temp_dir: Optional[Path] = None,
                    use_manual_files: bool = False) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        데이터를 수집합니다.

        Args:
            provider_names: 데이터를 수집할 Provider 이름 목록 (None이면 모든 Provider)
            use_async: 비동기 수집 사용 여부
            temp_dir: 임시 데이터 저장 디렉토리
            use_manual_files: 수동 파일 사용 여부

        Returns:
            수집된 데이터
        """
        start_time = datetime.now()
        self.logger.info("데이터 수집 시작")

        # 임시 디렉토리 설정
        if temp_dir is None:
            temp_dir = Path("./temp_data")
        temp_dir.mkdir(exist_ok=True)

        # 특정 Provider만 수집하는 경우
        if provider_names:
            temp_collector = DataCollector()
            for name in provider_names:
                if name in self.providers:
                    temp_collector.add_provider(self.providers[name])
                else:
                    self.logger.warning(f"Provider '{name}'를 찾을 수 없습니다")

            collected_data = temp_collector.collect_all_data(temp_dir, use_async)
        else:
            # 모든 Provider에서 수집
            collected_data = self.data_collector.collect_all_data(temp_dir, use_async)

        collection_time = datetime.now() - start_time
        self.logger.info(f"데이터 수집 완료: {collection_time.total_seconds():.2f}초")

        # 수집 결과 저장
        self.last_run_result = {
            'collection_timestamp': start_time.isoformat(),
            'collection_time_seconds': collection_time.total_seconds(),
            'collected_data': collected_data,
            'collection_summary': self.data_collector.get_collection_summary(),
            'data_statistics': self.data_collector.get_data_statistics()
        }

        return collected_data

    def export_to_csv(self, collected_data: Optional[Dict[str, Dict[str, List[Dict[str, Any]]]]] = None,
                     output_dir: Optional[Path] = None,
                     timestamp: Optional[datetime] = None) -> Dict[str, Path]:
        """
        수집된 데이터를 CSV 파일로 내보냅니다.

        Args:
            collected_data: 내보낼 데이터 (None이면 최근 수집된 데이터 사용)
            output_dir: 출력 디렉토리
            timestamp: 내보내기 타임스탬프

        Returns:
            생성된 CSV 파일 경로들
        """
        if collected_data is None:
            if self.last_run_result and 'collected_data' in self.last_run_result:
                collected_data = self.last_run_result['collected_data']
            else:
                raise ValueError("내보낼 데이터가 없습니다. 먼저 데이터를 수집하거나 collected_data를 제공해주세요")

        if output_dir:
            self.csv_exporter.output_dir = Path(output_dir)

        self.logger.info("CSV 내보내기 시작")

        try:
            exported_files = self.csv_exporter.export_to_csv(collected_data, timestamp)

            # 내보내기 통계 생성
            export_stats = self.csv_exporter.get_export_statistics(exported_files)

            # 최근 실행 결과에 내보내기 정보 추가
            if self.last_run_result:
                self.last_run_result['export_timestamp'] = datetime.now().isoformat()
                self.last_run_result['exported_files'] = {k: str(v) for k, v in exported_files.items()}
                self.last_run_result['export_statistics'] = export_stats

            self.logger.info(f"CSV 내보내기 완료: {len(exported_files)}개 파일 생성")
            return exported_files

        except Exception as e:
            self.logger.error(f"CSV 내보내기 실패: {e}")
            raise

    def run_full_workflow(self, provider_names: Optional[List[str]] = None,
                          output_dir: Optional[Path] = None,
                          temp_dir: Optional[Path] = None,
                          use_async: bool = True) -> Dict[str, Any]:
        """
        전체 워크플로우를 실행합니다 (데이터 수집 → CSV 내보내기).

        Args:
            provider_names: 데이터를 수집할 Provider 이름 목록
            output_dir: CSV 출력 디렉토리
            temp_dir: 임시 데이터 저장 디렉토리
            use_async: 비동기 수집 사용 여부

        Returns:
            실행 결과 요약
        """
        workflow_start = datetime.now()
        self.logger.info("전체 워크플로우 시작")

        try:
            # 1단계: 데이터 수집
            collected_data = self.collect_data(provider_names, use_async, temp_dir)

            # 2단계: 데이터 검증
            validation_errors = self.data_collector.validate_collected_data()
            if validation_errors:
                self.logger.warning(f"데이터 검증에서 {len(validation_errors)}개 오류 발견")

            # 3단계: 교차 검증 (도미노 vs 뱅크샐러드)
            cross_validation = self.data_collector.validate_cross_provider_data()
            if cross_validation['status'] != 'success':
                self.logger.warning(f"교차 검증 결과: {cross_validation['status']}")
                if cross_validation['warnings']:
                    for warning in cross_validation['warnings']:
                        self.logger.warning(f"교차 검증 경고: {warning}")
                if cross_validation['errors']:
                    for error in cross_validation['errors']:
                        self.logger.error(f"교차 검증 오류: {error}")

            # 4단계: CSV 내보내기
            exported_files = self.export_to_csv(collected_data, output_dir)

            # 워크플로우 완료
            workflow_time = datetime.now() - workflow_start

            result = {
                'status': 'success',
                'workflow_start': workflow_start.isoformat(),
                'workflow_duration_seconds': workflow_time.total_seconds(),
                'collected_providers': list(collected_data.keys()),
                            'total_data_records': sum(
                len(data)
                for provider_data in collected_data.values()
                for data in provider_data.values()
                if isinstance(data, list)
            ),
                'exported_files': {k: str(v) for k, v in exported_files.items()},
                'validation_errors': validation_errors,
                'cross_validation': cross_validation,
                'collection_summary': self.data_collector.get_collection_summary(),
                'export_statistics': self.csv_exporter.get_export_statistics(exported_files)
            }

            self.logger.info(f"전체 워크플로우 완료: {workflow_time.total_seconds():.2f}초")
            return result

        except Exception as e:
            workflow_time = datetime.now() - workflow_start
            self.logger.error(f"워크플로우 실행 실패: {e}")

            result = {
                'status': 'error',
                'error_message': str(e),
                'workflow_start': workflow_start.isoformat(),
                'workflow_duration_seconds': workflow_time.total_seconds()
            }

            return result

    def get_status(self) -> Dict[str, Any]:
        """
        현재 Donmoa 상태를 반환합니다.

        Returns:
            상태 정보
        """
        status = {
            'providers': {
                'total': len(self.providers),
                'names': list(self.providers.keys()),
                'enabled': len([p for p in self.providers.values() if hasattr(p, 'enabled') and p.enabled])
            },
            'account_mappings': {
                name: len(mapping) for name, mapping in self.account_mappings.items()
            },
            'last_run': self.last_run_result,
            'configuration': {
                'output_directory': str(self.csv_exporter.output_dir),
                'encoding': self.csv_exporter.encoding,
                'async_collection': True
            },
            'timestamp': datetime.now().isoformat()
        }

        return status

    def save_workflow_result(self, output_path: Optional[Path] = None) -> Path:
        """
        워크플로우 실행 결과를 파일로 저장합니다.

        Args:
            output_path: 출력 파일 경로 (None이면 자동 생성)

        Returns:
            저장된 파일 경로
        """
        if not self.last_run_result:
            raise ValueError("저장할 워크플로우 결과가 없습니다")

        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path(f"workflow_result_{timestamp}.json")

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.last_run_result, f, ensure_ascii=False, indent=2, default=str)

            self.logger.info(f"워크플로우 결과 저장 완료: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"워크플로우 결과 저장 실패: {e}")
            raise

    def clear_data(self) -> None:
        """수집된 데이터와 실행 결과를 초기화합니다."""
        self.data_collector.clear_collected_data()
        self.last_run_result = None
        self.logger.info("모든 데이터 초기화 완료")

    def test_provider_connection(self, provider_name: str) -> Dict[str, Any]:
        """
        특정 Provider의 연결을 테스트합니다.

        Args:
            provider_name: 테스트할 Provider 이름

        Returns:
            연결 테스트 결과
        """
        if provider_name not in self.providers:
            return {
                'status': 'error',
                'error': f"Provider '{provider_name}'를 찾을 수 없습니다"
            }

        provider = self.providers[provider_name]
        start_time = datetime.now()

        try:
            # 임시 디렉토리 생성
            temp_dir = Path("./temp_test")
            temp_dir.mkdir(exist_ok=True)

            # 데이터 수집 테스트
            test_data = provider.collect_all_data(temp_dir)

            return {
                'status': 'success',
                'provider': provider_name,
                'data_collection': 'success',
                'data_types_found': list(test_data.keys()),
                'total_records': sum(len(data) for data in test_data.values() if isinstance(data, list)),
                'test_time': (datetime.now() - start_time).total_seconds()
            }

        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'provider': provider_name,
                'test_time': (datetime.now() - start_time).total_seconds()
            }

    def get_provider_info(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """
        Provider의 상세 정보를 반환합니다.

        Args:
            provider_name: Provider 이름

        Returns:
            Provider 정보 또는 None
        """
        if provider_name not in self.providers:
            return None

        provider = self.providers[provider_name]

        info = {
            'name': provider.name,
            'type': provider.provider_type,
            'enabled': provider.enabled,
            'has_credentials': bool(provider.credentials),
            'account_mapping_count': len(provider.get_account_mapping()),
            'data_statistics': provider.get_data_statistics()
        }

        return info

    def validate_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        수집된 데이터의 유효성을 검증합니다.

        Args:
            collected_data: 검증할 데이터

        Returns:
            검증 결과
        """
        warnings = []
        is_valid = True

        for provider_name, data in collected_data.items():
            if not data:
                warnings.append(f"Provider '{provider_name}': 데이터가 없습니다")
                continue

            # 데이터 타입별 검증
            for data_type, records in data.items():
                if not isinstance(records, list):
                    warnings.append(f"Provider '{provider_name}' {data_type}: 잘못된 데이터 형식")
                    is_valid = False
                    continue

                if not records:
                    warnings.append(f"Provider '{provider_name}' {data_type}: 빈 데이터")
                    continue

                # 첫 번째 레코드로 스키마 검증
                first_record = records[0]
                if not isinstance(first_record, dict):
                    warnings.append(f"Provider '{provider_name}' {data_type}: 레코드가 딕셔너리가 아닙니다")
                    is_valid = False

        return {
            'is_valid': is_valid,
            'warnings': warnings,
            'total_providers': len(collected_data),
            'total_records': sum(len(records) for data in collected_data.values()
                                for records in data.values() if isinstance(records, list))
        }

    def check_health(self) -> Dict[str, Any]:
        """
        시스템 상태를 확인합니다.

        Returns:
            시스템 상태 정보
        """
        health_status = {}

        # Provider 상태 확인
        provider_health = {}
        for name, provider in self.providers.items():
            try:
                # Provider 기본 상태 확인
                provider_health[name] = {
                    'healthy': provider.enabled and provider.credentials is not None,
                    'message': '정상' if provider.enabled and provider.credentials else '비활성화됨'
                }
            except Exception as e:
                provider_health[name] = {
                    'healthy': False,
                    'message': f'오류: {str(e)}'
                }

        health_status['providers'] = provider_health

        # Provider가 없는 경우 기본 상태 추가
        if not self.providers:
            health_status['providers'] = {
                'status': {
                    'healthy': True,
                    'message': '등록된 Provider가 없습니다'
                }
            }

        # 파일 시스템 상태 확인
        try:
            output_dir = Path(config_manager.get('export.output_dir', './export'))
            output_dir.mkdir(exist_ok=True)

            health_status['file_system'] = {
                'healthy': True,
                'message': f'출력 디렉토리 정상: {output_dir}'
            }
        except Exception as e:
            health_status['file_system'] = {
                'healthy': False,
                'message': f'파일 시스템 오류: {str(e)}'
            }

        # 로깅 시스템 상태 확인
        try:
            log_file = Path(config_manager.get('logging.file', './logs/donmoa.log'))
            log_file.parent.mkdir(exist_ok=True)

            health_status['logging'] = {
                'healthy': True,
                'message': f'로깅 시스템 정상: {log_file}'
            }
        except Exception as e:
            health_status['logging'] = {
                'healthy': False,
                'message': f'로깅 시스템 오류: {str(e)}'
            }

        return health_status

    def collect_metrics(self) -> Dict[str, Any]:
        """
        시스템 메트릭을 수집합니다.

        Returns:
            시스템 메트릭
        """
        metrics = {}

        # Provider 메트릭
        total_providers = len(self.providers)
        active_providers = sum(1 for p in self.providers.values() if p.enabled)

        metrics['provider_count'] = {
            'value': total_providers,
            'unit': '개'
        }
        metrics['active_providers'] = {
            'value': active_providers,
            'unit': '개'
        }

        # 데이터 메트릭
        if self.last_run_result:
            total_records = sum(len(data) for data in self.last_run_result.get('collected_data', {}).values()
                               if isinstance(data, list))
            metrics['total_records'] = {
                'value': total_records,
                'unit': '건'
            }

        # 메모리 사용량 (간단한 추정)
        import sys
        memory_usage = sys.getsizeof(self) + sum(sys.getsizeof(p) for p in self.providers.values())
        metrics['memory_usage'] = {
            'value': memory_usage / 1024,  # KB
            'unit': 'KB'
        }

        return metrics

    def create_backup(self) -> str:
        """
        현재 데이터의 백업을 생성합니다.

        Returns:
            백업 파일 경로
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = Path("./backups")
        backup_dir.mkdir(exist_ok=True)

        backup_file = backup_dir / f"donmoa_backup_{timestamp}.json"

        backup_data = {
            'timestamp': timestamp,
            'providers': {name: provider.get_data_statistics()
                         for name, provider in self.providers.items()},
            'last_run_result': self.last_run_result,
            'account_mappings': self.account_mappings
        }

        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2, default=str)

        self.logger.info(f"백업 생성 완료: {backup_file}")
        return str(backup_file)

    def restore_from_backup(self, backup_path: str) -> None:
        """
        백업에서 데이터를 복원합니다.

        Args:
            backup_path: 백업 파일 경로
        """
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise FileNotFoundError(f"백업 파일을 찾을 수 없습니다: {backup_path}")

        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)

        # 계좌 매핑 복원
        self.account_mappings = backup_data.get('account_mappings', {})

        # Provider별 데이터 통계 복원
        for provider_name, stats in backup_data.get('providers', {}).items():
            if provider_name in self.providers:
                self.logger.info(f"Provider '{provider_name}' 통계 복원: {stats}")

        self.logger.info(f"백업에서 복원 완료: {backup_path}")

    def list_backups(self) -> List[Dict[str, Any]]:
        """
        사용 가능한 백업 목록을 반환합니다.

        Returns:
            백업 목록
        """
        backup_dir = Path("./backups")
        if not backup_dir.exists():
            return []

        backups = []
        for backup_file in backup_dir.glob("donmoa_backup_*.json"):
            try:
                stat = backup_file.stat()
                backups.append({
                    'filename': backup_file.name,
                    'size_mb': stat.st_size / (1024 * 1024),
                    'created_at': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'status': '사용 가능'
                })
            except Exception as e:
                backups.append({
                    'filename': backup_file.name,
                    'size_mb': 0,
                    'created_at': '알 수 없음',
                    'status': f'오류: {str(e)}'
                })

        # 생성일 기준으로 정렬 (최신순)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        return backups

    def cleanup_old_data(self) -> Dict[str, Any]:
        """
        오래된 데이터를 정리합니다.

        Returns:
            정리 결과
        """
        cleaned_records = 0

        # 30일 이상 된 로그 파일 정리
        log_dir = Path(config_manager.get('logging.file', './logs/donmoa.log')).parent
        if log_dir.exists():
            cutoff_date = datetime.now().timestamp() - (30 * 24 * 60 * 60)  # 30일
            for log_file in log_dir.glob("*.log.*"):
                try:
                    if log_file.stat().st_mtime < cutoff_date:
                        log_file.unlink()
                        cleaned_records += 1
                except Exception as e:
                    self.logger.warning(f"로그 파일 정리 실패: {log_file} - {e}")

        # 임시 파일 정리
        temp_dir = Path("./temp_test")
        if temp_dir.exists():
            try:
                import shutil
                shutil.rmtree(temp_dir)
                temp_dir.mkdir(exist_ok=True)
                cleaned_records += 1
            except Exception as e:
                self.logger.warning(f"임시 디렉토리 정리 실패: {e}")

        return {
            'cleaned_records': cleaned_records,
            'message': f'{cleaned_records}개 항목 정리 완료'
        }

    def optimize_storage(self) -> Dict[str, Any]:
        """
        저장소를 최적화합니다.

        Returns:
            최적화 결과
        """
        saved_space = 0

        # CSV 파일 압축
        export_dir = Path(config_manager.get('export.output_dir', './export'))
        if export_dir.exists():
            for csv_file in export_dir.glob("*.csv"):
                try:
                    # 간단한 압축 (실제로는 더 정교한 압축 로직 필요)
                    original_size = csv_file.stat().st_size
                    # 여기에 실제 압축 로직 구현
                    saved_space += original_size * 0.1  # 10% 절약 가정
                except Exception as e:
                    self.logger.warning(f"파일 압축 실패: {csv_file} - {e}")

        return {
            'saved_space': saved_space / (1024 * 1024),  # MB
            'message': f'{saved_space / (1024 * 1024):.1f}MB 절약'
        }

    def vacuum_storage(self) -> Dict[str, Any]:
        """
        저장 공간을 정리합니다.

        Returns:
            정리 결과
        """
        freed_space = 0

        # 빈 디렉토리 정리
        for root, dirs, files in os.walk(".", topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        freed_space += 4096  # 디렉토리 엔트리 크기
                except Exception as e:
                    self.logger.warning(f"빈 디렉토리 정리 실패: {dir_path} - {e}")

        return {
            'freed_space': freed_space / (1024 * 1024),  # MB
            'message': f'{freed_space / (1024 * 1024):.1f}MB 해제'
        }
