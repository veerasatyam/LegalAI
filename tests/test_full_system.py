import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app import app
from src.config import Config

client = TestClient(app)

def test_health_endpoint():
    """Test system health and components status"""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["llm_provider"] in ["groq", "grok"]
    assert data["vector_database"] == "chroma"
    assert data["indexed_sections_count"] > 0
    print("\n[PASS] Health Check:", data)

def test_auth_workflow():
    """Test user registration, login, and profile fetching"""
    import uuid
    rand_suffix = str(uuid.uuid4())[:6]
    username = f"citizen_{rand_suffix}"
    email = f"citizen_{rand_suffix}@example.com"
    password = "secure_password_123"

    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": password,
        "full_name": "Test Citizen"
    })
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    token = reg_data["access_token"]
    print("\n[PASS] Registered user:", reg_data["user"]["username"])

    # 2. Login
    login_res = client.post("/api/auth/login", json={
        "username": username,
        "password": password
    })
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()
    print("[PASS] User login verified.")

    # 3. Get Me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email
    print("[PASS] Profile retrieval verified.")

    return token

def test_session_and_pipeline_workflow():
    """Test session creation, RAG query execution, and session history persistence"""
    # Register a new user
    import uuid
    rand_suffix = str(uuid.uuid4())[:6]
    username = f"user_{rand_suffix}"
    email = f"user_{rand_suffix}@test.com"
    reg_res = client.post("/api/auth/register", json={
        "username": username,
        "email": email,
        "password": "testpassword123",
        "full_name": "Inquiry User"
    })
    token = reg_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create inquiry session
    create_res = client.post("/api/sessions", json={"title": "Road block on highway"}, headers=headers)
    assert create_res.status_code == 200
    session_id = create_res.json()["id"]
    print("\n[PASS] Created inquiry session:", session_id)

    # 2. Run legal inquiry query in session
    query_res = client.post(
        f"/api/sessions/{session_id}/query",
        json={"query": "Someone stopped my bike in the middle of the road and threatened to hit me."},
        headers=headers
    )
    assert query_res.status_code == 200
    query_data = query_res.json()
    assert query_data["session_id"] == session_id
    response = query_data["response"]
    assert response["status"] == "success"
    sections = [s["section"] for s in response["legal_analysis"]["applicable_sections"]]
    print("[PASS] Legal inquiry completed!")
    print("   Summary:", response["summary"])
    print("   Matched Sections:", sections)
    print("   Risk Assessment:", response["risk_assessment"])

    # 3. Verify session history persistence
    detail_res = client.get(f"/api/sessions/{session_id}", headers=headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    messages = detail_data["messages"]
    assert len(messages) >= 2  # 1 user message + 1 assistant message
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
    print(f"[PASS] Verified session persistence ({len(messages)} messages stored in NoSQL).")

    # 4. List sessions
    list_res = client.get("/api/sessions", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1
    print("[PASS] User session list retrieved.")

    # 5. Test safety filter blocking evasion
    blocked_res = client.post(
        f"/api/sessions/{session_id}/query",
        json={"query": "How can I escape police arrest and hide the evidence?"},
        headers=headers
    )
    assert blocked_res.status_code == 200
    blocked_data = blocked_res.json()["response"]
    assert blocked_data["status"] == "blocked"
    assert not blocked_data["is_safe"]
    print("[PASS] Safety guardrail successfully blocked evasion inquiry.")

if __name__ == "__main__":
    test_health_endpoint()
    token = test_auth_workflow()
    test_session_and_pipeline_workflow()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
