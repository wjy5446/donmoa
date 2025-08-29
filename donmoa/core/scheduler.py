"""
자동 스케줄링 기능 모듈
"""
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
import json

from .donmoa import Donmoa
from ..utils.logger import LoggerMixin
from ..utils.config import config_manager


class DonmoaScheduler(LoggerMixin):
    """Donmoa 자동 스케줄링 클래스"""
    
    def __init__(self, donmoa: Donmoa):
        """
        DonmoaScheduler 초기화
        
        Args:
            donmoa: Donmoa 인스턴스
        """
        self.donmoa = donmoa
        self.scheduler_thread = None
        self.is_running = False
        self.scheduled_jobs: Dict[str, Any] = {}
        self.job_history: List[Dict[str, Any]] = []
        
        # 설정에서 스케줄 정보 로드
        self._load_schedule_config()
        
        # 기본 작업 등록
        self._register_default_jobs()
    
    def _load_schedule_config(self) -> None:
        """설정에서 스케줄 정보를 로드합니다."""
        self.schedule_enabled = config_manager.get('schedule.enabled', True)
        self.default_interval_hours = config_manager.get('schedule.interval_hours', 24)
        self.default_start_time = config_manager.get('schedule.start_time', '09:00')
    
    def _register_default_jobs(self) -> None:
        """기본 작업을 등록합니다."""
        if self.schedule_enabled:
            # 기본 일일 작업 등록
            self.add_daily_job(
                name="daily_collection",
                time=self.default_start_time,
                job_func=self._run_daily_collection,
                description="일일 데이터 수집 및 CSV 내보내기"
            )
            
            # 기본 주기적 작업 등록
            if self.default_interval_hours < 24:
                self.add_interval_job(
                    name="periodic_collection",
                    interval_hours=self.default_interval_hours,
                    job_func=self._run_periodic_collection,
                    description=f"{self.default_interval_hours}시간마다 데이터 수집"
                )
    
    def add_daily_job(self, name: str, time: str, job_func: Callable, 
                      description: str = "") -> bool:
        """
        매일 특정 시간에 실행되는 작업을 추가합니다.
        
        Args:
            name: 작업 이름
            time: 실행 시간 (HH:MM 형식)
            job_func: 실행할 함수
            description: 작업 설명
            
        Returns:
            등록 성공 여부
        """
        try:
            # 기존 작업이 있다면 제거
            if name in self.scheduled_jobs:
                self.remove_job(name)
            
            # 새 작업 등록
            job = schedule.every().day.at(time).do(self._execute_job, name, job_func, description)
            
            self.scheduled_jobs[name] = {
                'type': 'daily',
                'time': time,
                'job': job,
                'description': description,
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"일일 작업 등록 완료: {name} ({time})")
            return True
            
        except Exception as e:
            self.logger.error(f"일일 작업 등록 실패: {e}")
            return False
    
    def add_interval_job(self, name: str, interval_hours: int, job_func: Callable,
                        description: str = "") -> bool:
        """
        지정된 간격으로 실행되는 작업을 추가합니다.
        
        Args:
            name: 작업 이름
            interval_hours: 실행 간격 (시간)
            job_func: 실행할 함수
            description: 작업 설명
            
        Returns:
            등록 성공 여부
        """
        try:
            # 기존 작업이 있다면 제거
            if name in self.scheduled_jobs:
                self.remove_job(name)
            
            # 새 작업 등록
            if interval_hours >= 24:
                job = schedule.every(interval_hours // 24).days.do(
                    self._execute_job, name, job_func, description
                )
            else:
                job = schedule.every(interval_hours).hours.do(
                    self._execute_job, name, job_func, description
                )
            
            self.scheduled_jobs[name] = {
                'type': 'interval',
                'interval_hours': interval_hours,
                'job': job,
                'description': description,
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"주기 작업 등록 완료: {name} ({interval_hours}시간마다)")
            return True
            
        except Exception as e:
            self.logger.error(f"주기 작업 등록 실패: {e}")
            return False
    
    def add_custom_job(self, name: str, schedule_rule: str, job_func: Callable,
                       description: str = "") -> bool:
        """
        사용자 정의 스케줄 규칙으로 작업을 추가합니다.
        
        Args:
            name: 작업 이름
            schedule_rule: 스케줄 규칙 (예: 'every().monday.at("09:00")')
            job_func: 실행할 함수
            description: 작업 설명
            
        Returns:
            등록 성공 여부
        """
        try:
            # 기존 작업이 있다면 제거
            if name in self.scheduled_jobs:
                self.remove_job(name)
            
            # 동적으로 스케줄 규칙 생성
            # 예: schedule.every().monday.at("09:00")
            schedule_parts = schedule_rule.split('.')
            schedule_obj = schedule
            
            for part in schedule_parts:
                if hasattr(schedule_obj, part):
                    schedule_obj = getattr(schedule_obj, part)
                elif part.startswith('(') and part.endswith(')'):
                    # 함수 호출 (예: at("09:00"))
                    func_name = part[:part.find('(')]
                    args_str = part[part.find('(')+1:part.rfind(')')]
                    
                    if hasattr(schedule_obj, func_name):
                        func = getattr(schedule_obj, func_name)
                        # 간단한 인수 파싱 (문자열만 지원)
                        args = [arg.strip('"\'') for arg in args_str.split(',') if arg.strip()]
                        schedule_obj = func(*args)
                    else:
                        raise ValueError(f"알 수 없는 함수: {func_name}")
                else:
                    raise ValueError(f"알 수 없는 스케줄 속성: {part}")
            
            # 작업 등록
            job = schedule_obj.do(self._execute_job, name, job_func, description)
            
            self.scheduled_jobs[name] = {
                'type': 'custom',
                'schedule_rule': schedule_rule,
                'job': job,
                'description': description,
                'created_at': datetime.now().isoformat()
            }
            
            self.logger.info(f"사용자 정의 작업 등록 완료: {name} ({schedule_rule})")
            return True
            
        except Exception as e:
            self.logger.error(f"사용자 정의 작업 등록 실패: {e}")
            return False
    
    def remove_job(self, name: str) -> bool:
        """
        등록된 작업을 제거합니다.
        
        Args:
            name: 제거할 작업 이름
            
        Returns:
            제거 성공 여부
        """
        if name not in self.scheduled_jobs:
            self.logger.warning(f"작업 '{name}'를 찾을 수 없습니다")
            return False
        
        try:
            job_info = self.scheduled_jobs[name]
            schedule.cancel_job(job_info['job'])
            del self.scheduled_jobs[name]
            
            self.logger.info(f"작업 제거 완료: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"작업 제거 실패: {e}")
            return False
    
    def _execute_job(self, name: str, job_func: Callable, description: str) -> None:
        """
        작업을 실행하고 결과를 기록합니다.
        
        Args:
            name: 작업 이름
            job_func: 실행할 함수
            description: 작업 설명
        """
        start_time = datetime.now()
        job_result = {
            'job_name': name,
            'description': description,
            'start_time': start_time.isoformat(),
            'status': 'running'
        }
        
        try:
            self.logger.info(f"작업 실행 시작: {name}")
            
            # 작업 실행
            result = job_func()
            
            # 실행 완료
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            job_result.update({
                'status': 'completed',
                'end_time': end_time.isoformat(),
                'execution_time_seconds': execution_time,
                'result': result
            })
            
            self.logger.info(f"작업 실행 완료: {name} ({execution_time:.2f}초)")
            
        except Exception as e:
            # 실행 실패
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            job_result.update({
                'status': 'failed',
                'end_time': end_time.isoformat(),
                'execution_time_seconds': execution_time,
                'error': str(e)
            })
            
            self.logger.error(f"작업 실행 실패: {name} - {e}")
        
        # 작업 히스토리에 추가
        self.job_history.append(job_result)
        
        # 히스토리 크기 제한 (최근 100개만 유지)
        if len(self.job_history) > 100:
            self.job_history = self.job_history[-100:]
    
    def _run_daily_collection(self) -> Dict[str, Any]:
        """일일 데이터 수집 작업을 실행합니다."""
        try:
            return self.donmoa.run_full_workflow()
        except Exception as e:
            self.logger.error(f"일일 데이터 수집 실패: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _run_periodic_collection(self) -> Dict[str, Any]:
        """주기적 데이터 수집 작업을 실행합니다."""
        try:
            return self.donmoa.run_full_workflow()
        except Exception as e:
            self.logger.error(f"주기적 데이터 수집 실패: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def start(self) -> bool:
        """
        스케줄러를 시작합니다.
        
        Returns:
            시작 성공 여부
        """
        if self.is_running:
            self.logger.warning("스케줄러가 이미 실행 중입니다")
            return False
        
        try:
            self.is_running = True
            
            # 스케줄러 스레드 시작
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
            
            self.logger.info("스케줄러 시작 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"스케줄러 시작 실패: {e}")
            self.is_running = False
            return False
    
    def stop(self) -> bool:
        """
        스케줄러를 중지합니다.
        
        Returns:
            중지 성공 여부
        """
        if not self.is_running:
            self.logger.warning("스케줄러가 실행 중이 아닙니다")
            return False
        
        try:
            self.is_running = False
            
            # 스케줄러 스레드 종료 대기
            if self.scheduler_thread and self.scheduler_thread.is_alive():
                self.scheduler_thread.join(timeout=5)
            
            self.logger.info("스케줄러 중지 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"스케줄러 중지 실패: {e}")
            return False
    
    def _run_scheduler(self) -> None:
        """스케줄러 메인 루프를 실행합니다."""
        self.logger.info("스케줄러 메인 루프 시작")
        
        while self.is_running:
            try:
                # 대기 중인 작업 실행
                schedule.run_pending()
                
                # 1초 대기
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"스케줄러 실행 오류: {e}")
                time.sleep(5)  # 오류 발생 시 5초 대기
        
        self.logger.info("스케줄러 메인 루프 종료")
    
    def get_status(self) -> Dict[str, Any]:
        """
        스케줄러 상태를 반환합니다.
        
        Returns:
            스케줄러 상태 정보
        """
        status = {
            'is_running': self.is_running,
            'scheduled_jobs': {
                name: {
                    'type': info['type'],
                    'description': info['description'],
                    'created_at': info['created_at']
                }
                for name, info in self.scheduled_jobs.items()
            },
            'total_jobs': len(self.scheduled_jobs),
            'recent_jobs': self.job_history[-10:] if self.job_history else [],
            'next_run': self._get_next_run_info()
        }
        
        return status
    
    def _get_next_run_info(self) -> Dict[str, Any]:
        """다음 실행 예정 작업 정보를 반환합니다."""
        try:
            next_job = schedule.next_run()
            if next_job:
                return {
                    'next_job_time': next_job.next_run.isoformat(),
                    'next_job_name': str(next_job.job_func)
                }
        except Exception:
            pass
        
        return {'next_job_time': None, 'next_job_name': None}
    
    def run_job_now(self, name: str) -> bool:
        """
        등록된 작업을 즉시 실행합니다.
        
        Args:
            name: 실행할 작업 이름
            
        Returns:
            실행 성공 여부
        """
        if name not in self.scheduled_jobs:
            self.logger.warning(f"작업 '{name}'를 찾을 수 없습니다")
            return False
        
        try:
            job_info = self.scheduled_jobs[name]
            job_func = job_info['job'].job_func
            
            # 작업 즉시 실행
            self._execute_job(name, job_func, job_info['description'])
            
            self.logger.info(f"작업 즉시 실행 완료: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"작업 즉시 실행 실패: {e}")
            return False
    
    def save_schedule_config(self, output_path: Optional[Path] = None) -> Path:
        """
        현재 스케줄 설정을 파일로 저장합니다.
        
        Args:
            output_path: 출력 파일 경로 (None이면 자동 생성)
            
        Returns:
            저장된 파일 경로
        """
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path(f"schedule_config_{timestamp}.json")
        
        config = {
            'scheduler_status': {
                'is_running': self.is_running,
                'total_jobs': len(self.scheduled_jobs)
            },
            'scheduled_jobs': self.scheduled_jobs,
            'recent_job_history': self.job_history[-20:] if self.job_history else [],
            'exported_at': datetime.now().isoformat()
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2, default=str)
            
            self.logger.info(f"스케줄 설정 저장 완료: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"스케줄 설정 저장 실패: {e}")
            raise
