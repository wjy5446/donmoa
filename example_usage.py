#!/usr/bin/env python3
"""
Donmoa 사용 예시

이 파일은 Donmoa를 사용하는 방법을 보여줍니다.
"""

from pathlib import Path
from donmoa.core import Donmoa
from donmoa.providers.securities import MockSecuritiesProvider
from donmoa.core.scheduler import DonmoaScheduler


def main():
    """Donmoa 사용 예시"""
    print("🚀 Donmoa 사용 예시 시작")
    
    # 1. Donmoa 인스턴스 생성
    print("\n1. Donmoa 초기화...")
    donmoa = Donmoa()
    
    # 2. Provider 추가 (모의 데이터 사용)
    print("\n2. Provider 추가...")
    mock_securities = MockSecuritiesProvider("MockSecurities")
    donmoa.add_provider(mock_securities)
    
    # 3. Provider 상태 확인
    print("\n3. Provider 상태 확인...")
    status = donmoa.get_status()
    print(f"등록된 Provider: {status['providers']['names']}")
    
    # 4. Provider 연결 테스트
    print("\n4. Provider 연결 테스트...")
    test_result = donmoa.test_provider_connection("MockSecurities")
    print(f"테스트 결과: {test_result['status']}")
    
    # 5. 데이터 수집 및 CSV 내보내기
    print("\n5. 데이터 수집 및 CSV 내보내기...")
    try:
        result = donmoa.run_full_workflow()
        
        if result['status'] == 'success':
            print(f"✅ 워크플로우 실행 성공!")
            print(f"   - 수집된 Provider: {result['collected_providers']}")
            print(f"   - 총 데이터 레코드: {result['total_data_records']}")
            print(f"   - 실행 시간: {result['workflow_duration_seconds']:.2f}초")
            print(f"   - 생성된 CSV 파일:")
            
            for file_type, file_path in result['exported_files'].items():
                if file_type != 'summary':
                    print(f"     * {file_type}: {file_path}")
        else:
            print(f"❌ 워크플로우 실행 실패: {result.get('error_message', '알 수 없는 오류')}")
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    # 6. 스케줄러 설정
    print("\n6. 스케줄러 설정...")
    scheduler = DonmoaScheduler(donmoa)
    
    # 일일 작업 추가
    scheduler.add_daily_job(
        name="daily_collection",
        time="09:00",
        job_func=scheduler._run_daily_collection,
        description="매일 오전 9시 데이터 수집"
    )
    
    # 4시간마다 실행하는 작업 추가
    scheduler.add_interval_job(
        name="periodic_collection",
        interval_hours=4,
        job_func=scheduler._run_periodic_collection,
        description="4시간마다 데이터 수집"
    )
    
    print("✅ 스케줄러 작업 등록 완료")
    
    # 7. 스케줄러 상태 확인
    print("\n7. 스케줄러 상태 확인...")
    scheduler_status = scheduler.get_status()
    print(f"등록된 작업 수: {scheduler_status['total_jobs']}")
    
    for job_name, job_info in scheduler_status['scheduled_jobs'].items():
        print(f"  - {job_name}: {job_info['type']} ({job_info['description']})")
    
    # 8. 워크플로우 결과 저장
    print("\n8. 워크플로우 결과 저장...")
    if donmoa.last_run_result:
        result_file = donmoa.save_workflow_result()
        print(f"✅ 결과 저장 완료: {result_file}")
    
    print("\n🎉 Donmoa 사용 예시 완료!")
    print("\n다음 명령어로 CLI를 사용할 수 있습니다:")
    print("  python -m donmoa collect          # 데이터 수집 및 CSV 내보내기")
    print("  python -m donmoa status           # 상태 확인")
    print("  python -m donmoa scheduler start  # 스케줄러 시작")
    print("  python -m donmoa scheduler status # 스케줄러 상태 확인")


def demo_simple_usage():
    """간단한 사용 예시"""
    print("\n🔧 간단한 사용 예시")
    
    # Donmoa 인스턴스 생성
    donmoa = Donmoa()
    
    # 모의 Provider 추가
    mock_provider = MockSecuritiesProvider("TestSecurities")
    donmoa.add_provider(mock_provider)
    
    # 데이터 수집
    print("데이터 수집 중...")
    collected_data = donmoa.collect_data()
    
    # CSV 내보내기
    print("CSV 내보내기 중...")
    exported_files = donmoa.export_to_csv(collected_data)
    
    print(f"✅ 완료! {len(exported_files)}개 파일 생성")
    
    return donmoa, collected_data, exported_files


if __name__ == "__main__":
    try:
        main()
        
        # 간단한 사용 예시도 실행
        demo_simple_usage()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ 사용자가 중단했습니다.")
    except Exception as e:
        print(f"\n\n❌ 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
