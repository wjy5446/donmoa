"""
Donmoa - 개인 자산 관리 도구

여러 증권사, 은행, 암호화폐 거래소의 데이터를 한 곳으로 모아
개인이 손쉽게 관리할 수 있도록 돕는 개인 자산 관리 도구입니다.
"""

__version__ = "0.1.0"
__author__ = "Donmoa Team"
__email__ = "contact@donmoa.com"

from .core import Donmoa
from .providers.base import BaseProvider

__all__ = ["Donmoa", "BaseProvider"]
