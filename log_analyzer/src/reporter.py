from typing import Dict, List, Set, Tuple, Optional, Type
import os
from collections import defaultdict

# Добавим src в sys.path, чтобы можно было импортировать модули
import sys

from log_parser import parse_log_line


class Report:
    """Базовый класс для всех отчетов."""

    name: str = ""

    def __init__(self) -> None:
        """Инициализация отчета."""
        pass

    def process_log_entry(self, log_level: str, handler: str) -> None:
        """
        Обрабатывает одну запись лога.

        Args:
            log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            handler: Обработчик API (путь)
        """
        raise NotImplementedError("Метод должен быть переопределен в дочернем классе")

    def generate(self) -> str:
        """
        Генерирует отчет в виде строки.

        Returns:
            str: Отформатированный отчет
        """
        raise NotImplementedError("Метод должен быть переопределен в дочернем классе")


class HandlersReport(Report):
    """
    Отчет о состоянии ручек API по каждому уровню логирования.

    Формат отчета:
    ```
    Total requests: 1000
    HANDLER              DEBUG    INFO WARNING    ERROR    CRITICAL
    /admin/dashboard/     20       72     19       14         18
    /api/v1/auth/login/   23       78     14       15         18
    ...
                        178      494     96      116        116
    ```
    """

    name: str = "handlers"

    def __init__(self) -> None:
        """Инициализация отчета о ручках API."""
        super().__init__()
        # dictionary для хранения статистики
        self.stats: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.handlers: Set[str] = set()
        self.total_requests: int = 0

    def process_log_entry(self, log_level: str, handler: str) -> None:
        """
        Обрабатывает одну запись лога для отчета о ручках API.

        Args:
            log_level: Уровень логирования (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            handler: Обработчик API (путь)
        """
        self.stats[handler][log_level] += 1
        self.handlers.add(handler)
        self.total_requests += 1

    def generate(self) -> str:
        """
        Генерирует отчет о ручках API.

        Returns:
            str: Отформатированный отчет
        """
        sorted_handlers: List[str] = sorted(self.handlers)

        log_levels: List[str] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        level_totals: Dict[str, int] = {
            level: sum(self.stats[handler][level] for handler in self.handlers)
            for level in log_levels
        }

        result: List[str] = [f"Total requests: {self.total_requests}"]

        header: str = "HANDLER".ljust(20)
        for level in log_levels:
            header += level.ljust(8)
        result.append(header)

        for handler in sorted_handlers:
            line: str = handler.ljust(20)
            for level in log_levels:
                count: int = self.stats[handler][level]
                line += str(count).ljust(8)
            result.append(line)

        totals_line: str = " ".ljust(20)
        for level in log_levels:
            totals_line += str(level_totals[level]).ljust(8)
        result.append(totals_line)

        return "\n".join(result)


def get_report_by_name(report_name: str) -> Optional[Report]:
    """
    Возвращает экземпляр отчета по его имени.

    Args:
        report_name: Имя отчета

    Returns:
        Report: Экземпляр отчета или None, если отчет не найден
    """
    reports: Dict[str, Type[Report]] = {
        "handlers": HandlersReport,

    }

    report_class: Optional[Type[Report]] = reports.get(report_name)
    if report_class:
        return report_class()
    return None


def generate_report(log_files: List[str], report_name: str) -> str:
    """
    Генерирует отчет на основе лог-файлов.

    Args:
        log_files: Список путей к лог-файлам
        report_name: Имя отчета для генерации

    Returns:
        str: Отформатированный отчет
    """
    report: Optional[Report] = get_report_by_name(report_name)
    if not report:
        raise ValueError(f"Неизвестный тип отчета: {report_name}")

    # Обрабатываем каждый файл
    for log_file in log_files:
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    result: Optional[Tuple[str, str]] = parse_log_line(line)
                    if result:
                        log_level, handler = result
                        report.process_log_entry(log_level, handler)
        except FileNotFoundError:
            # эта проверка уже есть в main.py, но добавим для надежности
            print(f"Ошибка: Файл не найден при обработке: {log_file}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"Ошибка при чтении файла {log_file}: {e}", file=sys.stderr)
            continue

    return report.generate()

