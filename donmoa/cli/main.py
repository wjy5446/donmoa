"""
CLI 인터페이스
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from ..core.donmoa import Donmoa
from ..utils.config import config_manager

console = Console()


@click.group()
@click.option('--config', '-c', help='설정 파일 경로')
def cli(config):
    """Donmoa - 간소화된 개인 자산 관리 도구"""
    if config:
        config_manager.config_path = Path(config)
        config_manager.reload()


@cli.command()
@click.option('--input-dir', '-i', help='입력 파일 디렉토리')
@click.option('--output-dir', '-o', help='출력 디렉토리')
def collect(input_dir, output_dir):
    """데이터를 수집하고 CSV로 내보냅니다"""
    donmoa = Donmoa()

    # 설정에서 기본값 가져오기
    if not input_dir:
        input_dir = config_manager.get("input_dir", "data/input")
    if not output_dir:
        output_dir = config_manager.get("export.output_dir", "data/export")

    # 워크플로우 실행
    result = donmoa.run_full_workflow(input_dir, Path(output_dir) if output_dir else None)

    if result['status'] == 'success':
        console.print(f"[green]✅ 성공: {result['total_records']}개 레코드 처리[/green]")
        for file_type, file_path in result['exported_files'].items():
            console.print(f"  {file_type}: {file_path}")
    else:
        console.print(f"[red]❌ 실패: {result['message']}[/red]")


@cli.command()
@click.option('--input-dir', '-i', help='입력 파일 디렉토리')
def status(input_dir):
    """현재 상태를 확인합니다"""
    donmoa = Donmoa()

    # 설정에서 기본값 가져오기
    if not input_dir:
        input_dir = config_manager.get("input_dir", "data/input")

    status_info = donmoa.get_status()

    # 상태 테이블 생성
    table = Table(title="Donmoa 상태")
    table.add_column("항목", style="cyan")
    table.add_column("값", style="white")

    table.add_row("Provider 수", str(status_info["providers"]["total"]))
    table.add_row("Provider 목록", ", ".join(status_info["providers"]["names"]))
    table.add_row("입력 디렉토리", input_dir)
    table.add_row("출력 디렉토리", status_info["configuration"]["output_directory"])

    if status_info["last_run"]:
        table.add_row("마지막 실행", status_info["last_run"]["collection_timestamp"])

    console.print(table)


if __name__ == '__main__':
    cli()
