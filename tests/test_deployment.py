#!/usr/bin/env python3
"""
배포 환경 기능 테스트 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from donmoa.core.donmoa import Donmoa


def test_health_check():
    """시스템 상태 확인 테스트"""
    print("=== 시스템 상태 확인 테스트 ===")

    try:
        # Donmoa 인스턴스 생성
        donmoa = Donmoa()
        print("✅ Donmoa 인스턴스 생성 성공")

        # 상태 확인
        health_status = donmoa.check_health()
        print(f"✅ 상태 확인 완료: {len(health_status)}개 컴포넌트")

        for component, status in health_status.items():
            if component == 'providers':
                if isinstance(status, dict) and 'status' in status:
                    # Provider가 없는 경우
                    provider_status = status['status']
                    if provider_status['healthy']:
                        print(f"  ✅ {component}: {provider_status['message']}")
                    else:
                        print(f"  ❌ {component}: {provider_status['message']}")
                else:
                    # Provider가 있는 경우
                    for provider_name, provider_status in status.items():
                        if provider_status['healthy']:
                            print(f"    ✅ {provider_name}: {provider_status['message']}")
                        else:
                            print(f"    ❌ {provider_name}: {provider_status['message']}")
            else:
                if status['healthy']:
                    print(f"  ✅ {component}: {status['message']}")
                else:
                    print(f"  ❌ {component}: {status['message']}")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metrics_collection():
    """메트릭 수집 테스트"""
    print("\n=== 메트릭 수집 테스트 ===")

    try:
        # Donmoa 인스턴스 생성
        donmoa = Donmoa()
        print("✅ Donmoa 인스턴스 생성 성공")

        # 메트릭 수집
        metrics = donmoa.collect_metrics()
        print(f"✅ 메트릭 수집 완료: {len(metrics)}개 메트릭")

        for metric_name, data in metrics.items():
            print(f"  - {metric_name}: {data['value']} {data['unit']}")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backup_operations():
    """백업 작업 테스트"""
    print("\n=== 백업 작업 테스트 ===")

    try:
        # Donmoa 인스턴스 생성
        donmoa = Donmoa()
        print("✅ Donmoa 인스턴스 생성 성공")

        # 백업 목록 확인
        backups = donmoa.list_backups()
        print(f"✅ 백업 목록 확인 완료: {len(backups)}개 백업")

        if backups:
            for backup in backups:
                print(f"  - {backup['filename']}: {backup['size_mb']:.1f}MB ({backup['created_at']})")
        else:
            print("  - 백업이 없습니다")

        # 백업 생성
        backup_file = donmoa.create_backup()
        print(f"✅ 백업 생성 완료: {backup_file}")

        # 백업 목록 재확인
        backups_after = donmoa.list_backups()
        print(f"✅ 백업 생성 후 목록: {len(backups_after)}개 백업")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_maintenance_operations():
    """유지보수 작업 테스트"""
    print("\n=== 유지보수 작업 테스트 ===")

    try:
        # Donmoa 인스턴스 생성
        donmoa = Donmoa()
        print("✅ Donmoa 인스턴스 생성 성공")

        # 데이터 정리
        cleanup_result = donmoa.cleanup_old_data()
        print(f"✅ 데이터 정리 완료: {cleanup_result['message']}")

        # 저장소 최적화
        optimize_result = donmoa.optimize_storage()
        print(f"✅ 저장소 최적화 완료: {optimize_result['message']}")

        # 저장 공간 정리
        vacuum_result = donmoa.vacuum_storage()
        print(f"✅ 저장 공간 정리 완료: {vacuum_result['message']}")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_validation():
    """데이터 유효성 검증 테스트"""
    print("\n=== 데이터 유효성 검증 테스트 ===")

    try:
        # Donmoa 인스턴스 생성
        donmoa = Donmoa()
        print("✅ Donmoa 인스턴스 생성 성공")

        # 샘플 데이터로 검증 테스트
        sample_data = {
            'banksalad': {
                'balances': [
                    {'account': 'test1', 'balance': 1000},
                    {'account': 'test2', 'balance': 2000}
                ],
                'transactions': [
                    {'date': '2025-01-01', 'amount': 100},
                    {'date': '2025-01-02', 'amount': 200}
                ]
            }
        }

        # 데이터 유효성 검증
        validation_result = donmoa.validate_data(sample_data)
        print(f"✅ 데이터 유효성 검증 완료")
        print(f"  - 유효성: {'✅' if validation_result['is_valid'] else '❌'}")
        print(f"  - Provider 수: {validation_result['total_providers']}")
        print(f"  - 총 레코드: {validation_result['total_records']}")

        if validation_result['warnings']:
            print(f"  - 경고: {len(validation_result['warnings'])}개")
            for warning in validation_result['warnings']:
                print(f"    ⚠️ {warning}")

        return True

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """메인 테스트 함수"""
    print("🚀 배포 환경 기능 테스트 시작\n")

    # 각 테스트 실행
    tests = [
        ("시스템 상태 확인", test_health_check),
        ("메트릭 수집", test_metrics_collection),
        ("백업 작업", test_backup_operations),
        ("유지보수 작업", test_maintenance_operations),
        ("데이터 유효성 검증", test_data_validation)
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} 테스트 실행 중 오류: {e}")
            results[test_name] = False

    # 결과 요약
    print("\n" + "="*60)
    print("📊 배포 환경 기능 테스트 결과 요약")
    print("="*60)

    for test_name, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")

    success_count = sum(results.values())
    total_count = len(results)

    print(f"\n총 테스트: {total_count}개")
    print(f"성공: {success_count}개")
    print(f"실패: {total_count - success_count}개")
    print(f"성공률: {(success_count / total_count) * 100:.1f}%")

    if success_count == total_count:
        print("\n🎉 모든 테스트가 성공했습니다!")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")


if __name__ == "__main__":
    main()
