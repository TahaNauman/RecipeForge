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


def test_create_recipe(client):
    token = _register(client, "alice")
    res = _create(client, token)
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Chicken Karahi"
    assert body["author_username"] == "alice"
    assert body["version"]["version_number"] == "1.0"
    assert [i["name"] for i in body["version"]["ingredients"]] == ["chicken", "tomatoes"]
    assert len(body["version"]["instructions"]) == 2
    assert "password_hash" not in body


def test_create_recipe_unauthenticated(client):
    res = client.post("/api/recipes", json=_payload())
    assert res.status_code == 401


def test_create_recipe_empty_ingredients(client):
    token = _register(client, "bob")
    res = _create(client, token, ingredients=[])
    assert res.status_code == 422


def test_create_recipe_short_title(client):
    token = _register(client, "bob2")
    res = _create(client, token, title="x")
    assert res.status_code == 422


def test_get_recipe_not_found(client):
    token = _register(client, "carl")
    res = client.get("/api/recipes/999", headers=_auth(token))
    assert res.status_code == 404


def test_get_recipe_detail(client):
    token = _register(client, "dana")
    recipe_id = _create(client, token).json()["id"]
    res = client.get(f"/api/recipes/{recipe_id}")
    assert res.status_code == 200
    assert res.json()["title"] == "Chicken Karahi"
    assert res.json()["version"]["ingredients"][0]["unit"] == "kg"


def test_list_recipes_newest_first(client):
    token = _register(client, "erin")
    first = _create(client, token, title="First Recipe").json()["id"]
    second = _create(client, token, title="Second Recipe").json()["id"]
    res = client.get("/api/recipes")
    assert res.status_code == 200
    ids = [r["id"] for r in res.json()]
    assert ids.index(second) < ids.index(first)
    item = next(r for r in res.json() if r["id"] == first)
    assert item["ingredient_count"] == 2
    assert item["author_username"] == "erin"


def test_update_recipe_rewrites_snapshot(client):
    token = _register(client, "finn")
    recipe_id = _create(client, token, title="Original").json()["id"]
    res = client.put(
        f"/api/recipes/{recipe_id}",
        json={
            "title": "Renamed",
            "ingredients": [{"name": "beef", "quantity": 0.5, "unit": "kg"}],
            "instructions": [{"text": "Braise slowly"}],
        },
        headers=_auth(token),
    )
    assert res.status_code == 200
    body = res.json()
    assert body["title"] == "Renamed"
    assert body["cuisine"] == "Pakistani"  # untouched fields survive
    assert [i["name"] for i in body["version"]["ingredients"]] == ["beef"]
    assert body["version"]["ingredients"][0]["quantity"] == 0.5
    assert body["version"]["instructions"][0]["text"] == "Braise slowly"


def test_update_recipe_non_author_forbidden(client):
    owner = _register(client, "gary")
    intruder = _register(client, "gina")
    recipe_id = _create(client, owner).json()["id"]
    res = client.put(f"/api/recipes/{recipe_id}", json={"title": "Hijacked"}, headers=_auth(intruder))
    assert res.status_code == 403


def test_delete_recipe_and_author_only(client):
    owner = _register(client, "hank")
    other = _register(client, "hugo")
    recipe_id = _create(client, owner).json()["id"]
    assert client.delete(f"/api/recipes/{recipe_id}", headers=_auth(other)).status_code == 403
    assert client.delete(f"/api/recipes/{recipe_id}", headers=_auth(owner)).status_code == 204
    assert client.get(f"/api/recipes/{recipe_id}").status_code == 404