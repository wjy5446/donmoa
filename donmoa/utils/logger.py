"""
로깅 유틸리티 모듈
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "donmoa",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console_output: bool = True,
) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.

    Args:
        name: 로거 이름
        level: 로그 레벨
        log_file: 로그 파일 경로 (None이면 파일 출력 안함)
        console_output: 콘솔 출력 여부

    Returns:
        설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 설정되어 있다면 중복 설정 방지
    if logger.handlers:
        return logger

    logger.setLevel(level)

    # 로그 포맷 설정
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 콘솔 출력 핸들러
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # 파일 출력 핸들러
    if log_file:
        # 로그 디렉토리 생성
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "donmoa") -> logging.Logger:
    """
    기존 로거를 반환하거나 새로 생성합니다.

    Args:
        name: 로거 이름

    Returns:
        로거 인스턴스
    """
    return logging.getLogger(name)


# 기본 로거 인스턴스
logger = setup_logger()


class LoggerMixin:
    """로거를 포함하는 클래스들의 믹스인"""

    @property
    def logger(self) -> logging.Logger:
        """클래스별 로거를 반환합니다."""
        return get_logger(f"{self.__class__.__module__}.{self.__class__.__name__}")
