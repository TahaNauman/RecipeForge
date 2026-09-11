from app.services.auth import hash_password, verify_password


def _register(client, username, password="password123", email=None):
    return client.post(
        "/api/auth/register",
        json={
            "username": username,
            "email": email or f"{username}@example.com",
            "password": password,
        },
    )


def test_register_success(client):
    res = _register(client, "chef_taha")
    assert res.status_code == 201
    body = res.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body["user"]["username"] == "chef_taha"
    assert "password_hash" not in body["user"]
    assert "password" not in body


def test_password_stored_hashed_and_verifies(client):
    _register(client, "hash_check")
    from app.db.base import SessionLocal
    from app.models import User

    with SessionLocal() as db:
        user = db.query(User).filter(User.username == "hash_check").one()
        assert user.password_hash != "password123"
        assert user.password_hash.startswith("$2")
        assert verify_password("password123", user.password_hash)
        assert not verify_password("wrong", user.password_hash)


def test_register_duplicate_username(client):
    _register(client, "dupe_user")
    res = _register(client, "dupe_user")
    assert res.status_code == 400
    assert "username" in res.json()["detail"]


def test_register_duplicate_email(client):
    _register(client, "dupe_email")
    res = _register(client, "other_email", email="dupe_email@example.com")
    assert res.status_code == 400
    assert "email" in res.json()["detail"]


def test_register_weak_password(client):
    res = _register(client, "weak_pw", password="short")
    assert res.status_code == 422


def test_login_by_username(client):
    _register(client, "login_user")
    res = client.post(
        "/api/auth/login", json={"username_or_email": "login_user", "password": "password123"}
    )
    assert res.status_code == 200
    assert res.json()["access_token"]


def test_login_by_email(client):
    _register(client, "login_email")
    res = client.post(
        "/api/auth/login",
        json={"username_or_email": "login_email@example.com", "password": "password123"},
    )
    assert res.status_code == 200
    assert res.json()["access_token"]


def test_login_wrong_password(client):
    _register(client, "login_wrong")
    res = client.post(
        "/api/auth/login", json={"username_or_email": "login_wrong", "password": "nope"}
    )
    assert res.status_code == 401


def test_login_unknown_user(client):
    res = client.post(
        "/api/auth/login", json={"username_or_email": "ghost", "password": "password123"}
    )
    assert res.status_code == 401


def test_me_with_token(client):
    token = _register(client, "me_user").json()["access_token"]
    res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "me_user"


def test_me_without_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_with_garbage_token(client):
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert res.status_code == 401


def test_logout_authed(client):
    token = _register(client, "out_user").json()["access_token"]
    res = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 204


def test_logout_unauthed(client):
    assert client.post("/api/auth/logout").status_code == 401


def test_public_profile(client):
    _register(client, "public_guy")
    res = client.get("/api/users/public_guy")
    assert res.status_code == 200
    assert res.json()["username"] == "public_guy"
    assert "password_hash" not in res.json()


def test_public_profile_not_found(client):
    assert client.get("/api/users/nobody_here").status_code == 404