"""
도미노 증권 Provider - 간소화된 구조 (설정 파일 호환)
"""

import re
import quopri
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

import pandas as pd
from bs4 import BeautifulSoup

from ..utils.logger import logger
from .base import BaseProvider


class DominoProvider(BaseProvider):
    """도미노 증권 MHTML 파일 파싱 Provider"""

    def __init__(self, name: str = "domino_securities", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 목록을 반환합니다."""
        return ["mhtml"]

    def parse_cash(self, file_path: Path) -> List[Dict[str, Any]]:
        """현금 데이터를 파싱합니다"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content = quopri.decodestring(content.encode('latin1')).decode('utf-8', errors='ignore')

            soup = BeautifulSoup(content, 'html.parser')
            cash_data = []

            # "현금" 섹션 찾기
            cash_article = soup.find("h2", string="현금")
            if cash_article:
                cash_article = cash_article.find_parent("article")

                for li in cash_article.find_all("li"):
                    spans = li.find_all("span")
                    if len(spans) >= 3:
                        currency = spans[2].get_text(strip=True)
                        value_text = spans[-1].get_text(strip=True)
                        amount = self._extract_number(value_text)

                        cash_data.append({
                            'account': f"현금_{currency}",
                            'balance': amount,
                            'currency': currency,
                            'provider': self.name,
                            'collected_at': datetime.now().isoformat(),
                        })

            logger.info(f"현금 데이터 파싱 완료: {len(cash_data)}건")
            return cash_data

        except Exception as e:
            logger.error(f"현금 파싱 실패: {e}")
            return []

    def parse_positions(self, file_path: Path) -> List[Dict[str, Any]]:
        """포지션 데이터를 파싱합니다"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content = quopri.decodestring(content.encode('latin1')).decode('utf-8', errors='ignore')

            soup = BeautifulSoup(content, 'html.parser')
            positions_data = []

            # 테이블에서 포지션 데이터 추출
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')

                tmp_asset_info = {}
                for row in rows:
                    cells = row.find_all('td')

                    if not cells:
                        continue

                    # 자산 정보 추출
                    asset_info = self._extract_asset_info(cells[0])
                    if asset_info:
                        tmp_asset_info = asset_info
                        continue

                    account_name = cells[0].get_text(strip=True)
                    if not account_name or account_name == "-":
                        continue

                    amount = self._extract_number(cells[1].get_text(strip=True))
                    quantity = self._extract_number(cells[2].get_text(strip=True))
                    avg_price = self._extract_number(cells[3].get_text(strip=True))

                    if amount > 0:  # 실제 보유량이 있는 경우만
                        positions_data.append({
                            'account': account_name,
                            'name': tmp_asset_info['name'],
                            'ticker': tmp_asset_info['ticker'],
                            'quantity': quantity,
                            'average_price': avg_price,
                            'currency': 'KRW',
                            'provider': self.name,
                            'collected_at': datetime.now().isoformat(),
                        })

            logger.info(f"포지션 데이터 파싱 완료: {len(positions_data)}건")
            return positions_data

        except Exception as e:
            logger.error(f"포지션 파싱 실패: {e}")
            return []

    def parse_transactions(self, file_path: Path) -> List[Dict[str, Any]]:
        """거래 데이터를 파싱합니다"""
        return []

    def _extract_asset_info(self, cell) -> Dict[str, str]:
        """자산 정보를 추출합니다"""
        try:
            # 자산명과 티커가 있는 span 찾기
            vertical_span = cell.find("span", attrs={"direction": "vertical"})
            if vertical_span:
                spans = vertical_span.find_all("span")
                if len(spans) >= 2:
                    return {
                        'name': spans[0].get_text(strip=True),
                        'ticker': spans[1].get_text(strip=True)
                    }
            return {}
        except Exception as e:
            logger.error(f"자산 정보 추출 실패: {e}")
            return {}

    def _extract_number(self, text: str) -> float:
        """텍스트에서 숫자를 추출합니다"""
        try:
            cleaned = re.sub(r"[^\d.-]", "", text)
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
