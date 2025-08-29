"""
암호화 유틸리티 모듈
"""
import os
import base64
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from .logger import get_logger

logger = get_logger(__name__)


class EncryptionManager:
    """API 키 등 민감한 정보를 안전하게 관리하는 클래스"""
    
    def __init__(self, key_file: Optional[Path] = None):
        """
        EncryptionManager 초기화
        
        Args:
            key_file: 암호화 키 파일 경로 (None이면 기본 경로 사용)
        """
        self.key_file = key_file or Path.home() / ".donmoa" / "encryption.key"
        self._fernet = None
        self._initialize_encryption()
    
    def _initialize_encryption(self) -> None:
        """암호화 키를 초기화하거나 로드합니다."""
        try:
            if self.key_file.exists():
                # 기존 키 로드
                with open(self.key_file, 'rb') as f:
                    key = f.read()
                self._fernet = Fernet(key)
                logger.info("기존 암호화 키 로드 완료")
            else:
                # 새 키 생성
                self._generate_new_key()
                logger.info("새 암호화 키 생성 완료")
        except Exception as e:
            logger.error(f"암호화 키 초기화 실패: {e}")
            # 백업으로 새 키 생성
            self._generate_new_key()
    
    def _generate_new_key(self) -> None:
        """새로운 암호화 키를 생성합니다."""
        try:
            # 키 디렉토리 생성
            self.key_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 새 키 생성
            key = Fernet.generate_key()
            
            # 키 파일에 저장
            with open(self.key_file, 'wb') as f:
                f.write(key)
            
            # 키 파일 권한 설정 (Unix 시스템에서만)
            if os.name != 'nt':  # Windows가 아닌 경우
                os.chmod(self.key_file, 0o600)
            
            self._fernet = Fernet(key)
            logger.info(f"새 암호화 키 생성 및 저장 완료: {self.key_file}")
        except Exception as e:
            logger.error(f"새 암호화 키 생성 실패: {e}")
            raise
    
    def encrypt(self, data: str) -> str:
        """
        데이터를 암호화합니다.
        
        Args:
            data: 암호화할 데이터
            
        Returns:
            암호화된 데이터 (base64 인코딩)
        """
        if not self._fernet:
            raise RuntimeError("암호화 키가 초기화되지 않았습니다")
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            logger.error(f"데이터 암호화 실패: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        암호화된 데이터를 복호화합니다.
        
        Args:
            encrypted_data: 복호화할 데이터 (base64 인코딩)
            
        Returns:
            복호화된 데이터
        """
        if not self._fernet:
            raise RuntimeError("암호화 키가 초기화되지 않았습니다")
        
        try:
            decoded_data = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode('utf-8')
        except Exception as e:
            logger.error(f"데이터 복호화 실패: {e}")
            raise
    
    def encrypt_file(self, input_file: Path, output_file: Optional[Path] = None) -> Path:
        """
        파일을 암호화합니다.
        
        Args:
            input_file: 암호화할 입력 파일
            output_file: 암호화된 출력 파일 (None이면 자동 생성)
            
        Returns:
            암호화된 파일 경로
        """
        if output_file is None:
            output_file = input_file.with_suffix(input_file.suffix + '.encrypted')
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            encrypted_content = self.encrypt(content)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(encrypted_content)
            
            logger.info(f"파일 암호화 완료: {input_file} -> {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"파일 암호화 실패: {e}")
            raise
    
    def decrypt_file(self, input_file: Path, output_file: Optional[Path] = None) -> Path:
        """
        암호화된 파일을 복호화합니다.
        
        Args:
            input_file: 복호화할 입력 파일
            output_file: 복호화된 출력 파일 (None이면 자동 생성)
            
        Returns:
            복호화된 파일 경로
        """
        if output_file is None:
            if input_file.suffix == '.encrypted':
                output_file = input_file.with_suffix('')
            else:
                output_file = input_file.with_suffix(input_file.suffix + '.decrypted')
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                encrypted_content = f.read()
            
            decrypted_content = self.decrypt(encrypted_content)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(decrypted_content)
            
            logger.info(f"파일 복호화 완료: {input_file} -> {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"파일 복호화 실패: {e}")
            raise
    
    def rotate_key(self) -> None:
        """암호화 키를 교체합니다."""
        try:
            # 새 키 생성
            new_key = Fernet.generate_key()
            new_fernet = Fernet(new_key)
            
            # 기존 키 백업
            backup_key_file = self.key_file.with_suffix('.backup')
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    old_key = f.read()
                with open(backup_key_file, 'wb') as f:
                    f.write(old_key)
                logger.info(f"기존 키 백업 완료: {backup_key_file}")
            
            # 새 키 저장
            with open(self.key_file, 'wb') as f:
                f.write(new_key)
            
            self._fernet = new_fernet
            logger.info("암호화 키 교체 완료")
        except Exception as e:
            logger.error(f"암호화 키 교체 실패: {e}")
            raise


# 전역 암호화 관리자 인스턴스
encryption_manager = EncryptionManager()
