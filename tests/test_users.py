from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

# unique username/email mỗi lần chạy test
TEST_EMAIL = f"test_{uuid.uuid4().hex[:8]}@gmail.com"
TEST_USERNAME = f"user_{uuid.uuid4().hex[:8]}"
TEST_PASSWORD = "testpass123"

def test_register():
    response = client.post("/users/register", json={"email":TEST_EMAIL,"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    response.json()["email"] == TEST_EMAIL
    
def test_register_duplicate():
    response = client.post("/users/register", json={"email":TEST_EMAIL,"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 400  # or 500
    
def test_login():
    response = client.post("/users/login", data={"username":TEST_USERNAME, "password": TEST_PASSWORD})
    assert response.status_code == 200
    assert "access_token" in response.json()
    
def test_login_wrong_password():
    response = client.post("/users/login", data={"username":TEST_USERNAME, "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    
def test_login_not_found():
    response = client.post("/users/login", data={"username":"AdminTester", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"