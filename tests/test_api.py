import requests


# Happy Path Tests
def test_health_endpoint_returns_healthy(base_url):
    """
    Prüft, ob die API erreichbar ist und 200 zurückgibt.
    """
    response = requests.get(f"{base_url}/")
    assert response.status_code == 200

def test_register_user_creates_new_user(base_url, unique_username):
    """
    Prüft, dass die Registrierung eines neuen Benutzers funktioniert.
    """
    response = requests.post(
        f"{base_url}/api/auth/register",
        json={
            "username": unique_username,
            "password": "Test123!"
        }
    )

    # Statuscode prüfen
    assert response.status_code == 201

    # JSON-Daten prüfen
    json_data = response.json()
    assert "user" in json_data, "Antwort enthält kein 'user'-Feld"
    assert json_data["user"]["username"] == unique_username

def test_login_returns_jwt_token(base_url, register_user):
    """
    Prüft, dass der Login ein JWT-Token zurückgibt.
    """
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
    """
    Prüft, dass das Erstellen eines Events Authentifizierung erfordert
    und mit gültigem JWT-Token erfolgreich ist.
    """
    headers = {"Authorization": f"Bearer {login_user}"}

    response = requests.post(
        f"{base_url}/api/events",
        headers=headers,
        json={
            "title": "Test Event",
            "description": "Test Desc",
            "date": "2026-01-15T18:00:00",
            "location": "Test Location",
            "capacity": 10,
            "is_public": True,
            "requires_admin": False
        }
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Event"

def test_rsvp_public_event(base_url, login_user):
    """
    Prüft, dass man erfolgreich RSVP zu einem öffentlichen Event senden kann.
    """
    headers = {"Authorization": f"Bearer {login_user}"}

    # Event erstellen
    event_response = requests.post(
        f"{base_url}/api/events",
        headers=headers,
        json={
            "title": "RSVP Event",
            "description": "Test",
            "date": "2026-01-15T18:00:00",
            "location": "Test",
            "capacity": 10,
            "is_public": True,
            "requires_admin": False
        }
    )
    event_id = event_response.json()["id"]

    # RSVP senden
    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}",
        headers=headers,
        json={"attending": True}
    )
    assert response.status_code in (200, 201)


# Fehler-/Randfalltests
def test_duplicate_registration_returns_400(base_url, unique_username):
    """
    Prüft, dass die doppelte Registrierung eines Benutzernamens fehlschlägt.
    """
    data = {
        "username": unique_username,
        "password": "Test123!"
    }
    first = requests.post(f"{base_url}/api/auth/register", json=data)
    second = requests.post(f"{base_url}/api/auth/register", json=data)

    assert first.status_code == 201
    assert second.status_code == 400

def test_create_event_without_auth_returns_401(base_url):
    """
    Prüft, dass das Erstellen eines Events ohne JWT-Token fehlschlägt.
    """
    response = requests.post(
        f"{base_url}/api/events",
        json={
            "title": "Unauthorized Event",
            "description": "Test",
            "date": "2026-01-15T18:00:00",
            "location": "Test",
            "capacity": 10,
            "is_public": True,
            "requires_admin": False
        }
    )
    assert response.status_code == 401

def test_rsvp_private_event_without_auth_fails(base_url, login_user):
    """
    Prüft, dass das RSVP für ein privates Event ohne Authentifizierung fehlschlägt.
    """
    headers = {"Authorization": f"Bearer {login_user}"}

    # Privates Event erstellen
    event_response = requests.post(
        f"{base_url}/api/events",
        headers=headers,
        json={
            "title": "Private Event",
            "description": "Test",
            "date": "2026-01-15T18:00:00",
            "location": "Test",
            "capacity": 10,
            "is_public": False,
            "requires_admin": False
        }
    )
    event_id = event_response.json()["id"]

    # RSVP ohne Token versuchen
    response = requests.post(
        f"{base_url}/api/rsvps/event/{event_id}",
        json={"attending": True}
    )
    assert response.status_code == 401
