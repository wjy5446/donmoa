#!/usr/bin/env python3
"""
파일 파싱 테스트 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from donmoa.providers.banksalad import BanksaladProvider
from donmoa.providers.domino import DominoProvider

def test_banksalad_excel():
    """뱅크샐러드 Excel 파일 파싱 테스트"""
    print("=== 뱅크샐러드 Excel 파일 파싱 테스트 ===")

    try:
        # Provider 생성
        provider = BanksaladProvider("TestBank")
        print("✅ BanksaladProvider 생성 성공")

        # 파일 경로 설정
        input_dir = Path("data/input")
        excel_file = input_dir / "banksalad.xlsx"

        if not excel_file.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {excel_file}")
            return False

        print(f"✅ 파일 발견: {excel_file}")

        # 파일 다운로드 시뮬레이션
        downloaded_files = {'balances': excel_file, 'transactions': excel_file}

        # 데이터 파싱
        parsed_data = provider.parse_data(downloaded_files)
        print(f"✅ 데이터 파싱 완료: {len(parsed_data)}개 데이터 타입")

        for data_type, data in parsed_data.items():
            print(f"  - {data_type}: {len(data)}건")
            if data:
                print(f"    첫 번째 항목: {data[0]}")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_domino_mhtml():
    """도미노 MHTML 파일 파싱 테스트"""
    print("\n=== 도미노 MHTML 파일 파싱 테스트 ===")

    try:
        # Provider 생성
        provider = DominoProvider("TestSecurities")
        print("✅ DominoProvider 생성 성공")

        # 파일 경로 설정
        input_dir = Path("data/input")
        mhtml_file = input_dir / "domino.mhtml"

        if not mhtml_file.exists():
            print(f"❌ 파일을 찾을 수 없습니다: {mhtml_file}")
            return False

        print(f"✅ 파일 발견: {mhtml_file}")

        # 파일 다운로드 시뮬레이션
        downloaded_files = {'balances': mhtml_file, 'positions': mhtml_file, 'transactions': mhtml_file}

        # 데이터 파싱
        parsed_data = provider.parse_data(downloaded_files)
        print(f"✅ 데이터 파싱 완료: {len(parsed_data)}개 데이터 타입")

        for data_type, data in parsed_data.items():
            print(f"  - {data_type}: {len(data)}건")
            if data:
                print(f"    첫 번째 항목: {data[0]}")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 파일 파싱 테스트 시작\n")

    # 뱅크샐러드 테스트
    banksalad_success = test_banksalad_excel()

    # 도미노 테스트
    domino_success = test_domino_mhtml()

    # 결과 요약
    print("\n" + "="*50)
    print("📊 테스트 결과 요약")
    print("="*50)
    print(f"뱅크샐러드 Excel 파싱: {'✅ 성공' if banksalad_success else '❌ 실패'}")
    print(f"도미노 MHTML 파싱: {'✅ 성공' if domino_success else '❌ 실패'}")

    if banksalad_success and domino_success:
        print("\n🎉 모든 테스트가 성공했습니다!")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")

if __name__ == "__main__":
    main()
