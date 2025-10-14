"""
CLI 인터페이스
"""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
import requests
from datetime import datetime

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

    if "last_run" in status_info and status_info["last_run"]:
        table.add_row("마지막 실행", status_info["last_run"]["collection_timestamp"])

    console.print(table)


@cli.command()
@click.option('--input-dir', '-i', help='입력 파일 디렉토리')
def template(input_dir):
    """수동 입력을 위한 Excel 템플릿을 생성합니다"""
    from ..core.template_generator import TemplateGenerator

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


@cli.command()
@click.option('--export-dir', '-e', help='내보낸 CSV가 있는 디렉토리')
@click.option('--date', '-d', help='스냅샷 날짜 (YYYY-MM-DD)')
@click.option('--notes', '-n', help='스냅샷 노트')
def upload(export_dir, date, notes):
    """CSV 파일을 API로 업로드합니다"""

    # API 설정 확인
    api_url = config_manager.get("api.url")
    api_token = config_manager.get("api.token")

    if not api_url:
        console.print("[red]ERROR: API URL이 설정되지 않았습니다.[/red]")
        console.print("[yellow]config/config.yaml에 api.url을 설정하세요.[/yellow]")
        return

    if not api_token:
        console.print("[red]ERROR: API 토큰이 설정되지 않았습니다.[/red]")
        console.print("[yellow]config/config.yaml에 api.token을 설정하세요.[/yellow]")
        return

    # 날짜 확인
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
        console.print(f"[yellow]날짜가 지정되지 않아 오늘 날짜로 설정: {date}[/yellow]")

    # Export 디렉토리 확인
    if not export_dir:
        # 최근 export 디렉토리 찾기
        export_base = Path(config_manager.get("export.output_dir", "data/export"))
        if export_base.exists():
            subdirs = sorted([d for d in export_base.iterdir() if d.is_dir()], reverse=True)
            if subdirs:
                export_dir = str(subdirs[0])
                console.print(f"[yellow]최근 export 디렉토리 사용: {export_dir}[/yellow]")
            else:
                console.print("[red]ERROR: export 디렉토리를 찾을 수 없습니다.[/red]")
                return
        else:
            console.print("[red]ERROR: export 디렉토리가 존재하지 않습니다.[/red]")
            return

    export_path = Path(export_dir)
    if not export_path.exists():
        console.print(f"[red]ERROR: 디렉토리가 존재하지 않습니다: {export_dir}[/red]")
        return

    # CSV 파일 확인
    cash_file = export_path / "cash.csv"
    positions_file = export_path / "positions.csv"
    transactions_file = export_path / "transactions.csv"

    files = {}
    if cash_file.exists():
        files['cash_file'] = ('cash.csv', open(cash_file, 'rb'), 'text/csv')
    if positions_file.exists():
        files['positions_file'] = ('positions.csv', open(positions_file, 'rb'), 'text/csv')
    if transactions_file.exists():
        files['transactions_file'] = ('transactions.csv', open(transactions_file, 'rb'), 'text/csv')

    if not files:
        console.print(f"[red]ERROR: CSV 파일을 찾을 수 없습니다: {export_dir}[/red]")
        return

    console.print(f"[cyan]업로드할 파일:[/cyan]")
    for key in files.keys():
        console.print(f"  - {key.replace('_file', '')}.csv")

    # API 요청
    try:
        console.print(f"[cyan]API로 업로드 중...[/cyan]")

        data = {'snapshot_date': date}
        if notes:
            data['notes'] = notes

        headers = {
            'Authorization': f'Bearer {api_token}'
        }

        response = requests.post(
            f"{api_url}/v1/snapshots/upload",
            files=files,
            data=data,
            headers=headers,
            timeout=60
        )

        # 파일 핸들 닫기
        for _, file_tuple in files.items():
            file_tuple[1].close()

        if response.status_code == 200:
            result = response.json()
            console.print(f"[green]SUCCESS: 스냅샷 업로드 완료 (ID: {result['snapshot_id']})[/green]")
            console.print(f"  파싱된 행 수:")
            console.print(f"    - 현금: {result['parsed_rows']['cash']}")
            console.print(f"    - 포지션: {result['parsed_rows']['positions']}")
            console.print(f"    - 거래: {result['parsed_rows']['transactions']}")
            console.print(f"  생성된 라인:")
            console.print(f"    - 현금: {result['lines']['cash']}")
            console.print(f"    - 포지션: {result['lines']['positions']}")
            console.print(f"    - 거래: {result['lines']['transactions']}")

            if result.get('warnings'):
                console.print(f"[yellow]경고 ({len(result['warnings'])}개):[/yellow]")
                for warning in result['warnings'][:5]:  # 최대 5개만 표시
                    console.print(f"  - {warning}")

            if result.get('errors'):
                console.print(f"[red]에러 ({len(result['errors'])}개):[/red]")
                for error in result['errors'][:5]:  # 최대 5개만 표시
                    console.print(f"  - {error}")
        else:
            console.print(f"[red]ERROR: API 요청 실패 (HTTP {response.status_code})[/red]")
            try:
                error_data = response.json()
                console.print(f"  메시지: {error_data.get('error', {}).get('message', 'Unknown error')}")
            except:
                console.print(f"  응답: {response.text[:200]}")

    except requests.exceptions.Timeout:
        console.print("[red]ERROR: API 요청 시간 초과[/red]")
    except requests.exceptions.ConnectionError:
        console.print(f"[red]ERROR: API 서버에 연결할 수 없습니다: {api_url}[/red]")
    except Exception as e:
        console.print(f"[red]ERROR: {str(e)}[/red]")


if __name__ == '__main__':
    cli()
