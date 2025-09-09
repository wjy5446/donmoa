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
        console.print(f"[green]SUCCESS: {result['total_records']}개 레코드 처리[/green]")
        for file_type, file_path in result['exported_files'].items():
            console.print(f"  {file_type}: {file_path}")
    else:
        console.print(f"[red]ERROR: {result['message']}[/red]")


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


@cli.command()
@click.option('--input-dir', '-i', help='입력 파일 디렉토리')
def template(input_dir):
    """수동 입력을 위한 Excel 템플릿을 생성합니다"""
    from ..core.template_generator import TemplateGenerator
    from datetime import datetime

    # 설정에서 기본값 가져오기
    if not input_dir:
        input_dir = config_manager.get("input_dir", "data/input")

    # 날짜 입력 받기
    while True:
        try:
            date_input = console.input("[cyan]날짜를 입력하세요 (YYYY-MM-DD 형식, 엔터시 오늘 날짜): [/cyan]")
            if not date_input.strip():
                # 엔터만 치면 오늘 날짜로 설정
                date = datetime.now().strftime("%Y-%m-%d")
                console.print(f"[yellow]오늘 날짜로 설정: {date}[/yellow]")
                break

            # 날짜 형식 검증
            datetime.strptime(date_input.strip(), "%Y-%m-%d")
            date = date_input.strip()
            break
        except ValueError:
            console.print("[red]올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식으로 입력해주세요.[/red]")
        except KeyboardInterrupt:
            console.print("\n[yellow]작업이 취소되었습니다.[/yellow]")
            return

    template_generator = TemplateGenerator()
    result = template_generator.create_template(date, input_dir)

    if result['status'] == 'success':
        console.print(f"[green]SUCCESS: 템플릿 생성 완료: {result['file_path']}[/green]")
        console.print(f"  - Position 시트: {result['sheets']['position']}개 컬럼")
        console.print(f"  - Cash 시트: {result['sheets']['cash']}개 컬럼")
        console.print(f"  - Transaction 시트: {result['sheets']['transaction']}개 컬럼")
    else:
        console.print(f"[red]ERROR: 템플릿 생성 실패: {result['message']}[/red]")


if __name__ == '__main__':
    cli()
