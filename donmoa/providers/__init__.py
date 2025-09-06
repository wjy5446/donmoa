"""
간소화된 Provider 모듈들 - 설정 파일 호환
"""

from .base import BaseProvider
from .banksalad import BanksaladProvider
from .domino import DominoProvider

# Provider 팩토리 함수
def create_provider(provider_name: str, credentials: dict = None) -> BaseProvider:
    """Provider 이름으로 인스턴스를 생성합니다"""
    providers = {
        "domino": DominoProvider,
        "domino_securities": DominoProvider,
        "banksalad": BanksaladProvider,
        "banksalad_csv": BanksaladProvider,
    }

    if provider_name not in providers:
        raise ValueError(f"지원하지 않는 Provider: {provider_name}")

    return providers[provider_name](provider_name, credentials)

def get_available_providers() -> list:
    """사용 가능한 Provider 목록을 반환합니다"""
    return ["domino", "domino_securities", "banksalad", "banksalad_csv"]

__all__ = [
    "BaseProvider",
    "BanksaladProvider",
    "DominoProvider",
    "create_provider",
    "get_available_providers",
]
