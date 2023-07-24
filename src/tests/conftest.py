import pytest
from unittest import mock
import os


@pytest.fixture(autouse=True)
def mock_environment_variables():
    with mock.patch.dict(os.environ, {
        "RDS_HOST": "test-host",
        "RDS_USERNAME": "test-user",
        "RDS_PASSWORD": "test-pass",
        "RDS_NAME": "test-db"
    }):
        yield
