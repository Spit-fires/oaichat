# oaichat Tests

## Running Tests

Install test dependencies:
```bash
pip install -e ".[test]"
```

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=oaichat --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_config.py
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_config.py` - Configuration management tests
- `test_database.py` - Database operation tests  
- `test_models.py` - Data model tests

## Writing Tests

Tests use temporary directories for configuration and database files to avoid interfering with your actual oaichat installation.

Use the `temp_app_dir` fixture to get a temporary application directory:

```python
def test_something(temp_app_dir, monkeypatch):
    from oaichat import config
    monkeypatch.setattr(config, "get_app_dir", lambda: temp_app_dir)
    # Your test code here
```
