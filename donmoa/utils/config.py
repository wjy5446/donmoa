"""
설정 관리 유틸리티 모듈
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from .logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """설정 파일 및 환경 변수 관리 클래스"""
    
    def __init__(self, config_path: Optional[Path] = None, env_path: Optional[Path] = None):
        """
        ConfigManager 초기화
        
        Args:
            config_path: 설정 파일 경로 (None이면 기본 경로 사용)
            env_path: 환경 변수 파일 경로 (None이면 기본 경로 사용)
        """
        self.config_path = config_path or Path("config.yaml")
        self.env_path = env_path or Path(".env")
        
        # 환경 변수 로드
        self._load_env()
        
        # 설정 파일 로드
        self.config = self._load_config()
        
        # 기본값 설정
        self._set_defaults()
    
    def _load_env(self) -> None:
        """환경 변수 파일을 로드합니다."""
        if self.env_path.exists():
            load_dotenv(self.env_path)
            logger.info(f"환경 변수 파일 로드 완료: {self.env_path}")
        else:
            logger.warning(f"환경 변수 파일을 찾을 수 없습니다: {self.env_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """설정 파일을 로드합니다."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    logger.info(f"설정 파일 로드 완료: {self.config_path}")
                    return config or {}
            except Exception as e:
                logger.error(f"설정 파일 로드 실패: {e}")
                return {}
        else:
            logger.warning(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
            return {}
    
    def _set_defaults(self) -> None:
        """기본 설정값을 설정합니다."""
        defaults = {
            'schedule': {
                'enabled': True,
                'interval_hours': 24,
                'start_time': '09:00'
            },
            'export': {
                'output_dir': './export',
                'file_format': 'csv',
                'encoding': 'utf-8'
            },
            'providers': {
                'securities': {
                    'enabled': True,
                    'retry_count': 3,
                    'timeout': 30
                },
                'bank': {
                    'enabled': True,
                    'retry_count': 3,
                    'timeout': 30
                },
                'exchange': {
                    'enabled': True,
                    'retry_count': 3,
                    'timeout': 30
                }
            },
            'logging': {
                'level': 'INFO',
                'file': './logs/donmoa.log',
                'console': True
            }
        }
        
        # 기본값과 사용자 설정 병합
        self._merge_configs(defaults, self.config)
    
    def _merge_configs(self, defaults: Dict[str, Any], user_config: Dict[str, Any]) -> None:
        """기본 설정과 사용자 설정을 병합합니다."""
        for key, default_value in defaults.items():
            if key not in user_config:
                user_config[key] = default_value
            elif isinstance(default_value, dict) and isinstance(user_config[key], dict):
                self._merge_configs(default_value, user_config[key])
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값을 가져옵니다.
        
        Args:
            key: 설정 키 (점 표기법 지원, 예: 'schedule.interval_hours')
            default: 기본값
            
        Returns:
            설정값 또는 기본값
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_env(self, key: str, default: Any = None) -> Any:
        """
        환경 변수값을 가져옵니다.
        
        Args:
            key: 환경 변수 키
            default: 기본값
            
        Returns:
            환경 변수값 또는 기본값
        """
        return os.getenv(key, default)
    
    def save_config(self) -> None:
        """현재 설정을 파일에 저장합니다."""
        try:
            # 설정 디렉토리 생성
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            
            logger.info(f"설정 파일 저장 완료: {self.config_path}")
        except Exception as e:
            logger.error(f"설정 파일 저장 실패: {e}")
    
    def update(self, key: str, value: Any) -> None:
        """
        설정값을 업데이트합니다.
        
        Args:
            key: 설정 키 (점 표기법 지원)
            value: 새로운 값
        """
        keys = key.split('.')
        config = self.config
        
        # 마지막 키 전까지 탐색
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 마지막 키에 값 설정
        config[keys[-1]] = value
        logger.info(f"설정 업데이트: {key} = {value}")
    
    def reload(self) -> None:
        """설정을 다시 로드합니다."""
        self._load_env()
        self.config = self._load_config()
        self._set_defaults()
        logger.info("설정 재로드 완료")


# 전역 설정 관리자 인스턴스
config_manager = ConfigManager()
