import pytest
from src.log_parser import parse_log_line

def test_parse_log_line_valid():
    """Тест парсинга валидной строки лога."""

    log_line = '2024-04-29 10:00:00,123 INFO django.requests: "GET /api/v1/users/ HTTP/1.1" 200 1234'
    result = parse_log_line(log_line)
    assert result is not None
    assert result[0] == "INFO"
    assert result[1] == "/api/v1/users/"

def test_parse_log_line_invalid_format():
    """Тест парсинга строки с неверным форматом."""

    log_line = 'Invalid log line format'
    result = parse_log_line(log_line)
    assert result is None

def test_parse_log_line_not_django_request():
    """Тест парсинга строки, не относящейся к django.requests."""

    log_line = '2024-04-29 10:00:00,123 INFO django.db: Database query executed in 0.5s'
    result = parse_log_line(log_line)
    assert result is None

def test_parse_log_line_different_log_levels():
    """Тест парсинга строк с разными уровнями логирования."""
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    for level in log_levels:
        log_line = f'2024-04-29 10:00:00,123 {level} django.requests: "GET /api/v1/users/ HTTP/1.1" 200 1234'
        result = parse_log_line(log_line)
        assert result is not None
        assert result[0] == level
        assert result[1] == "/api/v1/users/"

def test_parse_log_line_different_handlers():
    """Тест парсинга строк с разными обработчиками."""

    handlers = [
        "/api/v1/users/",
        "/api/v1/auth/login/",
        "/admin/dashboard/",
        "/api/v1/products/123",
        "/"
    ]
    
    for handler in handlers:
        log_line = f'2024-04-29 10:00:00,123 INFO django.requests: "GET {handler} HTTP/1.1" 200 1234'
        result = parse_log_line(log_line)
        assert result is not None
        assert result[0] == "INFO"
        assert result[1] == handler

def test_parse_log_line_different_methods():
    """Тест парсинга строк с разными HTTP методами."""

    methods = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]
    
    for method in methods:
        log_line = f'2024-04-29 10:00:00,123 INFO django.requests: "{method} /api/v1/users/ HTTP/1.1" 200 1234'
        result = parse_log_line(log_line)
        assert result is not None
        assert result[0] == "INFO"
        assert result[1] == "/api/v1/users/"

def test_parse_log_line_iso_timestamp():
    """Тест парсинга строк с ISO форматом времени."""
    
    log_line = '2024-04-29T10:00:00.123Z INFO django.requests: "GET /api/v1/users/ HTTP/1.1" 200 1234'
    result = parse_log_line(log_line)
    assert result is not None
    assert result[0] == "INFO"
    assert result[1] == "/api/v1/users/"
