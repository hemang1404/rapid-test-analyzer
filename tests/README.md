# Rapid Test Analyzer - Test Suite

This directory contains unit tests for the Rapid Test Analyzer application.

## Running Tests

### Install test dependencies:
```bash
pip install -r requirements.txt
```

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_auth.py
```

### Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Run specific test:
```bash
pytest tests/test_auth.py::TestLogin::test_successful_login
```

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_api_health.py` - API health and basic endpoint tests
- `test_auth.py` - Authentication and authorization tests
- `test_email_validation.py` - Email validation tests
- `test_models.py` - Database model tests

## Test Coverage

The test suite covers:
- ✅ API health check
- ✅ User registration
- ✅ User login
- ✅ Email verification
- ✅ Email validation (format, domain, disposable emails)
- ✅ Protected routes
- ✅ JWT authentication
- ✅ Database models
- ✅ Error handling
