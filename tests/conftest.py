import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

@pytest.fixture
def base_url():
    return BASE_URL

@pytest.fixture
def unique_username():
    """
    Erzeugt einen garantiert eindeutigen Benutzernamen mittels UUID.
    """
    # generiert eine zufällige ID, wir nehmen nur die ersten 8 Zeichen
    return f"user_{uuid.uuid4().hex[:8]}"

@pytest.fixture
def register_user(base_url, unique_username):
    response = requests.post(
        f"{base_url}/api/auth/register",
        json={
            "username": unique_username,
            "password": "Test123!"
        }
    )
    assert response.status_code == 201
    return unique_username

@pytest.fixture
def login_user(base_url, register_user):
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": register_user,
            "password": "Test123!"
        }
    )
    assert response.status_code == 200
    return response.json().get("access_token")