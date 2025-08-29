#!/usr/bin/env python3
"""
Donmoa 기능 테스트 스크립트

이 스크립트는 Donmoa의 주요 기능들을 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from donmoa import Donmoa
    from donmoa.providers.securities import MockSecuritiesProvider
    from donmoa.core.scheduler import DonmoaScheduler
    from donmoa.utils.config import config_manager
    from donmoa.utils.encryption import encryption_manager

    print("✅ 모든 모듈 import 성공")

except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    print("프로젝트 구조를 확인해주세요.")
    sys.exit(1)


def test_basic_functionality():
    """기본 기능 테스트"""
    print("\n🔧 기본 기능 테스트 시작")

    try:
        # 1. Donmoa 초기화
        donmoa = Donmoa()
        print("✅ Donmoa 초기화 성공")

        # 2. Provider 추가
        mock_provider = MockSecuritiesProvider("TestSecurities")
        donmoa.add_provider(mock_provider)
        print("✅ Provider 추가 성공")

        # 3. 상태 확인
        status = donmoa.get_status()
        print(f"✅ 상태 확인 성공: {len(status['providers']['names'])}개 Provider")

        # 4. Provider 정보 확인
        provider_info = donmoa.get_provider_info("TestSecurities")
        print(f"✅ Provider 정보 확인 성공: {provider_info['type']}")

        return donmoa

    except Exception as e:
        print(f"❌ 기본 기능 테스트 실패: {e}")
        return None


def test_data_collection(donmoa):
    """데이터 수집 테스트"""
    print("\n📊 데이터 수집 테스트 시작")

    try:
        # 데이터 수집
        collected_data = donmoa.collect_data()
        print(f"✅ 데이터 수집 성공: {len(collected_data)}개 Provider")

        # 수집 요약 확인
        summary = donmoa.data_collector.get_collection_summary()
        print(f"✅ 수집 요약 생성 성공: {summary['total_data_count']}건 데이터")

        # 데이터 통계 확인
        stats = donmoa.data_collector.get_data_statistics()
        print(f"✅ 데이터 통계 생성 성공: {len(stats)}개 Provider")

        return collected_data

    except Exception as e:
        print(f"❌ 데이터 수집 테스트 실패: {e}")
        return None


def test_csv_export(donmoa, collected_data):
    """CSV 내보내기 테스트"""
    print("\n📁 CSV 내보내기 테스트 시작")

    try:
        # CSV 내보내기
        exported_files = donmoa.export_to_csv(collected_data)
        print(f"✅ CSV 내보내기 성공: {len(exported_files)}개 파일")

        # 파일 존재 확인
        for file_type, file_path in exported_files.items():
            if file_type != 'summary':
                if Path(file_path).exists():
                    file_size = Path(file_path).stat().st_size
                    print(f"  ✅ {file_type}: {file_path} ({file_size} bytes)")
                else:
                    print(f"  ❌ {file_type}: 파일이 존재하지 않음")

        return exported_files

    except Exception as e:
        print(f"❌ CSV 내보내기 테스트 실패: {e}")
        return None


def test_scheduler(donmoa):
    """스케줄러 테스트"""
    print("\n⏰ 스케줄러 테스트 시작")

    try:
        # 스케줄러 생성
        scheduler = DonmoaScheduler(donmoa)
        print("✅ 스케줄러 생성 성공")

        # 작업 추가
        scheduler.add_daily_job(
            name="test_daily",
            time="10:00",
            job_func=lambda: print("일일 작업 실행"),
            description="테스트용 일일 작업"
        )

        scheduler.add_interval_job(
            name="test_interval",
            interval_hours=2,
            job_func=lambda: print("주기 작업 실행"),
            description="테스트용 주기 작업"
        )

        print("✅ 작업 등록 성공")

        # 상태 확인
        status = scheduler.get_status()
        print(f"✅ 스케줄러 상태 확인 성공: {status['total_jobs']}개 작업")

        # 작업 즉시 실행 테스트
        scheduler.run_job_now("test_daily")
        print("✅ 작업 즉시 실행 성공")

        return scheduler

    except Exception as e:
        print(f"❌ 스케줄러 테스트 실패: {e}")
        return None


def test_utilities():
    """유틸리티 기능 테스트"""
    print("\n🛠️ 유틸리티 기능 테스트 시작")

    try:
        # 설정 관리자 테스트
        config_value = config_manager.get('schedule.enabled')
        print(f"✅ 설정 관리자 테스트 성공: schedule.enabled = {config_value}")

        # 암호화 관리자 테스트
        test_data = "test_secret_data"
        encrypted = encryption_manager.encrypt(test_data)
        decrypted = encryption_manager.decrypt(encrypted)

        if decrypted == test_data:
            print("✅ 암호화 관리자 테스트 성공")
        else:
            print("❌ 암호화 관리자 테스트 실패: 복호화된 데이터가 원본과 다름")

        return True

    except Exception as e:
        print(f"❌ 유틸리티 기능 테스트 실패: {e}")
        return False


def test_full_workflow(donmoa):
    """전체 워크플로우 테스트"""
    print("\n🚀 전체 워크플로우 테스트 시작")

    try:
        # 전체 워크플로우 실행
        result = donmoa.run_full_workflow()

        if result['status'] == 'success':
            print("✅ 전체 워크플로우 실행 성공")
            print(f"   - 실행 시간: {result['workflow_duration_seconds']:.2f}초")
            print(f"   - 수집된 데이터: {result['total_data_records']}건")
            print(f"   - 생성된 파일: {len(result['exported_files'])}개")

            # 결과 저장
            result_file = donmoa.save_workflow_result()
            print(f"   - 결과 저장: {result_file}")

            return True
        else:
            print(f"❌ 전체 워크플로우 실행 실패: {result.get('error_message', '알 수 없는 오류')}")
            return False

    except Exception as e:
        print(f"❌ 전체 워크플로우 테스트 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    print("🧪 Donmoa 기능 테스트 시작")
    print("=" * 50)

    # 테스트 결과 추적
    test_results = []

    try:
        # 1. 기본 기능 테스트
        donmoa = test_basic_functionality()
        test_results.append(("기본 기능", donmoa is not None))

        if donmoa is None:
            print("❌ 기본 기능 테스트 실패로 인해 중단")
            return

        # 2. 데이터 수집 테스트
        collected_data = test_data_collection(donmoa)
        test_results.append(("데이터 수집", collected_data is not None))

        # 3. CSV 내보내기 테스트
        if collected_data:
            exported_files = test_csv_export(donmoa, collected_data)
            test_results.append(("CSV 내보내기", exported_files is not None))

        # 4. 스케줄러 테스트
        scheduler = test_scheduler(donmoa)
        test_results.append(("스케줄러", scheduler is not None))

        # 5. 유틸리티 기능 테스트
        utils_success = test_utilities()
        test_results.append(("유틸리티", utils_success))

        # 6. 전체 워크플로우 테스트
        workflow_success = test_full_workflow(donmoa)
        test_results.append(("전체 워크플로우", workflow_success))

    except Exception as e:
        print(f"❌ 테스트 실행 중 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()

    # 테스트 결과 요약
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)

    passed = 0
    total = len(test_results)

    for test_name, success in test_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:15} : {status}")
        if success:
            passed += 1

    print("-" * 50)
    print(f"총 테스트: {total}개")
    print(f"성공: {passed}개")
    print(f"실패: {total - passed}개")
    print(f"성공률: {(passed/total*100):.1f}%")

    if passed == total:
        print("\n🎉 모든 테스트가 성공했습니다!")
    else:
        print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")

    print("\n테스트 완료!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 치명적 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
