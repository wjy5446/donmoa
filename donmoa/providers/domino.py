"""
도미노 앱 MHTML 파싱 기반 증권사 Provider
"""

import re
import quopri
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from bs4 import BeautifulSoup

from ..utils.logger import logger
from .base import BaseProvider


class DominoProvider(BaseProvider):
    """도미노 앱 HTML 파싱 기반 증권사 Provider"""

    def __init__(self, name: str, credentials: Dict[str, str] = None):
        super().__init__(name, "securities", credentials)
        self.html_files = {}

        # Provider 설정 로드
        self.provider_config = self._load_provider_config()

    def _load_provider_config(self) -> Dict[str, Any]:
        """Provider 설정을 로드합니다."""
        from ..utils.config import config_manager

        return config_manager.get_provider_config("domino")

    def get_file_patterns(self) -> Dict[str, str]:
        """파일 패턴을 가져옵니다."""
        return self.provider_config.get("manual_files", {}).get("file_patterns", {})

    def get_account_mapping(self) -> Dict[str, str]:
        """계좌 매핑을 가져옵니다."""
        return self.provider_config.get("account_mapping", {})

    def download_data(self, output_dir: Path) -> Dict[str, Path]:
        """
        수동 파일에서 HTML 파일을 읽습니다.

        Args:
            output_dir: 파일이 있는 디렉토리

        Returns:
            읽은 파일 경로들
        """
        downloaded_files = {}

        # 수동 파일만 사용 - data/input 디렉토리에서 찾기
        logger.info(f"{self.name} 수동 파일 사용")
        file_patterns = self.get_file_patterns()

        # input 디렉토리 설정
        input_dir = Path("data/input")
        if not input_dir.exists():
            logger.warning(f"입력 디렉토리가 존재하지 않습니다: {input_dir}")
            return downloaded_files

        for data_type in ["balances", "positions", "transactions"]:
            if data_type in file_patterns:
                pattern = file_patterns[data_type]
                manual_file = self._find_manual_file(input_dir, data_type, pattern)
                if manual_file:
                    downloaded_files[data_type] = manual_file

        if downloaded_files:
            logger.info(f"{self.name} HTML 파일 준비 완료: {len(downloaded_files)}개")
        else:
            logger.warning(f"{self.name} HTML 파일을 찾을 수 없습니다")

        return downloaded_files

    def _find_manual_file(
        self, directory: Path, data_type: str, pattern: str
    ) -> Optional[Path]:
        """수동으로 다운로드한 파일을 찾습니다."""
        try:
            matching_files = list(directory.glob(pattern))
            if matching_files:
                # 가장 최근 파일 선택
                latest_file = max(matching_files, key=lambda f: f.stat().st_mtime)
                logger.info(f"{data_type} 수동 파일 발견: {latest_file}")
                return latest_file
        except Exception as e:
            logger.error(f"{data_type} 파일 검색 오류: {e}")

        return None

    def parse_data(
        self, file_paths: Dict[str, Path]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        HTML/Excel 파일을 파싱하여 구조화된 데이터로 변환합니다.

        Args:
            file_paths: 파싱할 HTML/Excel 파일 경로들

        Returns:
            파싱된 데이터
        """
        parsed_data = {}

        try:
            # 잔고 정보 파싱
            if "balances" in file_paths and file_paths["balances"].exists():
                balances = self._parse_balances(file_paths["balances"])
                if balances:
                    parsed_data["balances"] = balances
                    logger.info(f"{self.name} 잔고 파싱 완료: {len(balances)}건")

            # 포지션 정보 파싱
            if "positions" in file_paths and file_paths["positions"].exists():
                positions = self._parse_positions(file_paths["positions"])
                if positions:
                    parsed_data["positions"] = positions
                    logger.info(f"{self.name} 포지션 파싱 완료: {len(positions)}건")

            # 거래 내역 파싱 (배당 내역 제외)
            if "transactions" in file_paths and file_paths["transactions"].exists():
                transactions = self._parse_transactions(file_paths["transactions"])
                if transactions:
                    # 배당 내역 필터링 (기획서 수정사항 반영)
                    filtered_transactions = [
                        tx
                        for tx in transactions
                        if tx.get("type") != "dividend" and tx.get("type") != "배당"
                    ]
                    parsed_data["transactions"] = filtered_transactions
                    logger.info(
                        f"{self.name} 거래내역 파싱 완료: {len(filtered_transactions)}건 (배당 제외)"
                    )

        except Exception as e:
            logger.error(f"{self.name} HTML/Excel 파싱 오류: {e}")

        return parsed_data

    def _parse_balances(self, file_path: Path) -> List[Dict[str, Any]]:
        """잔고 정보 MHTML을 파싱합니다."""
        try:
            file_ext = file_path.suffix.lower()

            if file_ext == ".mhtml":
                return self._parse_mhtml_cash(file_path)
            else:
                logger.error(f"지원하지 않는 파일 형식: {file_ext}")
                return []

        except Exception as e:
            logger.error(f"잔고 파일 파싱 실패: {e}")
            return []

    def _parse_balance_sheet(
        self, df: pd.DataFrame, sheet_name: str
    ) -> List[Dict[str, Any]]:
        """잔고 Excel 시트를 파싱합니다."""
        try:
            balances = []

            # Excel 시트 구조에 맞춰 파싱 로직 구현
            # 실제 구현에서는 실제 Excel 구조를 분석하여 수정 필요
            for _, row in df.iterrows():
                try:
                    account = str(row.get("계좌번호", row.get("account", "")))
                    balance_text = str(row.get("잔액", row.get("balance", "0")))
                    available_text = str(
                        row.get("가용잔액", row.get("available_balance", "0"))
                    )

                    # 숫자 추출
                    balance = self._extract_number(balance_text)
                    available = self._extract_number(available_text)

                    balances.append(
                        {
                            "account": account,
                            "balance": balance,
                            "available_balance": available,
                            "currency": "KRW",
                            "sheet_name": sheet_name,
                            "provider": self.name,
                            "parsed_at": datetime.now().isoformat(),
                        }
                    )

                except Exception as e:
                    logger.warning(f"잔고 Excel 항목 파싱 실패: {e}")
                    continue

            return balances

        except Exception as e:
            logger.error(f"잔고 Excel 시트 파싱 실패: {e}")
            return []

    def _parse_positions(self, file_path: Path) -> List[Dict[str, Any]]:
        """포지션 정보 MHTML을 파싱합니다."""
        try:
            file_ext = file_path.suffix.lower()

            if file_ext == ".mhtml":
                return self._parse_mhtml_positions(file_path)
            else:
                logger.error(f"지원하지 않는 파일 형식: {file_ext}")
                return []

        except Exception as e:
            logger.error(f"포지션 파일 파싱 실패: {e}")
            return []

    def _parse_transactions(self, file_path: Path) -> List[Dict[str, Any]]:
        """거래 내역 HTML을 파싱합니다 (배당 제외)."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, "html.parser")
            transactions = []

            # 도미노 앱 HTML 구조에 맞춰 파싱 로직 구현
            transaction_elements = soup.find_all("div", class_="transaction-item")

            for element in transaction_elements:
                try:
                    # 배당 내역인지 확인 (기획서 수정사항 반영)
                    transaction_type = element.find("span", class_="type").text.strip()
                    if (
                        "배당" in transaction_type
                        or "dividend" in transaction_type.lower()
                    ):
                        continue  # 배당 내역 제외

                    date_text = element.find("span", class_="date").text.strip()
                    time_text = element.find("span", class_="time").text.strip()
                    symbol = element.find("span", class_="symbol").text.strip()
                    quantity_text = element.find("span", class_="quantity").text.strip()
                    amount_text = element.find("span", class_="amount").text.strip()

                    # 날짜 파싱
                    date = self._parse_date(date_text)

                    # 숫자 추출
                    quantity = self._extract_number(quantity_text)
                    amount = self._extract_number(amount_text)

                    transactions.append(
                        {
                            "date": date.strftime("%Y-%m-%d"),
                            "time": time_text,
                            "type": transaction_type,
                            "symbol": symbol,
                            "quantity": quantity,
                            "amount": amount,
                            "currency": "KRW",
                            "provider": self.name,
                            "parsed_at": datetime.now().isoformat(),
                        }
                    )

                except Exception as e:
                    logger.warning(f"거래내역 항목 파싱 실패: {e}")
                    continue

            return transactions

        except Exception as e:
            logger.error(f"거래내역 HTML 파싱 실패: {e}")
            return []

    def _extract_number(self, text: str) -> float:
        """텍스트에서 숫자를 추출합니다."""
        try:
            # 쉼표, 원화 기호, 공백 제거 후 숫자 추출
            cleaned = re.sub(r"[^\d.-]", "", text)
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0

    def _parse_mhtml_cash(self, file_path: Path) -> List[Dict[str, Any]]:
        """MHTML 파일에서 현금 데이터를 파싱합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content = quopri.decodestring(content.encode('latin1')).decode('utf-8', errors='ignore')

            # MHTML에서 HTML 부분 추출
            html_start = content.find('<!DOCTYPE html>')
            html_content = content[html_start:]

            soup = BeautifulSoup(html_content, 'html.parser')
            cash_data = []

            # "현금" h2를 가진 article 찾기
            cash_article = soup.find("h2", string="현금")
            if cash_article:
                cash_article = cash_article.find_parent("article")

                # 원화/달러/엔 정보 추출
                for li in cash_article.find_all("li"):
                    spans = li.find_all("span")
                    if len(spans) >= 3:
                        currency = spans[2].get_text(strip=True)   # "원", "달러", "엔"
                        value_text = spans[-1].get_text(strip=True)
                        numeric_value = float(re.sub(r"[^\d.]", "", value_text))

                        cash_data.append({
                            'account': f"현금_{currency}",
                            'balance': numeric_value,
                            'available_balance': numeric_value,
                            'currency': currency,
                            'provider': self.name,
                            'parsed_at': datetime.now().isoformat(),
                        })

            logger.info(f"{self.name} 현금 데이터 파싱 완료: {len(cash_data)}건")
            return cash_data

        except Exception as e:
            logger.error(f"현금 MHTML 파싱 실패: {e}")
            return []

    def _parse_mhtml_positions(self, file_path: Path) -> List[Dict[str, Any]]:
        """MHTML 파일에서 포지션 데이터를 파싱합니다."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                content = quopri.decodestring(content.encode('latin1')).decode('utf-8', errors='ignore')

            # MHTML에서 HTML 부분 추출
            html_start = content.find('<!DOCTYPE html>')
            html_content = content[html_start:]

            soup = BeautifulSoup(html_content, 'html.parser')
            all_data = []

            # 테이블 구조 분석
            tables = soup.find_all('table')
            logger.info(f"발견된 테이블 개수: {len(tables)}")

            # 포지션 테이블 찾기
            position_tables = soup.find_all('table')

            for position_table in position_tables:
                # 헤더 분석
                thead = position_table.find('thead')
                headers = []
                if thead:
                    header_cells = thead.find_all('th')
                    for i, header in enumerate(header_cells):
                        span = header.find('span')
                        if span and span.contents:
                            text = span.contents[0].strip()
                            headers.append(text)
                        else:
                            headers.append(f"Column_{i}")

                # 데이터 행 분석
                tbody = position_table.find('tbody')
                if tbody:
                    rows = tbody.find_all('tr')

                    for row_idx, row in enumerate(rows):
                        is_asset = row.find("span", attrs={"direction": "vertical"}) is not None
                        cells = row.find_all('td')

                        # 자산명과 티커 추출
                        cell_first = cells[0]
                        name = ""
                        ticker = ""
                        if is_asset:
                            span_names = cell_first.find("span", attrs={"direction": "vertical"}).find_all("span")
                            if len(span_names) >= 2:
                                name = span_names[0].get_text().strip()
                                ticker = span_names[1].get_text().strip()
                        else:
                            name = cell_first.get_text().strip()
                            ticker = ""

                        # 행 데이터 구성
                        row_data = {
                            'name': name,
                            'ticker': ticker,
                            'is_asset': is_asset
                        }

                        # 나머지 셀 데이터 추가
                        for i, cell in enumerate(cells[1:]):
                            text = cell.get_text().strip()
                            if i < len(headers) - 1:  # 헤더 개수에 맞춰 조정
                                column_name = headers[i + 1] if i + 1 < len(headers) else f"column_{i + 1}"
                                row_data[column_name] = text

                        all_data.append(row_data)

            # 계좌별 자산 보유량으로 변환
            account_assets = []
            current_asset = None

            for row_data in all_data:
                if row_data['is_asset']:  # 자산 총합 행
                    current_asset = {
                        'asset_name': row_data['name'],
                        'ticker': row_data['ticker'] if row_data['ticker'] else '',
                    }
                else:  # 계좌별 보유량 행
                    if current_asset and row_data['name'].strip():  # 계좌명이 있는 경우만
                        # 숫자 값들을 정리
                        evaluation_amount = self._extract_number(row_data.get('평가액', '0'))
                        quantity = self._extract_number(row_data.get('보유량', '0'))
                        avg_price = self._extract_number(row_data.get('평단가', '0'))

                        # 0원인 계좌는 제외 (실제 보유량이 없는 경우)
                        if evaluation_amount > 0:
                            account_assets.append({
                                'account': row_data['name'],
                                'symbol': current_asset['ticker'],
                                'symbol_name': current_asset['asset_name'],
                                'quantity': quantity,
                                'average_price': avg_price,
                                'market_value': evaluation_amount,
                                'currency': 'KRW',
                                'provider': self.name,
                                'parsed_at': datetime.now().isoformat(),
                            })

            logger.info(f"{self.name} 포지션 데이터 파싱 완료: {len(account_assets)}건")
            return account_assets

        except Exception as e:
            logger.error(f"포지션 MHTML 파싱 실패: {e}")
            return []

    def _parse_date(self, date_text: str) -> datetime:
        """날짜 텍스트를 파싱합니다."""
        try:
            # 다양한 날짜 형식 지원
            formats = ["%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%m/%d/%Y"]

            for fmt in formats:
                try:
                    return datetime.strptime(date_text, fmt)
                except ValueError:
                    continue

            # 파싱 실패 시 현재 날짜 반환
            logger.warning(f"날짜 파싱 실패: {date_text}")
            return datetime.now()

        except Exception as e:
            logger.error(f"날짜 파싱 오류: {e}")
            return datetime.now()
