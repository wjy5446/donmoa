"""
Donmoa 메인 클래스
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import json

from .data_collector import DataCollector
from .csv_exporter import CSVExporter
from ..providers.base import BaseProvider
from ..utils.logger import LoggerMixin
from ..utils.config import config_manager
from ..utils.encryption import encryption_manager


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
        
        self.logger.info("Donmoa 초기화 완료")
    
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
        self.logger.info(f"Provider 추가 완료: {provider.name}")
    
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
    
    def collect_data(self, provider_names: Optional[List[str]] = None, 
                    use_async: bool = True) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """
        데이터를 수집합니다.
        
        Args:
            provider_names: 데이터를 수집할 Provider 이름 목록 (None이면 모든 Provider)
            use_async: 비동기 수집 사용 여부
            
        Returns:
            수집된 데이터
        """
        start_time = datetime.now()
        self.logger.info("데이터 수집 시작")
        
        # 특정 Provider만 수집하는 경우
        if provider_names:
            temp_collector = DataCollector()
            for name in provider_names:
                if name in self.providers:
                    temp_collector.add_provider(self.providers[name])
                else:
                    self.logger.warning(f"Provider '{name}'를 찾을 수 없습니다")
            
            collected_data = temp_collector.collect_all_data(use_async=use_async)
        else:
            # 모든 Provider에서 수집
            collected_data = self.data_collector.collect_all_data(use_async=use_async)
        
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
                          use_async: bool = True) -> Dict[str, Any]:
        """
        전체 워크플로우를 실행합니다 (데이터 수집 → CSV 내보내기).
        
        Args:
            provider_names: 데이터를 수집할 Provider 이름 목록
            output_dir: CSV 출력 디렉토리
            use_async: 비동기 수집 사용 여부
            
        Returns:
            실행 결과 요약
        """
        workflow_start = datetime.now()
        self.logger.info("전체 워크플로우 시작")
        
        try:
            # 1단계: 데이터 수집
            collected_data = self.collect_data(provider_names, use_async)
            
            # 2단계: 데이터 검증
            validation_errors = self.data_collector.validate_collected_data()
            if validation_errors:
                self.logger.warning(f"데이터 검증에서 {len(validation_errors)}개 오류 발견")
            
            # 3단계: CSV 내보내기
            exported_files = self.export_to_csv(collected_data, output_dir)
            
            # 워크플로우 완료
            workflow_time = datetime.now() - workflow_start
            
            result = {
                'status': 'success',
                'workflow_start': workflow_start.isoformat(),
                'workflow_duration_seconds': workflow_time.total_seconds(),
                'collected_providers': list(collected_data.keys()),
                'total_data_records': sum(
                    len(data) for provider_data in collected_data.values()
                    for data in provider_data.values()
                ),
                'exported_files': {k: str(v) for k, v in exported_files.items()},
                'validation_errors': validation_errors,
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
            # 인증 테스트
            auth_result = provider.authenticate()
            
            if not auth_result:
                return {
                    'status': 'error',
                    'error': '인증 실패',
                    'provider': provider_name,
                    'test_time': (datetime.now() - start_time).total_seconds()
                }
            
            # 간단한 데이터 수집 테스트
            test_data = provider.collect_all_data()
            
            return {
                'status': 'success',
                'provider': provider_name,
                'authentication': 'success',
                'data_collection': 'success',
                'data_types_found': list(test_data.keys()),
                'total_records': sum(len(data) for data in test_data.values()),
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
            'endpoints': provider.endpoints,
            'has_credentials': bool(provider.credentials),
            'session_active': hasattr(provider, 'session') and provider.session is not None
        }
        
        return info
