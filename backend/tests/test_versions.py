import pytest
import sqlalchemy.exc
from sqlalchemy import text

from app.db.base import engine


def _register(client, username, password="password123"):
    res = client.post(
        "/api/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    assert res.status_code == 201
    return res.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _payload(**overrides):
    data = {
        "title": "Chicken Karahi",
        "description": "Spicy tomato-based chicken curry",
        "cuisine": "Pakistani",
        "difficulty": "medium",
        "prep_time": 15,
        "cook_time": 40,
        "servings": 4,
        "ingredients": [
            {"name": "chicken", "quantity": 1, "unit": "kg"},
            {"name": "tomatoes", "quantity": 4, "unit": "pieces"},
        ],
        "instructions": [{"text": "Brown the chicken"}, {"text": "Add tomatoes and simmer"}],
    }
    data.update(overrides)
    return data


def _create(client, token, **overrides):
    return client.post("/api/recipes", json=_payload(**overrides), headers=_auth(token))


def test_edit_creates_version_chain(client):
    token = _register(client, "ivy")
    recipe_id = _create(client, token).json()["id"]
    v1 = _create_revision(client, token, recipe_id, {"title": "Beef Karahi", "ingredients": [{"name": "beef", "quantity": 0.5, "unit": "kg"}]})
    assert v1["version_number"] == "1.1"
    assert v1["parent_version_id"] is not None
    v2 = _create_revision(client, token, recipe_id, {"servings": 6})
    assert v2["version_number"] == "1.2"
    assert v2["parent_version_id"] == v1["id"]
    detail = client.get(f"/api/recipes/{recipe_id}", headers=_auth(token)).json()
    assert detail["version"]["version_number"] == "1.2"


def _create_revision(client, token, recipe_id, patches):
    res = client.put(f"/api/recipes/{recipe_id}", json=patches, headers=_auth(token))
    assert res.status_code == 200
    return res.json()["version"]


def test_historical_snapshot_preserved(client):
    token = _register(client, "jade")
    created = _create(client, token).json()
    recipe_id = created["id"]
    v1_id = created["version"]["id"]
    _create_revision(client, token, recipe_id, {"ingredients": [{"name": "beef", "quantity": 1, "unit": "kg"}]})
    res = client.get(f"/api/recipes/{recipe_id}/versions/{v1_id}", headers=_auth(token))
    assert res.status_code == 200
    body = res.json()
    assert body["version_number"] == "1.0"
    assert [i["name"] for i in body["ingredients"]] == ["chicken", "tomatoes"]
    assert body["id"] == v1_id


def test_versions_list_newest_first(client):
    token = _register(client, "kelly")
    recipe_id = _create(client, token).json()["id"]
    _create_revision(client, token, recipe_id, {"title": "Renamed", "change_description": "rename"})
    _create_revision(client, token, recipe_id, {"servings": 6})
    res = client.get(f"/api/recipes/{recipe_id}/versions", headers=_auth(token))
    assert res.status_code == 200
    versions = res.json()
    assert [v["version_number"] for v in versions] == ["1.2", "1.1", "1.0"]
    assert all(v["author_username"] == "kelly" for v in versions)
    assert [v["ingredient_count"] for v in versions] == [2, 2, 2]
    assert versions[1]["change_description"] == "rename"


def test_noop_edit_skips_version(client):
    token = _register(client, "liam")
    recipe_id = _create(client, token).json()["id"]
    res = client.put(f"/api/recipes/{recipe_id}", json=_payload(), headers=_auth(token))
    assert res.status_code == 200
    assert res.json()["version"]["version_number"] == "1.0"
    versions = client.get(f"/api/recipes/{recipe_id}/versions", headers=_auth(token)).json()
    assert len(versions) == 1


def test_trigger_blocks_update(client):
    token = _register(client, "mia")
    version_id = _create(client, token).json()["version"]["id"]
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE recipe_versions SET version_number = '9.9' WHERE id = :vid"),
                {"vid": version_id},
            )
            conn.commit()
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        with engine.connect() as conn:
            conn.execute(
                text("UPDATE recipe_version_ingredients SET name = 'hacked' WHERE version_id = :vid"),
                {"vid": version_id},
            )
            conn.commit()


def test_version_detail_not_found(client):
    token = _register(client, "noah")
    recipe_id = _create(client, token).json()["id"]
    res = client.get(f"/api/recipes/{recipe_id}/versions/999", headers=_auth(token))
    assert res.status_code == 404


def test_version_from_other_recipe_404(client):
    token = _register(client, "olivia")
    a_id = _create(client, token, title="Recipe A").json()["id"]
    b_id = _create(client, token, title="Recipe B").json()["id"]
    a_version_id = client.get(f"/api/recipes/{a_id}/versions", headers=_auth(token)).json()[0]["id"]
    res = client.get(f"/api/recipes/{b_id}/versions/{a_version_id}", headers=_auth(token))
    assert res.status_code == 404