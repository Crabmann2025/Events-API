# Unit-Tests ohne HTTP-Aufrufe oder Datenbankzugriff
from werkzeug.security import generate_password_hash, check_password_hash

def test_user_password_hashing_behaves_correctly():
    """
    Testet das Passwort-Hashing.
    """
    password = "Secret123!"
    hashed = generate_password_hash(password)

    # Das Passwort darf nicht dem Hash entsprechen
    assert hashed != password

    # Richtige Passwörter sollen validiert werden
    assert check_password_hash(hashed, password) is True

    # Falsche Passwörter sollen fehlschlagen
    assert check_password_hash(hashed, "WrongPassword") is False
