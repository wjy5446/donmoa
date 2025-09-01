"""
Donmoa CLI 메인 인터페이스
"""
import click
import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..core.donmoa import Donmoa

from ..utils.config import config_manager
from ..utils.logger import setup_logger

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="donmoa")
@click.option('--config', '-c', type=click.Path(exists=True), help='설정 파일 경로')
@click.option('--verbose', '-v', is_flag=True, help='상세 로그 출력')
@click.option('--deployment', '-d', is_flag=True, help='배포 환경 모드')
@click.pass_context
def cli(ctx, config, verbose, deployment):
    """
    Donmoa - 개인 자산 관리 도구

    여러 증권사, 은행, 암호화폐 거래소의 데이터를 한 곳으로 모아
    개인이 손쉽게 관리할 수 있도록 돕는 개인 자산 관리 도구입니다.
    """
    # 배포 환경 설정 적용
    if deployment:
        deployment_config = Path("config/deployment.yaml")
        if deployment_config.exists():
            config = deployment_config
            console.print("[yellow]배포 환경 모드로 실행됩니다.[/yellow]")
        else:
            console.print("[red]배포 환경 설정 파일을 찾을 수 없습니다.[/red]")
            raise click.Abort()

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
    ctx.obj.deployment_mode = deployment


@cli.command()
@click.option('--provider', '-p', help='특정 Provider만 수집')
@click.option('--output-dir', '-o', type=click.Path(), help='CSV 출력 디렉토리')
@click.option('--async/--sync', default=True, help='비동기/동기 수집 (기본: 비동기)')
@click.option('--save-result', '-s', is_flag=True, help='실행 결과를 파일로 저장')
@click.option('--validate', is_flag=True, help='데이터 유효성 검증 수행')
@click.pass_context
def collect(ctx, provider, output_dir, async_mode, save_result, validate):
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

                collected_data = donmoa.collect_data([provider], use_async=async_mode)
                progress.update(task, description="CSV 내보내기 중...")
                exported_files = donmoa.export_to_csv(collected_data, output_dir)
            else:
                # 전체 워크플로우 실행
                result = donmoa.run_full_workflow(output_dir=output_dir, use_async=async_mode)

                if result['status'] == 'success':
                    exported_files = result['exported_files']
                    collected_data = result.get('collected_data', {})
                else:
                    console.print(f"[red]워크플로우 실행 실패: {result.get('error_message', '알 수 없는 오류')}[/red]")
                    return

            # 데이터 유효성 검증
            if validate:
                progress.update(task, description="데이터 유효성 검증 중...")
                validation_result = donmoa.validate_data(collected_data)
                if not validation_result['is_valid']:
                    console.print(f"[yellow]데이터 유효성 검증 경고: {validation_result['warnings']}[/yellow]")

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


