import argparse, os, sys
from typing import List, Tuple, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from reporter import generate_report, get_report_by_name

SUPPORTED_REPORTS: List[str] = ["handlers"]


def parse_arguments() -> Tuple[List[str], str]:
    """
        Парсит аргументы и возвращает лог-файлы и тип отчета
    """
    parser = argparse.ArgumentParser(
        description="Анализатор лог-файлов Django для генерации отчетов."
    )
    parser.add_argument(
        "log_files",
        metavar="LOG_FILE",
        type=str,
        nargs="+",
        help="Пути к лог-файлам для анализа.",
    )
    parser.add_argument(
        "--report",
        type=str,
        default="handlers",
        choices=SUPPORTED_REPORTS,
        help=f"Тип генерируемого отчета (по дефолту: handlers). Поддерживаются: {SUPPORTED_REPORTS}",
    )

    args: argparse.Namespace = parser.parse_args()

    # проверка существования файлов
    for log_file in args.log_files:
        if not os.path.exists(log_file):
            parser.error(f"Файл не найден: {log_file}")
        if not os.path.isfile(log_file):
            parser.error(f"Путь не является файлом: {log_file}")


def main() -> None:
    """Основная функция приложения."""
    try:
        log_files: List[str]
        report_name: str
        log_files, report_name = parse_arguments()
        report_output: str = generate_report(log_files, report_name)

        print(report_output)

    except ValueError as e:
        # Обработка ошибок
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Непредвиденая ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

