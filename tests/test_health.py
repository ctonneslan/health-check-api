import pytest
import sys
import os
from unittest import mock

# Add the project root to sys.path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import check_database, check_disk_usage, check_external_api

# Use pytest-asyncio for async tests
pytest_plugins = ("pytest_asyncio",)

@mock.patch("app.main.simulate_db_connection")
def test_check_database_success(mock_sim):
    mock_sim.return_value = True
    assert check_database() == "ok"

@mock.patch("app.main.simulate_db_connection")
def test_check_database_failure(mock_sim):
    mock_sim.return_value = False
    assert check_database() == "fail"

@mock.patch("app.main.simulate_db_connection")
def test_check_database_exception(mock_sim):
    mock_sim.side_effect = Exception("Simulated error")
    assert check_database() == "fail"

@mock.patch("shutil.disk_usage")
def test_check_disk_usage_ok(mock_usage):
    # Simulate 50% usage
    mock_usage.return_value = (100, 50, 50)
    assert check_disk_usage() == "ok"

@mock.patch("shutil.disk_usage")
def test_check_disk_usage_warn(mock_usage):
    # Simulate 75% usage
    mock_usage.return_value = (100, 75, 25)
    os.environ["DISK_WARN_THRESHOLD"] = "70"
    os.environ["DISK_FAIL_THRESHOLD"] = "90"
    assert check_disk_usage() == "warn"

@mock.patch("shutil.disk_usage")
def test_check_disk_usage_fail(mock_usage):
    # Simulate 95% usage
    mock_usage.return_value = (100, 95, 5)
    os.environ["DISK_WARN_THRESHOLD"] = "70"
    os.environ["DISK_FAIL_THRESHOLD"] = "90"
    assert check_disk_usage() == "fail"

@pytest.mark.asyncio
@mock.patch("httpx.AsyncClient.get")
async def test_check_external_api_ok(mock_get):
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = await check_external_api()
    assert result == "ok"

@pytest.mark.asyncio
@mock.patch("httpx.AsyncClient.get")
async def test_check_external_api_fail(mock_get):
    mock_response = mock.Mock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = await check_external_api()
    assert result == "fail"