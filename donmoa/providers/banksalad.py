"""
뱅크샐러드 Provider - 공통 스키마 출력
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

import pandas as pd
import openpyxl

from ..utils.logger import logger
from .base import BaseProvider


class BanksaladProvider(BaseProvider):
    """뱅크샐러드 Excel 파일 파싱 Provider"""

    def __init__(self, name: str = "banksalad_csv", config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)

    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 목록을 반환합니다."""
        return ["xlsx"]

    def parse_cash(self, file_path: Path) -> List[Dict[str, Any]]:
        """현금 데이터를 파싱합니다"""
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)

            if "뱅샐현황" not in workbook.sheetnames:
                logger.error("뱅샐현황 시트를 찾을 수 없습니다")
                return []

            sheet = workbook["뱅샐현황"]
            cash_data = []

            # "3.재무현황" 헤더 찾기
            header_cell = None
            for cell in sheet['B']:
                if cell.value and "3.재무현황" in str(cell.value):
                    header_cell = cell
                    break

            if not header_cell:
                logger.error("3.재무현황 헤더를 찾을 수 없습니다")
                return []

            # 재무현황 테이블 파싱
            table_start_row = header_cell.row + 3
            current_category = None

            for row in sheet.iter_rows(min_row=table_start_row, values_only=True):
                if not any(cell is not None for cell in row):
                    break

                category_text = row[1]  # B열
                if category_text:
                    current_category = self._get_category_type(category_text)
                if current_category == "기타":
                    continue

                account_name = row[2]  # C열
                amount = self._convert_to_number(row[4])  # E열

                if account_name and amount > 0 and current_category:
                    cash_data.append({
                        'account': str(account_name),
                        'balance': amount,
                        'currency': 'KRW',
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
        return []

    def parse_transactions(self, file_path: Path) -> List[Dict[str, Any]]:
        """거래내역 데이터를 파싱합니다"""
        try:
            if "가계부 내역" not in pd.ExcelFile(file_path).sheet_names:
                logger.error("가계부 내역 시트를 찾을 수 없습니다")
                return []

            # 가계부 내역 시트 읽기
            df = pd.read_excel(file_path, sheet_name="가계부 내역")

            # 최근 1개월 데이터만 필터링
            if "날짜" in df.columns:
                df["날짜"] = pd.to_datetime(df["날짜"])
                max_date = df["날짜"].max()
                start_date = max_date - pd.DateOffset(months=1)
                df = df[df["날짜"] >= start_date]

            transactions_data = []
            for _, row in df.iterrows():
                try:
                    transactions_data.append({
                        'date': row.get("날짜", "").strftime("%Y-%m-%d") if pd.notna(row.get("날짜")) else "",
                        'account': str(row.get("계좌명", "")),
                        'transaction_type': self._determine_transaction_type(row.get("내용", ""), row.get("금액", 0)),
                        'category': row.get("카테고리", ""),
                        'category_detail': row.get("세부카테고리", ""),
                        'amount': self._convert_to_number(row.get("금액", 0)),
                        'currency': 'KRW',
                        'note': str(row.get("내용", "")),
                        'provider': self.name,
                        'collected_at': datetime.now().isoformat(),
                    })
                except Exception as e:
                    logger.warning(f"거래내역 항목 파싱 실패: {e}")
                    continue

            logger.info(f"거래내역 데이터 파싱 완료: {len(transactions_data)}건")
            return transactions_data

        except Exception as e:
            logger.error(f"거래내역 파싱 실패: {e}")
            return []

    def _get_category_type(self, category_text: str) -> str:
        """카테고리 텍스트를 타입으로 변환합니다"""
        if "자유입출금" in category_text or "저축성" in category_text:
            return "은행"
        elif "전자금융" in category_text:
            return "페이"
        else:
            return "기타"

    def _convert_to_number(self, value) -> float:
        """값을 숫자로 변환합니다"""
        try:
            if pd.isna(value):
                return 0.0
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = value.replace(",", "").replace("원", "").replace("₩", "").strip()
                return float(cleaned) if cleaned else 0.0
            return 0.0
        except (ValueError, TypeError):
            return 0.0

    def _determine_transaction_type(self, description: str, amount: float) -> str:
        """거래 유형을 판별합니다"""
        if not description:
            return "기타"

        description_lower = description.lower()

        if any(keyword in description_lower for keyword in ["입금", "급여", "월급"]):
            return "입금"
        elif any(keyword in description_lower for keyword in ["출금", "이체", "송금", "결제"]):
            return "출금"
        elif any(keyword in description_lower for keyword in ["이자", "수익"]):
            return "이자"
        elif any(keyword in description_lower for keyword in ["수수료", "관리비"]):
            return "수수료"
        else:
            return "입금" if amount > 0 else "출금"
