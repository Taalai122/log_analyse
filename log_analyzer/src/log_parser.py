import re
from typing import Optional, Tuple

LOG_LINE_REGEX = re.compile(
    r'^\S+\s+(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+django\.requests:\s+"(?:GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+(/[^ ]*)'
)

LOG_LEVELS: set[str] = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def parse_log_line(line: str) -> Optional[Tuple[str, str]]:
    """
    Парсит одну строку лога.

    Ищет записи вида \'[TIMESTAMP] LEVEL django.requests: "METHOD /handler HTTP/..." STATUS SIZE\".
    Возвращает кортеж (log_level, handler) или None, если строка не соответствует формату.
    """
    match: Optional[re.Match[str]] = LOG_LINE_REGEX.search(line)
    if match:
        log_level: str = match.group(1)
        handler: str = match.group(2)
        # Убедимся, что извлеченный уровень логирования валиден (хотя regex уже это делает)
        if log_level in LOG_LEVELS:
            return log_level, handler
    return None

