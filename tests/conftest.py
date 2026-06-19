import os
import sys

from fastapi.testclient import TestClient
import pytest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app
from patchwork.services.cache_box import clear_everything


@pytest.fixture()
def client():
    clear_everything()
    with TestClient(app) as test_client:
        yield test_client
    clear_everything()
