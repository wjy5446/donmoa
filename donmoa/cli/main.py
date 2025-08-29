"""
Donmoa CLI 메인 인터페이스
"""
import click
import json
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from ..core.donmoa import Donmoa
from ..core.scheduler import DonmoaScheduler
from ..utils.config import config_manager
from ..utils.logger import setup_logger

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="donmoa")
@click.option('--config', '-c', type=click.Path(exists=True), help='설정 파일 경로')
@click.option('--verbose', '-v', is_flag=True, help='상세 로그 출력')
@click.pass_context
def cli(ctx, config, verbose):
    """
    Donmoa - 개인 자산 관리 도구
    
    여러 증권사, 은행, 암호화폐 거래소의 데이터를 한 곳으로 모아
    개인이 손쉽게 관리할 수 있도록 돕는 개인 자산 관리 도구입니다.
    """
    # 설정 파일 로드
    if config:
        config_path = Path(config)
        config_manager.config_path = config_path
        config_manager.reload()
    
    # 로깅 레벨 설정
    if verbose:
        setup_logger(level=10)  # DEBUG
    else:
        setup_logger(level=20)  # INFO
    
    # Donmoa 인스턴스 생성
    ctx.obj = Donmoa()
    
    # 컨텍스트에 설정 정보 저장
    ctx.obj.config_path = config


