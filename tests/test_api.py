import requests
from datetime import datetime, timedelta


# Hilfsfunktion für ein dynamisches Datum (immer morgen)
def get_future_date_str():
    """Generiert einen ISO-Zeitstempel für morgen zur gleichen Zeit."""
    return (datetime.now() + timedelta(days=1)).isoformat()


# Happy Path Tests
def test_health_endpoint_returns_healthy(base_url):
    """Prüft, ob die API erreichbar ist und 200 zurückgibt."""
    response = requests.get(f"{base_url}/")
    assert response.status_code == 200


def test_register_user_creates_new_user(base_url, unique_username):
    """Prüft, dass die Registrierung eines neuen Benutzers funktioniert."""
    response = requests.post(
        f"{base_url}/api/auth/register",
        json={
            "username": unique_username,
            "password": "Test123!"
        }
    )
    assert response.status_code == 201
    json_data = response.json()
    assert "user" in json_data
    assert json_data["user"]["username"] == unique_username


def test_login_returns_jwt_token(base_url, register_user):
    """Prüft, dass der Login ein JWT-Token zurückgibt."""
    response = requests.post(
        f"{base_url}/api/auth/login",
        json={
            "username": register_user,
            "password": "Test123!"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_create_public_event_requires_auth_and_succeeds_with_token(base_url, login_user):
    """Prüft, dass das Erstellen eines Events Authentifizierung erfordert."""
    headers = {"Authorization": f"Bearer {login_user}"}

    response = requests.post(
        f"{base_url}/api/events",
        headers=headers,
        json={
            "title": "Test Event",
            "description": "Test Desc",
            "date": get_future_date_str(),
            "location": "Test Location",
            "capacity": 10,
            "is_public": True,
            "requires_admin": False
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Event"


def test_rsvp_public_event(base_url, login_user):
    """Prüft, dass man erfolgreich RSVP zu einem öffentlichen Event senden kann."""
    headers = {"Authorization": f"Bearer {login_user}"}

    event_response = requests.post(
        f"{base_url}/api/events",
        headers=headers,
        json={
            "title": "RSVP Event",
            "description": "Test",
            "date": get_future_date_str(),
            "location": "Test",
            "capacity": 10,
            "is_public": True,
            "requires_admin": False
        }
    )
    event_id = event_response.json()["id"]

    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}",
        headers=headers,
        json={"attending": True}
    )
    assert response.status_code in (200, 201)


# Fehler-/Randfalltests
def test_duplicate_registration_returns_400(base_url, unique_username):
    """Prüft, dass die doppelte Registrierung fehlschlägt."""
    data = {"username": unique_username, "password": "Test123!"}
    requests.post(f"{base_url}/api/auth/register", json=data)
    second = requests.post(f"{base_url}/api/auth/register", json=data)
    assert second.status_code == 400


def test_create_event_without_auth_returns_401(base_url):
    """Prüft, dass Erstellen ohne Token fehlschlägt."""
    response = requests.post(
        f"{base_url}/api/events",
        json={
            "title": "Unauthorized Event",
            "date": get_future_date_str(),  # DYNAMISCH
            "location": "Test",
            "capacity": 10,
            "is_public": True
        }
    )
    assert response.status_code == 401


def test_rsvp_private_event_without_auth_fails(base_url, login_user):
    """Prüft, dass RSVP für private Events ohne Auth fehlschlägt."""
    headers = {"Authorization": f"Bearer {login_user}"}

    event_response = requests.post(
        f"{base_url}/api/events",
        headers=headers,
        json={
            "title": "Private Event",
            "date": get_future_date_str(),
            "is_public": False
        }
    )
    event_id = event_response.json()["id"]

    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}",
        json={"attending": True}
    )
    assert response.status_code == 401