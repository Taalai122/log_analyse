import pytest, os, sys
from src.reporter import HandlersReport, get_report_by_name, generate_report

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def sample_log_data():
    """Фикстура с примерами данных для отчета."""
    return [
        ("INFO", "/api/v1/users/"),
        ("DEBUG", "/api/v1/users/"),
        ("INFO", "/api/v1/auth/login/"),
        ("WARNING", "/api/v1/users/"),
        ("INFO", "/api/v1/users/"),
        ("ERROR", "/api/v1/auth/login/"),
        ("CRITICAL", "/admin/dashboard/"),
    ]

def test_handlers_report_init():
    """Тест инициализации HandlersReport."""
    report = HandlersReport()
    assert report.name == "handlers"
    assert report.total_requests == 0
    assert len(report.stats) == 0
    assert len(report.handlers) == 0

def test_handlers_report_process_log_entry(sample_log_data):
    """Тест обработки записей лога в HandlersReport."""
    report = HandlersReport()
    for level, handler in sample_log_data:
        report.process_log_entry(level, handler)
    
    assert report.total_requests == 7
    assert len(report.handlers) == 3
    assert "/api/v1/users/" in report.handlers
    assert "/api/v1/auth/login/" in report.handlers
    assert "/admin/dashboard/" in report.handlers
    
    assert report.stats["/api/v1/users/"]["INFO"] == 2
    assert report.stats["/api/v1/users/"]["DEBUG"] == 1
    assert report.stats["/api/v1/users/"]["WARNING"] == 1
    assert report.stats["/api/v1/auth/login/"]["INFO"] == 1
    assert report.stats["/api/v1/auth/login/"]["ERROR"] == 1
    assert report.stats["/admin/dashboard/"]["CRITICAL"] == 1
    # Проверка отсутствующих ключей
    assert report.stats["/api/v1/users/"]["ERROR"] == 0 

def test_handlers_report_generate(sample_log_data):
    """Тест генерации отчета HandlersReport."""
    report = HandlersReport()
    for level, handler in sample_log_data:
        report.process_log_entry(level, handler)
        
    generated_report = report.generate()
    
    expected_report = (
        "Total requests: 7\n"
        "HANDLER             DEBUG   INFO    WARNING ERROR   CRITICAL\n"
        "/admin/dashboard/   0       0       0       0       1       \n"
        "/api/v1/auth/login/ 0       1       0       1       0       \n"
        "/api/v1/users/      1       2       1       0       0       \n"
        "                    1       3       1       1       1       "
    )
    
    # Сравнение строк с учетом возможных пробелов в конце
    assert generated_report.strip() == expected_report.strip()

def test_get_report_by_name():
    """Тест получения экземпляра отчета по имени."""
    report = get_report_by_name("handlers")
    assert isinstance(report, HandlersReport)
    
    report_none = get_report_by_name("invalid_report")
    assert report_none is None

@pytest.fixture
def create_mock_log_files(tmp_path):
    """Фикстура для создания временных лог-файлов."""
    log_content1 = (
        "2024-04-29 10:00:00,123 INFO django.requests: \"GET /api/v1/users/ HTTP/1.1\" 200 1234\n"
        "2024-04-29 10:01:00,123 DEBUG django.requests: \"POST /api/v1/users/ HTTP/1.1\" 201 50\n"
        "Invalid log line\n"
        "2024-04-29 10:02:00,123 WARNING django.requests: \"GET /api/v1/users/ HTTP/1.1\" 500 100\n"
    )
    log_content2 = (
        "2024-04-29 10:03:00,123 INFO django.requests: \"GET /api/v1/auth/login/ HTTP/1.1\" 200 200\n"
        "2024-04-29 10:04:00,123 ERROR django.requests: \"POST /api/v1/auth/login/ HTTP/1.1\" 401 30\n"
        "2024-04-29 10:05:00,123 CRITICAL django.requests: \"GET /admin/dashboard/ HTTP/1.1\" 503 0\n"
        "2024-04-29 10:06:00,123 INFO django.requests: \"GET /api/v1/users/ HTTP/1.1\" 200 1234\n"
    )
    
    file1 = tmp_path / "app1.log"
    file1.write_text(log_content1, encoding='utf-8') 
    
    file2 = tmp_path / "app2.log"
    file2.write_text(log_content2, encoding='utf-8') 
    
    return [str(file1), str(file2)]

def test_generate_report_integration(create_mock_log_files):
    """Интеграционный тест функции generate_report."""
    log_files = create_mock_log_files
    report_name = "handlers"
    
    generated_report = generate_report(log_files, report_name)
    
    expected_report = (
        "Total requests: 7\n"
        "HANDLER             DEBUG   INFO    WARNING ERROR   CRITICAL\n"
        "/admin/dashboard/   0       0       0       0       1       \n"
        "/api/v1/auth/login/ 0       1       0       1       0       \n"
        "/api/v1/users/      1       2       1       0       0       \n"
        "                    1       3       1       1       1       "
    )
    
    assert generated_report.strip() == expected_report.strip()

def test_generate_report_invalid_report_name(create_mock_log_files):
    """Тест generate_report с неверным именем отчета."""
    log_files = create_mock_log_files
    report_name = "invalid_report"
    
    with pytest.raises(ValueError, match="Неизвестный тип отчета: invalid_report"):
        generate_report(log_files, report_name)