@cli.command()
@click.option('--provider', '-p', help='특정 Provider만 수집')
@click.option('--output-dir', '-o', type=click.Path(), help='CSV 출력 디렉토리')
@click.option('--async/--sync', default=True, help='비동기/동기 수집 (기본: 비동기)')
@click.option('--save-result', '-s', is_flag=True, help='실행 결과를 파일로 저장')
@click.pass_context
def collect(ctx, provider, output_dir, async, save_result):
    """데이터를 수집하고 CSV 파일로 내보냅니다."""
    donmoa = ctx.obj
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # 데이터 수집
            task = progress.add_task("데이터 수집 중...", total=None)
            
            if provider:
                # 특정 Provider만 수집
                if provider not in donmoa.list_providers():
                    console.print(f"[red]Provider '{provider}'를 찾을 수 없습니다[/red]")
                    return
                
                collected_data = donmoa.collect_data([provider], use_async=async)
                progress.update(task, description="CSV 내보내기 중...")
                exported_files = donmoa.export_to_csv(collected_data, output_dir)
            else:
                # 전체 워크플로우 실행
                result = donmoa.run_full_workflow(output_dir=output_dir, use_async=async)
                
                if result['status'] == 'success':
                    exported_files = result['exported_files']
                    collected_data = result.get('collected_data', {})
                else:
                    console.print(f"[red]워크플로우 실행 실패: {result.get('error_message', '알 수 없는 오류')}[/red]")
                    return
            
            progress.update(task, description="완료!")
        
        # 결과 출력
        _display_collection_results(donmoa, collected_data, exported_files)
        
        # 결과 저장
        if save_result:
            result_file = donmoa.save_workflow_result()
            console.print(f"\n[green]실행 결과가 저장되었습니다: {result_file}[/green]")
    
    except Exception as e:
        console.print(f"[red]오류 발생: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.pass_context
def status(ctx):
    """Donmoa 상태를 확인합니다."""
    donmoa = ctx.obj
    
    try:
        status_info = donmoa.get_status()
        
        # 상태 테이블 생성
        table = Table(title="Donmoa 상태")
        table.add_column("항목", style="cyan")
        table.add_column("값", style="white")
        
        table.add_row("Provider 수", str(status_info['providers']['total']))
        table.add_row("Provider 목록", ", ".join(status_info['providers']['names']) if status_info['providers']['names'] else "없음")
        table.add_row("출력 디렉토리", status_info['configuration']['output_directory'])
        table.add_row("인코딩", status_info['configuration']['encoding'])
        
        if status_info['last_run']:
            table.add_row("마지막 실행", status_info['last_run']['collection_timestamp'])
            table.add_row("수집 시간", f"{status_info['last_run']['collection_time_seconds']:.2f}초")
        
        console.print(table)
        
        # Provider 상세 정보
        if status_info['providers']['names']:
            console.print("\n[bold cyan]Provider 상세 정보:[/bold cyan]")
            for provider_name in status_info['providers']['names']:
                provider_info = donmoa.get_provider_info(provider_name)
                if provider_info:
                    provider_table = Table(title=f"Provider: {provider_name}")
                    provider_table.add_column("속성", style="cyan")
                    provider_table.add_column("값", style="white")
                    
                    for key, value in provider_info.items():
                        if key == 'endpoints':
                            value = json.dumps(value, ensure_ascii=False, indent=2)
                        provider_table.add_row(key, str(value))
                    
                    console.print(provider_table)
    
    except Exception as e:
        console.print(f"[red]상태 확인 실패: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option('--provider', '-p', required=True, help='테스트할 Provider 이름')
@click.pass_context
def test(ctx, provider):
    """Provider 연결을 테스트합니다."""
    donmoa = ctx.obj
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Provider '{provider}' 연결 테스트 중...", total=None)
            
            result = donmoa.test_provider_connection(provider)
            
            progress.update(task, description="완료!")
        
        # 테스트 결과 출력
        _display_test_results(provider, result)
    
    except Exception as e:
        console.print(f"[red]연결 테스트 실패: {e}[/red]")
        raise click.Abort()


@cli.group()
@click.pass_context
def scheduler(ctx):
    """스케줄러 관련 명령어"""
    pass


@scheduler.command()
@click.pass_context
def start(ctx):
    """스케줄러를 시작합니다."""
    donmoa = ctx.obj
    
    try:
        scheduler = DonmoaScheduler(donmoa)
        
        if scheduler.start():
            console.print("[green]스케줄러가 시작되었습니다[/green]")
            
            # 스케줄 정보 출력
            status_info = scheduler.get_status()
            _display_scheduler_status(status_info)
        else:
            console.print("[red]스케줄러 시작에 실패했습니다[/red]")
    
    except Exception as e:
        console.print(f"[red]스케줄러 시작 실패: {e}[/red]")
        raise click.Abort()


@scheduler.command()
@click.pass_context
def stop(ctx):
    """스케줄러를 중지합니다."""
    donmoa = ctx.obj
    
    try:
        scheduler = DonmoaScheduler(donmoa)
        
        if scheduler.stop():
            console.print("[green]스케줄러가 중지되었습니다[/green]")
        else:
            console.print("[red]스케줄러 중지에 실패했습니다[/red]")
    
    except Exception as e:
        console.print(f"[red]스케줄러 중지 실패: {e}[/red]")
        raise click.Abort()


@scheduler.command()
@click.pass_context
def status(ctx):
    """스케줄러 상태를 확인합니다."""
    donmoa = ctx.obj
    
    try:
        scheduler = DonmoaScheduler(donmoa)
        status_info = scheduler.get_status()
        
        _display_scheduler_status(status_info)
    
    except Exception as e:
        console.print(f"[red]스케줄러 상태 확인 실패: {e}[/red]")
        raise click.Abort()


@scheduler.command()
@click.option('--name', '-n', required=True, help='작업 이름')
@click.pass_context
def run_now(ctx, name):
    """등록된 작업을 즉시 실행합니다."""
    donmoa = ctx.obj
    
    try:
        scheduler = DonmoaScheduler(donmoa)
        
        if scheduler.run_job_now(name):
            console.print(f"[green]작업 '{name}' 즉시 실행 완료[/green]")
        else:
            console.print(f"[red]작업 '{name}' 즉시 실행 실패[/red]")
    
    except Exception as e:
        console.print(f"[red]작업 즉시 실행 실패: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option('--output-dir', '-o', type=click.Path(), help='CSV 출력 디렉토리')
@click.pass_context
def export(ctx, output_dir):
    """최근 수집된 데이터를 CSV로 내보냅니다."""
    donmoa = ctx.obj
    
    try:
        if not donmoa.last_run_result:
            console.print("[yellow]내보낼 데이터가 없습니다. 먼저 데이터를 수집해주세요.[/yellow]")
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("CSV 내보내기 중...", total=None)
            
            exported_files = donmoa.export_to_csv(output_dir=output_dir)
            
            progress.update(task, description="완료!")
        
        # 내보내기 결과 출력
        console.print(f"\n[green]CSV 내보내기 완료: {len(exported_files)}개 파일 생성[/green]")
        
        for file_type, file_path in exported_files.items():
            if file_type != 'summary':
                console.print(f"  - {file_type}: {file_path}")
    
    except Exception as e:
        console.print(f"[red]CSV 내보내기 실패: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.pass_context
def config(ctx):
    """현재 설정을 확인합니다."""
    try:
        # 설정 정보 출력
        config_info = {
            'schedule': {
                'enabled': config_manager.get('schedule.enabled'),
                'interval_hours': config_manager.get('schedule.interval_hours'),
                'start_time': config_manager.get('schedule.start_time')
            },
            'export': {
                'output_dir': config_manager.get('export.output_dir'),
                'file_format': config_manager.get('export.file_format'),
                'encoding': config_manager.get('export.encoding')
            },
            'logging': {
                'level': config_manager.get('logging.level'),
                'file': config_manager.get('logging.file'),
                'console': config_manager.get('logging.console')
            }
        }
        
        table = Table(title="Donmoa 설정")
        table.add_column("설정 그룹", style="cyan")
        table.add_column("설정 항목", style="yellow")
        table.add_column("값", style="white")
        
        for group, settings in config_info.items():
            for key, value in settings.items():
                table.add_row(group, key, str(value))
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[red]설정 확인 실패: {e}[/red]")
        raise click.Abort()


def _display_collection_results(donmoa, collected_data, exported_files):
    """데이터 수집 결과를 출력합니다."""
    # 수집 요약
    summary = donmoa.data_collector.get_collection_summary()
    
    console.print(f"\n[bold green]데이터 수집 완료![/bold green]")
    console.print(f"총 Provider: {summary['total_providers']}개")
    console.print(f"성공: {summary['successful_providers']}개")
    console.print(f"실패: {summary['failed_providers']}개")
    console.print(f"성공률: {summary['success_rate']:.1f}%")
    console.print(f"총 데이터: {summary['total_data_count']}건")
    console.print(f"평균 수집 시간: {summary['average_collection_time']:.2f}초")
    
    # CSV 파일 정보
    console.print(f"\n[bold cyan]생성된 CSV 파일:[/bold cyan]")
    for file_type, file_path in exported_files.items():
        if file_type != 'summary':
            console.print(f"  - {file_type}: {file_path}")


def _display_test_results(provider_name, result):
    """Provider 테스트 결과를 출력합니다."""
    if result['status'] == 'success':
        console.print(f"\n[bold green]Provider '{provider_name}' 연결 테스트 성공![/bold green]")
        
        table = Table(title="테스트 결과")
        table.add_column("항목", style="cyan")
        table.add_column("값", style="white")
        
        table.add_row("인증", result.get('authentication', 'N/A'))
        table.add_row("데이터 수집", result.get('data_collection', 'N/A'))
        table.add_row("발견된 데이터 타입", ", ".join(result.get('data_types_found', [])))
        table.add_row("총 레코드", str(result.get('total_records', 0)))
        table.add_row("테스트 시간", f"{result.get('test_time', 0):.2f}초")
        
        console.print(table)
    else:
        console.print(f"\n[bold red]Provider '{provider_name}' 연결 테스트 실패[/bold red]")
        console.print(f"오류: {result.get('error', '알 수 없는 오류')}")
        console.print(f"테스트 시간: {result.get('test_time', 0):.2f}초")


def _display_scheduler_status(status_info):
    """스케줄러 상태를 출력합니다."""
    console.print(f"\n[bold cyan]스케줄러 상태:[/bold cyan]")
    
    status_table = Table()
    status_table.add_column("항목", style="cyan")
    status_table.add_column("값", style="white")
    
    status_table.add_row("실행 상태", "실행 중" if status_info['is_running'] else "중지됨")
    status_table.add_row("등록된 작업", str(status_info['total_jobs']))
    
    console.print(status_table)
    
    # 등록된 작업 목록
    if status_info['scheduled_jobs']:
        console.print(f"\n[bold yellow]등록된 작업:[/bold yellow]")
        jobs_table = Table()
        jobs_table.add_column("작업명", style="cyan")
        jobs_table.add_column("타입", style="yellow")
        jobs_table.add_column("설명", style="white")
        
        for name, info in status_info['scheduled_jobs'].items():
            jobs_table.add_row(name, info['type'], info['description'])
        
        console.print(jobs_table)
    
    # 다음 실행 예정
    if status_info['next_run']['next_job_time']:
        console.print(f"\n[bold green]다음 실행 예정:[/bold green]")
        console.print(f"  시간: {status_info['next_run']['next_job_time']}")
        console.print(f"  작업: {status_info['next_run']['next_job_name']}")


if __name__ == '__main__':
    cli()
