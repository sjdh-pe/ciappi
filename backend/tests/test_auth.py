from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_credenciais_invalidas():
    response = client.post("/auth/login", json={"nome": "Invalido", "senha": "errada"})
    assert response.status_code == 401


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["sistema"] == "CIAPPI"
