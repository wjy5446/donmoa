"""
설정 관리 유틸리티 모듈
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """설정 파일 관리 클래스"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        ConfigManager 초기화

        Args:
            config_path: 설정 파일 경로 (None이면 기본 경로 사용)
        """
        self.config_path = config_path or Path("config/config.yaml")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """설정 파일을 로드합니다."""
        if not self.config_path.exists():
            logger.warning(f"설정 파일을 찾을 수 없습니다: {self.config_path}")
            return {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info(f"설정 파일 로드 완료: {self.config_path}")

                # 계좌 설정 로드 (여전히 외부 파일 사용)
                if config and "accounts" in config:
                    config["accounts_config"] = self._load_external_config(
                        config["accounts"], "Accounts"
                    )

                return config or {}
        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return {}

    def _load_external_config(self, config_path: str, config_name: str) -> Dict[str, Any]:
        """외부 설정 파일을 로드합니다."""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"{config_name} 설정 파일을 찾을 수 없습니다: {config_path}")
                return {}

            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                logger.info(f"{config_name} 설정 로드 완료")
                return config or {}
        except Exception as e:
            logger.error(f"{config_name} 설정 로드 실패: {e}")
            return {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        설정값을 가져옵니다.

        Args:
            key: 설정 키 (점 표기법 지원, 예: 'export.output_dir')
            default: 기본값

        Returns:
            설정값 또는 기본값
        """
        keys = key.split(".")
        value = self.config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """특정 Provider의 설정을 가져옵니다."""
        providers = self.config.get("providers", {})
        return providers.get(provider_name, {})

    def get_accounts_config(self) -> Dict[str, Any]:
        """계좌 설정을 가져옵니다."""
        return self.config.get("accounts_config", {})

    def get_accounts(self) -> List[Dict[str, Any]]:
        """계좌 목록을 가져옵니다."""
        accounts_config = self.get_accounts_config()
        return accounts_config.get("accounts", [])

    def get_providers(self) -> Dict[str, Dict[str, Any]]:
        """모든 Provider 설정을 가져옵니다."""
        return self.config.get("providers", {})

    def reload(self) -> None:
        """설정을 다시 로드합니다."""
        self.config = self._load_config()


# 전역 설정 관리자 인스턴스
config_manager = ConfigManager()
