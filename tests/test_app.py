import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from app import TalentScoutDB, verify_explicit_consent, web_app


def test_verify_explicit_consent_gatekeeper():
    assert verify_explicit_consent("Rust developer #open-to-work", "Bio") is True
    assert verify_explicit_consent("Normal developer bio without markers", "None") is False


def test_db_rejects_non_consented_profile_and_supports_erasure():
    with tempfile.TemporaryDirectory() as tmpdir:
        db = TalentScoutDB(db_path=os.path.join(tmpdir, "talent.db"))
        with pytest.raises(ValueError):
            db.register_developer(
                {
                    "github_handle": "unconsented-user",
                    "display_name": "No Consent",
                    "bio": "Just coding.",
                    "skills": "python",
                    "consent_proof": "None",
                }
            )
        # Verify right-to-erasure (opt-out)
        assert db.remove_developer("deniz-rust-dev") is True
        remaining = [d["github_handle"] for d in db.list_developers()]
        assert "deniz-rust-dev" not in remaining


def test_api_endpoints():
    client = TestClient(web_app)
    resp = client.get("/api/talent?skill=python")
    assert resp.status_code == 200
    assert resp.json()["count"] >= 1
