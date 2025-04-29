import pytest, os, sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import main

@pytest.fixture
def create_mock_log_files_main(tmp_path):
    """Фикстура для создания временных лог-файлов для тестов main."""
    log_content1 = (
        "2024-04-29 10:00:00,123 INFO django.requests: \"GET /api/v1/users/ HTTP/1.1\" 200 1234\n"
        "2024-04-29 10:01:00,123 DEBUG django.requests: \"POST /api/v1/users/ HTTP/1.1\" 201 50\n"
    )
    log_content2 = (
        "2024-04-29 10:03:00,123 INFO django.requests: \"GET /api/v1/auth/login/ HTTP/1.1\" 200 200\n"
    )
    
    file1 = tmp_path / "main_app1.log"
    file1.write_text(log_content1, encoding='utf-8')
    
    file2 = tmp_path / "main_app2.log"
    file2.write_text(log_content2, encoding='utf-8')
    
    return [str(file1), str(file2)]

def test_parse_arguments_success(monkeypatch, create_mock_log_files_main):
    """Тест успешного парсинга аргументов."""
    mock_files = create_mock_log_files_main
    test_args = ["main.py"] + mock_files + ["--report", "handlers"]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    log_files, report_name = main.parse_arguments()
    
    assert log_files == mock_files
    assert report_name == "handlers"

def test_parse_arguments_file_not_found(monkeypatch, tmp_path):
    """Тест ошибки парсинга, если файл не найден."""
    non_existent_file = tmp_path / "non_existent.log"
    test_args = ["main.py", str(non_existent_file), "--report", "handlers"]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    with pytest.raises(SystemExit) as excinfo:
        main.parse_arguments()
    assert excinfo.value.code == 1

def test_parse_arguments_invalid_report(monkeypatch, create_mock_log_files_main):
    """Тест ошибки парсинга с неверным именем отчета (проверяется argparse)."""
    mock_files = create_mock_log_files_main
    test_args = ["main.py"] + mock_files + ["--report", "invalid"]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    with pytest.raises(SystemExit) as excinfo:
        main.parse_arguments()
    assert excinfo.value.code == 2 

def test_main_success(monkeypatch, capsys, create_mock_log_files_main):
    """Тест успешного выполнения main."""
    mock_files = create_mock_log_files_main
    test_args = ["main.py"] + mock_files + ["--report", "handlers"]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    main.main()
    
    captured = capsys.readouterr()
    
    expected_output = (
        "Total requests: 3\n"
        "HANDLER             DEBUG   INFO    WARNING ERROR   CRITICAL\n"
        "/api/v1/auth/login/ 0       1       0       0       0       \n"
        "/api/v1/users/      1       1       0       0       0       \n"
        "                    1       2       0       0       0       "
    )
    
    assert captured.out.strip() == expected_output.strip()
    assert captured.err == ""

def test_main_generate_report_error(monkeypatch, create_mock_log_files_main):
    """Тест обработки ошибки при генерации отчета в main."""
    mock_files = create_mock_log_files_main
    test_args = ["main.py"] + mock_files + ["--report", "handlers"]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    with patch('main.generate_report', side_effect=ValueError("Test error")):
        with pytest.raises(SystemExit) as excinfo:
            main.main()
        assert excinfo.value.code == 1

def test_main_unexpected_error(monkeypatch, create_mock_log_files_main):
    """Тест обработки непредвиденной ошибки в main."""
    mock_files = create_mock_log_files_main
    test_args = ["main.py"] + mock_files + ["--report", "handlers"]
    monkeypatch.setattr(sys, 'argv', test_args)
    
    with patch('main.generate_report', side_effect=Exception("Unexpected error")):
        with pytest.raises(SystemExit) as excinfo:
            main.main()
        assert excinfo.value.code == 1

