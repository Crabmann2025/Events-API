import pytest
import requests
import time


BASE_URL = "http://localhost:5000"

@pytest.fixture
def base_url():
    """
    Gibt die Basis-URL der API zurück.
    """
    return BASE_URL

@pytest.fixture
def unique_username():
    """
    Erzeugt einen eindeutigen Benutzernamen mit Zeitstempel,
    """
    return f"user_{int(time.time())}"

@pytest.fixture
def register_user(base_url, unique_username):
    """
    Registriert einen neuen Benutzer und gibt den Benutzernamen zurück.
    """
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
    """
    Meldet den registrierten Benutzer an und gibt das JWT-Token zurück.
    """
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": register_user,
            "password": "Test123!"
        }
    )
    assert response.status_code == 200
    return response.json().get("access_token")
