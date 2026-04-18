import hashlib
from database import get_connection

current_user = None


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def login(username, password):
    global current_user
    conn = get_connection()
    cursor = conn.cursor()
    # Compare against stored SHA-256 hash (NFR-03)
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hash_password(password)),
    )
    user = cursor.fetchone()
    conn.close()
    if user:
        current_user = dict(user)
        return True
    return False


def logout():
    global current_user
    current_user = None


def get_current_user():
    return current_user
