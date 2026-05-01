import os
import sys
import time
import threading

import httpx
import pytest
import uvicorn

_BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, _BACKEND_PATH)

from main import app  # noqa: E402

_BASE_URL = "http://127.0.0.1:8000"


@pytest.fixture(scope="session")
def backend_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8000, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(30):
        try:
            httpx.get(f"{_BASE_URL}/docs", timeout=1)
            break
        except Exception:
            time.sleep(0.3)
    yield _BASE_URL
    server.should_exit = True


@pytest.fixture
def api_client(backend_server):
    with httpx.Client(base_url=backend_server) as client:
        yield client


@pytest.fixture
def frontend_url(backend_server):
    return f"{backend_server}/"
