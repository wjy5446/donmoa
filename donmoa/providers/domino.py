"""
도미노 증권 Provider
"""

import re
import quopri
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

import pandas as pd
from bs4 import BeautifulSoup

from ..schemas import CashSchema, PositionSchema, TransactionSchema
from ..utils.logger import logger
from .base import BaseProvider


class DominoProvider(BaseProvider):
    """도미노 증권 MHTML 파일 파싱 Provider"""

    def __init__(self, name: str = "domino_securities", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

    def get_supported_names(self) -> List[str]:
        """지원하는 파일 이름 목록을 반환합니다."""
        return ["domino.mhtml"]

    def parse_raw(self, file_path: Path) -> Dict[str, pd.DataFrame]:
        """원본 데이터를 파싱합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content = quopri.decodestring(content.encode('latin1')).decode('utf-8', errors='ignore')

            soup = BeautifulSoup(content, 'html.parser')

            dict_datas = {
                "cash": pd.DataFrame(),
                "positions": pd.DataFrame()
            }

            #########################################################
            # 현금 데이터 파싱
            #########################################################
            cash_article = soup.find("h2", string="현금")
            if cash_article:
                cash_article = cash_article.find_parent("article")

                cash_headers = ["currency", "amount"]
                cash_datas = []
                for li in cash_article.find_all("li"):
                    spans = li.find_all("span")
                    if len(spans) >= 3:
                        currency = spans[2].get_text(strip=True)
                        value_text = spans[-1].get_text(strip=True)
                        amount = self._extract_number(value_text)
                        cash_datas.append([currency, amount])
                dict_datas["cash"] = pd.DataFrame(cash_datas, columns=cash_headers)

            #########################################################
            # 포지션 데이터 파싱
            #########################################################
            positions_tables = soup.find_all('table')
            if positions_tables:
                positions_headers = ["account", "name", "ticker", "quantity", "average_price"]
                positions_datas = []

                for table in positions_tables:
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
                            positions_datas.append({
                                'account': account_name,
                                'name': tmp_asset_info['name'],
                                'ticker': tmp_asset_info['ticker'],
                                'quantity': quantity,
                                'average_price': avg_price,
                            })

                dict_datas["positions"] = pd.DataFrame(positions_datas, columns=positions_headers)

            logger.info(f"현금 데이터 파싱 완료: {len(dict_datas['cash'])}건")
            logger.info(f"포지션 데이터 파싱 완료: {len(dict_datas['positions'])}건")

            return dict_datas

        except Exception as e:
            logger.error(f"데이터 파싱 실패: {e}")
            return {
                "cash": pd.DataFrame(),
                "positions": pd.DataFrame()
            }

    def parse_cash(self, data: Dict[str, pd.DataFrame]) -> List[CashSchema]:
        """현금 데이터를 파싱합니다"""
        df_cash = data["cash"]
        df_positions = data["positions"]

        cash_datas = []
        for _, row in df_cash.iterrows():
            currency = row["currency"]
            amount = row["amount"]

            cash_datas.append(CashSchema(
                date=datetime.now().strftime("%Y-%m-%d"),
                category="증권",
                account="증권",
                balance=amount,
                currency=self._convert_currency(currency),
                provider=self.name,
                collected_at=self._get_current_timestamp(),
            ))

        for _, row in df_positions.iterrows():
            name = row["name"]
            quantity = row["quantity"]
            average_price = row["average_price"]

            if "현금성자산" not in name:
                continue

            cash_datas.append(CashSchema(
                date=datetime.now().strftime("%Y-%m-%d"),
                category="증권",
                account=name,
                balance=quantity * average_price,
                currency="KRW",
                provider=self.name,
                collected_at=self._get_current_timestamp(),
            ))

        return cash_datas

    def parse_positions(self, data: Dict[str, pd.DataFrame]) -> List[PositionSchema]:
        """포지션 데이터를 파싱합니다"""
        df_positions = data["positions"]

        positions_datas = []
        for _, row in df_positions.iterrows():
            account = row["account"]
            name = row["name"]
            ticker = row["ticker"]
            quantity = row["quantity"]
            average_price = row["average_price"]

            if "현금성자산" in name:
                continue

            positions_datas.append(PositionSchema(
                date=datetime.now().strftime("%Y-%m-%d"),
                account=account,
                name=name,
                ticker=ticker,
                quantity=quantity,
                average_price=average_price,
                currency="KRW",
                provider=self.name,
                collected_at=self._get_current_timestamp(),
            ))

        return positions_datas

    def parse_transactions(self, data: Dict[str, pd.DataFrame]) -> List[TransactionSchema]:
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

    def _convert_currency(self, currency: str) -> str:
        """통화를 변환합니다"""
        if currency == "원":
            return "KRW"
        elif currency == "달러":
            return "USD"
        elif currency == "엔":
            return "JPY"
        elif currency == "유로":
            return "EUR"
        else:
            return currency