@cli.command()
@click.option('--health', is_flag=True, help='상태 확인만 수행')
@click.option('--metrics', is_flag=True, help='메트릭 수집')
@click.pass_context
def health(ctx, health, metrics):
    """시스템 상태 및 메트릭을 확인합니다."""
    donmoa = ctx.obj

    try:
        if health:
            health_status = donmoa.check_health()
            _display_health_status(health_status)
        elif metrics:
            metrics_data = donmoa.collect_metrics()
            _display_metrics(metrics_data)
        else:
            # 기본 상태 확인
            health_status = donmoa.check_health()
            _display_health_status(health_status)

    except Exception as e:
        console.print(f"[red]상태 확인 실패: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option('--backup', is_flag=True, help='백업 생성')
@click.option('--restore', type=click.Path(exists=True), help='백업에서 복원')
@click.option('--list', 'list_backups', is_flag=True, help='백업 목록 표시')
@click.pass_context
def backup(ctx, backup, restore, list_backups):
    """데이터 백업 및 복원을 관리합니다."""
    donmoa = ctx.obj

    try:
        if backup:
            backup_file = donmoa.create_backup()
            console.print(f"[green]백업 생성 완료: {backup_file}[/green]")
        elif restore:
            donmoa.restore_from_backup(restore)
            console.print(f"[green]백업에서 복원 완료: {restore}[/green]")
        elif list_backups:
            backups = donmoa.list_backups()
            _display_backup_list(backups)
        else:
            console.print("[yellow]백업 옵션을 지정해주세요. --help로 도움말을 확인하세요.[/yellow]")

    except Exception as e:
        console.print(f"[red]백업 작업 실패: {e}[/red]")
        raise click.Abort()


@cli.command()
@click.option('--clean', is_flag=True, help='오래된 데이터 정리')
@click.option('--optimize', is_flag=True, help='데이터베이스 최적화')
@click.option('--vacuum', is_flag=True, help='저장 공간 정리')
@click.pass_context
def maintenance(ctx, clean, optimize, vacuum):
    """시스템 유지보수를 수행합니다."""
    donmoa = ctx.obj

    try:
        if clean:
            result = donmoa.cleanup_old_data()
            console.print(f"[green]데이터 정리 완료: {result['cleaned_records']}개 레코드 정리[/green]")
        elif optimize:
            result = donmoa.optimize_storage()
            console.print(f"[green]저장소 최적화 완료: {result['saved_space']}MB 절약[/green]")
        elif vacuum:
            result = donmoa.vacuum_storage()
            console.print(f"[green]저장 공간 정리 완료: {result['freed_space']}MB 해제[/green]")
        else:
            console.print("[yellow]유지보수 옵션을 지정해주세요. --help로 도움말을 확인하세요.[/yellow]")

    except Exception as e:
        console.print(f"[red]유지보수 작업 실패: {e}[/red]")
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


def _display_health_status(health_status):
    """시스템 상태를 출력합니다."""
    table = Table(title="시스템 상태")
    table.add_column("항목", style="cyan")
    table.add_column("상태", style="white")
    table.add_column("세부사항", style="yellow")

    for component, status in health_status.items():
        if component == 'providers':
            # providers 컴포넌트는 특별한 구조를 가짐
            if isinstance(status, dict) and 'status' in status:
                # Provider가 없는 경우
                provider_status = status['status']
                if provider_status['healthy']:
                    status_text = "[green]정상[/green]"
                else:
                    status_text = "[red]오류[/red]"
                table.add_row(
                    component,
                    status_text,
                    provider_status.get('message', '')
                )
            else:
                # Provider가 있는 경우
                for provider_name, provider_status in status.items():
                    if provider_status['healthy']:
                        status_text = "[green]정상[/green]"
                    else:
                        status_text = "[red]오류[/red]"
                    table.add_row(
                        f"  {provider_name}",
                        status_text,
                        provider_status.get('message', '')
                    )
        else:
            # 일반 컴포넌트
            if status['healthy']:
                status_text = "[green]정상[/green]"
            else:
                status_text = "[red]오류[/red]"

            table.add_row(component, status_text, status.get('message', ''))

    console.print(table)


def _display_metrics(metrics_data):
    """시스템 메트릭을 출력합니다."""
    table = Table(title="시스템 메트릭")
    table.add_column("메트릭", style="cyan")
    table.add_column("값", style="white")
    table.add_column("단위", style="yellow")

    for metric, data in metrics_data.items():
        table.add_row(metric, str(data['value']), data.get('unit', ''))

    console.print(table)


def _display_backup_list(backups):
    """백업 목록을 출력합니다."""
    table = Table(title="백업 목록")
    table.add_column("파일명", style="cyan")
    table.add_column("크기", style="white")
    table.add_column("생성일", style="yellow")
    table.add_column("상태", style="green")

    for backup in backups:
        table.add_row(
            backup['filename'],
            f"{backup['size_mb']:.1f}MB",
            backup['created_at'],
            backup['status']
        )

    console.print(table)


if __name__ == '__main__':
    cli()
