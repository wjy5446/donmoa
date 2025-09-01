"""
뱅크샐러드 Excel/CSV 파싱 기반 은행/증권 잔고 Provider
"""
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd
from .base import BaseProvider
from ..utils.logger import logger


class BanksaladProvider(BaseProvider):
    """뱅크샐러드 CSV 파싱 기반 은행/증권 잔고 Provider"""

    def __init__(self, name: str, credentials: Dict[str, str] = None):
        super().__init__(name, "bank", credentials)
        self.data_files = {}

        # Provider 설정 로드
        self.provider_config = self._load_provider_config()

    def _load_provider_config(self) -> Dict[str, Any]:
        """Provider 설정을 로드합니다."""
        from ..utils.config import config_manager
        return config_manager.get_provider_config("banksalad_csv")

    def get_file_patterns(self) -> Dict[str, str]:
        """파일 패턴을 가져옵니다."""
        return self.provider_config.get('manual_files', {}).get('file_patterns', {})

    def get_account_mapping(self) -> Dict[str, str]:
        """계좌 매핑을 가져옵니다."""
        return self.provider_config.get('account_mapping', {})

    def download_data(self, output_dir: Path) -> Dict[str, Path]:
        """
        수동 파일에서 Excel/CSV 파일을 읽습니다.

        Args:
            output_dir: 파일이 있는 디렉토리

        Returns:
            읽은 파일 경로들
        """
        downloaded_files = {}

        # 수동 파일만 사용
        logger.info(f"{self.name} 수동 파일 사용")
        file_patterns = self.get_file_patterns()

        for data_type in ['balances', 'transactions']:
            if data_type in file_patterns:
                pattern = file_patterns[data_type]
                manual_file = self._find_manual_file(output_dir, data_type, pattern)
                if manual_file:
                    downloaded_files[data_type] = manual_file

        if downloaded_files:
            logger.info(f"{self.name} Excel/CSV 파일 준비 완료: {len(downloaded_files)}개")
        else:
            logger.warning(f"{self.name} Excel/CSV 파일을 찾을 수 없습니다")

        return downloaded_files

    def _find_manual_file(self, directory: Path, data_type: str, pattern: str) -> Optional[Path]:
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

    def parse_data(self, file_paths: Dict[str, Path]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Excel/CSV 파일을 파싱하여 구조화된 데이터로 변환합니다.

        Args:
            file_paths: 파싱할 Excel/CSV 파일 경로들

        Returns:
            파싱된 데이터
        """
        parsed_data = {}

        try:
            # 잔고 정보 파싱
            if 'balances' in file_paths and file_paths['balances'].exists():
                balances = self._parse_balances(file_paths['balances'])
                if balances:
                    parsed_data['balances'] = balances
                    logger.info(f"{self.name} 잔고 파싱 완료: {len(balances)}건")

            # 거래 내역 파싱
            if 'transactions' in file_paths and file_paths['transactions'].exists():
                transactions = self._parse_transactions(file_paths['transactions'])
                if transactions:
                    parsed_data['transactions'] = transactions
                    logger.info(f"{self.name} 거래내역 파싱 완료: {len(transactions)}건")

        except Exception as e:
            logger.error(f"{self.name} CSV 파싱 오류: {e}")

        return parsed_data

    def _parse_balances(self, file_path: Path) -> List[Dict[str, Any]]:
        """잔고 정보 Excel/CSV를 파싱합니다."""
        try:
            file_ext = file_path.suffix.lower()

            if file_ext in ['.xlsx', '.xls']:
                # Excel 파일 읽기
                excel_data = pd.read_excel(file_path, sheet_name=None)
                logger.info(f"잔고 Excel 파일 읽기 완료: {len(excel_data)}개 시트")

                balances = []
                for sheet_name, df in excel_data.items():
                    logger.info(f"시트 '{sheet_name}' 처리 중...")
                    sheet_balances = self._parse_balance_sheet(df, sheet_name)
                    balances.extend(sheet_balances)

                return balances

            elif file_ext == '.csv':
                # CSV 파일 읽기
                df = pd.read_csv(file_path, encoding='utf-8')
                logger.info(f"잔고 CSV 파일 읽기 완료: {len(df)}행")
                return self._parse_balance_sheet(df, 'main')

            else:
                logger.error(f"지원하지 않는 파일 형식: {file_ext}")
                return []

        except Exception as e:
            logger.error(f"잔고 파일 파싱 실패: {e}")
            return []

    def _parse_balance_sheet(self, df: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """잔고 시트/DataFrame을 파싱합니다."""
        try:
            balances = []
            for _, row in df.iterrows():
                try:
                    # 계좌 정보 추출
                    account = row.get('계좌명', row.get('account', ''))
                    institution = row.get('기관명', row.get('institution', ''))
                    balance_text = row.get('잔액', row.get('balance', '0'))
                    account_type = row.get('계좌구분', row.get('account_type', ''))

                    # 숫자 변환
                    balance = self._convert_to_number(balance_text)

                    # 통화 정보
                    currency = 'KRW'  # 기본값
                    if 'currency' in row:
                        currency = row['currency']
                    elif '통화' in row:
                        currency = row['통화']

                    balances.append({
                        'account': account,
                        'institution': institution,
                        'balance': balance,
                        'account_type': account_type,
                        'currency': currency,
                        'sheet_name': sheet_name,
                        'provider': self.name,
                        'parsed_at': datetime.now().isoformat()
                    })

                except Exception as e:
                    logger.warning(f"잔고 항목 파싱 실패: {e}")
                    continue

            return balances

        except Exception as e:
            logger.error(f"잔고 시트 파싱 실패: {e}")
            return []

    def _parse_transactions(self, file_path: Path) -> List[Dict[str, Any]]:
        """거래 내역 Excel/CSV를 파싱합니다."""
        try:
            file_ext = file_path.suffix.lower()

            if file_ext in ['.xlsx', '.xls']:
                # Excel 파일 읽기
                excel_data = pd.read_excel(file_path, sheet_name=None)
                logger.info(f"거래내역 Excel 파일 읽기 완료: {len(excel_data)}개 시트")

                transactions = []
                for sheet_name, df in excel_data.items():
                    logger.info(f"시트 '{sheet_name}' 처리 중...")
                    sheet_transactions = self._parse_transaction_sheet(df, sheet_name)
                    transactions.extend(sheet_transactions)

                return transactions

            elif file_ext == '.csv':
                # CSV 파일 읽기
                df = pd.read_csv(file_path, encoding='utf-8')
                logger.info(f"거래내역 CSV 파일 읽기 완료: {len(df)}행")
                return self._parse_transaction_sheet(df, 'main')

            else:
                logger.error(f"지원하지 않는 파일 형식: {file_ext}")
                return []

        except Exception as e:
            logger.error(f"거래내역 파일 파싱 실패: {e}")
            return []

    def _parse_transaction_sheet(self, df: pd.DataFrame, sheet_name: str) -> List[Dict[str, Any]]:
        """거래 내역 시트/DataFrame을 파싱합니다."""
        try:
            transactions = []

            # 뱅크샐러드 Excel/CSV 컬럼 구조에 맞춰 파싱
            # 실제 구현에서는 실제 파일 구조를 분석하여 수정 필요
            for _, row in df.iterrows():
                try:
                    # 거래 정보 추출
                    date_text = row.get('거래일자', row.get('date', ''))
                    time_text = row.get('거래시간', row.get('time', ''))
                    description = row.get('내용', row.get('description', ''))
                    amount_text = row.get('금액', row.get('amount', '0'))
                    balance_text = row.get('잔액', row.get('balance', '0'))
                    account = row.get('계좌명', row.get('account', ''))

                    # 날짜 파싱
                    date = self._parse_date(date_text)

                    # 숫자 변환
                    amount = self._convert_to_number(amount_text)
                    balance = self._convert_to_number(balance_text)

                    # 거래 유형 판별
                    transaction_type = self._determine_transaction_type(description, amount)

                    transactions.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'time': time_text,
                        'description': description,
                        'type': transaction_type,
                        'amount': amount,
                        'balance': balance,
                        'account': account,
                        'currency': 'KRW',
                        'sheet_name': sheet_name,
                        'provider': self.name,
                        'parsed_at': datetime.now().isoformat()
                    })

                except Exception as e:
                    logger.warning(f"거래내역 항목 파싱 실패: {e}")
                    continue

            return transactions

        except Exception as e:
            logger.error(f"거래내역 시트 파싱 실패: {e}")
            return []

    def _convert_to_number(self, value) -> float:
        """값을 숫자로 변환합니다."""
        try:
            if pd.isna(value):
                return 0.0

            if isinstance(value, (int, float)):
                return float(value)

            # 문자열인 경우 숫자 추출
            if isinstance(value, str):
                # 쉼표, 원화 기호, 공백 제거
                cleaned = value.replace(',', '').replace('원', '').replace('₩', '').strip()
                return float(cleaned) if cleaned else 0.0

            return 0.0

        except (ValueError, TypeError):
            return 0.0

    def _parse_date(self, date_text) -> datetime:
        """날짜 텍스트를 파싱합니다."""
        try:
            if pd.isna(date_text):
                return datetime.now()

            if isinstance(date_text, datetime):
                return date_text

            # 문자열인 경우 파싱
            if isinstance(date_text, str):
                # 다양한 날짜 형식 지원
                formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%m/%d/%Y', '%Y%m%d']

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

    def _determine_transaction_type(self, description: str, amount: float) -> str:
        """거래 설명과 금액을 기반으로 거래 유형을 판별합니다."""
        description_lower = description.lower()

        # 입금 관련
        if any(keyword in description_lower for keyword in ['입금', '입금', '급여', '월급', '월급여']):
            return '입금'

        # 출금 관련
        if any(keyword in description_lower for keyword in ['출금', '출금', '이체', '송금', '결제']):
            return '출금'

        # 이자 관련
        if any(keyword in description_lower for keyword in ['이자', '이자수익', '이자지급']):
            return '이자'

        # 수수료 관련
        if any(keyword in description_lower for keyword in ['수수료', '관리비', '서비스비']):
            return '수수료'

        # 기본값: 금액 기반 판별
        if amount > 0:
            return '입금'
        elif amount < 0:
            return '출금'
        else:
            return '기타'
