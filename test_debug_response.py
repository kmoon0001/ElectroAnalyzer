#!/usr/bin/env python
"""Debug script to check the API response for invalid strictness."""
import sys
import os
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from datetime import UTC, datetime
from unittest.mock import patch, MagicMock
import types

# Mock modules before importing app
sys.modules["transformers"] = types.ModuleType("transformers")
sys.modules["transformers"].pipeline = MagicMock()
sys.modules["transformers"].AutoModelForTokenClassification = MagicMock()
sys.modules["transformers"].AutoTokenizer = MagicMock()
sys.modules["transformers.configuration_utils"] = types.ModuleType("transformers.configuration_utils")
sys.modules["transformers.configuration_utils"].PretrainedConfig = MagicMock()
sys.modules["transformers.utils"] = types.ModuleType("transformers.utils")
sys.modules["transformers"].utils = sys.modules["transformers.utils"]
sys.modules["transformers.utils"].logging = MagicMock()

MOCK_MODULES = {
    "src.core.nlg_service": MagicMock(),
    "src.core.risk_scoring_service": MagicMock(),
    "src.core.preprocessing_service": MagicMock(),
    "ctransformers": MagicMock(),
    "sentence_transformers": MagicMock(),
}
sys.modules.update(MOCK_MODULES)

from fastapi.testclient import TestClient
from src.api.main import app, limiter
from src.auth import get_current_active_user
from src.database import schemas

# Disable rate limiting
limiter.enabled = False

# Create dummy user
dummy_user = schemas.User(
    id=1,
    username="testuser",
    is_active=True,
    is_admin=False,
    created_at=datetime.now(UTC),
)

def override_get_current_active_user():
    return dummy_user

app.dependency_overrides[get_current_active_user] = override_get_current_active_user

client = TestClient(app)

# Test invalid strictness
with tempfile.TemporaryDirectory() as tmp_dir:
    file_path = Path(tmp_dir) / "invalid.txt"
    file_path.write_text("bad strictness")

    with file_path.open("rb") as f:
        response = client.post(
            "/analysis/analyze",
            files={"file": (file_path.name, f, "text/plain")},
            data={
                "discipline": "pt",
                "analysis_mode": "rubric",
                "strictness": "ultra",
            },
        )

    print(f"Status code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Response text: {response.text}")
    try:
        payload = response.json()
        print(f"JSON payload: {payload}")
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
