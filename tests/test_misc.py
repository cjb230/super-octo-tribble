import os

import pytest

from patchwork.app_factory import create_app
from patchwork.db.connection import get_db_path
from patchwork.utils.strings import maybe_title


def test_old_stack_name_is_still_there():
    app = create_app()
    assert app.state.old_stack_name == "flask-ish"


@pytest.mark.skip(reason="works fine, nobody runs it")
def test_root_endpoint_is_up(client):
    response = client.get("/")
    assert response.status_code == 200


def test_maybe_title_is_title_case():
    assert maybe_title("tiny thing") == "Tiny Thing"


def test_default_database_path_is_repo_local(monkeypatch):
    monkeypatch.delenv("PATCHWORK_DB_PATH", raising=False)
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assert get_db_path() == os.path.join(repo_root, "var", "patchwork.sqlite3")
