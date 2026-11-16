import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.core import config  # noqa: E402

needs_data = pytest.mark.skipif(not config.DATA_PATH.exists(),
                                reason=f"Base original ausente em {config.DATA_PATH}")


@pytest.fixture(scope="session")
def engine():
    from app.services.engine import Engine
    return Engine()


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c
