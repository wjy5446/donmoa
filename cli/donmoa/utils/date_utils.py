"""
날짜 관련 유틸리티 함수들
"""
from pathlib import Path
from datetime import datetime
from typing import Optional


def extract_date_from_folder_name(folder_path: Path) -> Optional[str]:
    """
    폴더 이름에서 날짜를 추출합니다.

    Args:
        folder_path: 날짜가 포함된 폴더 경로

    Returns:
        YYYY-MM-DD 형식의 날짜 문자열 또는 None
    """
    folder_name = folder_path.name

    # YYYY-MM-DD 형식인지 확인
    try:
        datetime.strptime(folder_name, "%Y-%m-%d")
        return folder_name
    except ValueError:
        pass

    # YYYYMMDD 형식인지 확인
    try:
        if len(folder_name) == 8 and folder_name.isdigit():
            date_obj = datetime.strptime(folder_name, "%Y%m%d")
            return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        pass

    # YYYY_MM_DD 형식인지 확인
    try:
        if folder_name.count('_') == 2:
            date_obj = datetime.strptime(folder_name, "%Y_%m_%d")
            return date_obj.strftime("%Y-%m-%d")
    except ValueError:
        pass

    return None


def get_date_from_input_folder(input_dir: Path) -> Optional[str]:
    """
    input 폴더에서 날짜 폴더를 찾아 날짜를 추출합니다.

    Args:
        input_dir: data/input 폴더 경로

    Returns:
        YYYY-MM-DD 형식의 날짜 문자열 또는 None
    """
    if not input_dir.exists():
        return None

    # input 폴더의 직접 하위 폴더들을 확인
    for item in input_dir.iterdir():
        if item.is_dir():
            date_str = extract_date_from_folder_name(item)
            if date_str:
                return date_str

    return None


def get_all_date_folders(input_dir: Path) -> list[tuple[str, Path]]:
    """
    input 폴더에서 모든 날짜 폴더를 찾아 반환합니다.

    Args:
        input_dir: data/input 폴더 경로

    Returns:
        (날짜문자열, 폴더경로) 튜플의 리스트
    """
    date_folders = []

    if not input_dir.exists():
        return date_folders

    for item in input_dir.iterdir():
        if item.is_dir():
            date_str = extract_date_from_folder_name(item)
            if date_str:
                date_folders.append((date_str, item))

    # 날짜순으로 정렬
    date_folders.sort(key=lambda x: x[0])
    return date_folders
