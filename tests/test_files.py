from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch, AsyncMock
import uuid
import io
from app.database import SessionLocal
from app import models
client = TestClient(app)

def get_token():
    email = f"test_{uuid.uuid4().hex[:8]}@gmail.com"
    username = f"user_{uuid.uuid4().hex[:8]}"
    with patch("app.routers.users.send_verification_email", new=AsyncMock()):
        client.post("/users/register", json={"email": email, "username": username, "password": "testpass123"})
    res = client.post("/users/login", data={"username": username, "password": "testpass123"})
    return res.json()["access_token"]

def test_upload_unverified():
    token = get_token()
    files = {"file": ("test.txt", io.BytesIO(b"hello"), "text/plain")}
    response = client.post("/files/upload", 
     headers={"Authorization": f"Bearer {token}"},
     files=files)
    assert response.status_code == 403
    assert response.json()["detail"] == "User not verified !"
def get_verified_token():
    email = f"test_{uuid.uuid4().hex[:8]}@gmail.com"
    username = f"user_{uuid.uuid4().hex[:8]}"
    with patch("app.routers.users.send_verification_email", new=AsyncMock()):
        client.post("/users/register", json={"email": email, "username": username, "password": "testpass123"})

    # bypass email — set verified directly in DB
    db = SessionLocal()
    user = db.query(models.User).filter(models.User.username == username).first()
    user.is_verified = True
    db.commit()
    db.close()
    
    res = client.post("/users/login", data={"username": username, "password": "testpass123"})
    return res.json()["access_token"]
def test_delete_not_owner():
    token1 = get_verified_token()  # user 1
    token2 = get_verified_token()  # user 2
    fname = f"test_{uuid.uuid4().hex[:8]}.txt"
    files = {"file": (fname, io.BytesIO(b"hello"), "text/plain")}
    upload_response = client.post("/files/upload", 
     headers={"Authorization": f"Bearer {token1}"},
     files=files)
    file_id = upload_response.json()["id"]
    response = client.delete(f"/files/{file_id}", 
    headers={"Authorization": f"Bearer {token2}"}
     )
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied !"