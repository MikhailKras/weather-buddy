import pytest
from httpx import AsyncClient

from src.auth.email import Email
from src.auth.jwt import is_authenticated
from src.main import app


async def test_register_step_1_auth(ac: AsyncClient, monkeypatch):
    def override_is_authenticated():
        return True
    app.dependency_overrides[is_authenticated] = override_is_authenticated

    response = await ac.get("/users/register/city")

    assert response.status_code == 307
    assert response.headers["location"] == "/users/me"


async def test_register_step_1_not_auth(ac: AsyncClient):
    response = await ac.get("/users/register/city")

    assert response.status_code == 200
    assert 'text/html' in response.headers["content-type"]


@pytest.mark.parametrize(
    "purpose, city_input, expected_status, expected_detail, expected_content_type",
    [
        ("not_purpose", "london", 400, "Invalid purpose!", None),
        ("register", "not_city", 400, "Invalid city!", None),
        ("register", "london", 200, None, "text/html"),
        ("settings", "london", 200, None, "text/html")
    ]
)
async def test_find_city_name_matches(
        ac: AsyncClient, purpose,
        city_input,
        expected_status,
        expected_detail,
        expected_content_type
):
    response = await ac.get(f"/users/{purpose}/city/choose_city_name?city_input={city_input}")

    assert response.status_code == expected_status
    if expected_detail:
        assert response.json()["detail"] == expected_detail
    if expected_content_type:
        assert expected_content_type in response.headers["content-type"]


async def test_register_step_1_submit(ac: AsyncClient, city_data, registration_token):
    response = await ac.post("users/register/city", json=city_data)

    assert response.status_code == 302
    assert response.headers["location"] == "/users/register/details"

    assert "registration_token" in response.cookies
    assert response.cookies["registration_token"] == registration_token


@pytest.mark.parametrize(
    "registration_token_value, expected_status, content_type, location",
    [
        ("valid_token", 200, "text/html", None),
        (None, 307, None, "/users/register/city")
    ]
)
async def test_register_step_2(
        ac: AsyncClient,
        registration_token,
        registration_token_value,
        expected_status,
        content_type,
        location
):
    if registration_token_value == "valid_token":
        registration_token_value = registration_token
    ac.cookies.set("registration_token", registration_token_value)

    response = await ac.get("/users/register/details")

    assert response.status_code == expected_status

    if content_type:
        assert content_type in response.headers["content-type"]
    if location:
        assert response.headers["location"] == location


async def test_register_step_2_submit(ac: AsyncClient, monkeypatch):
    async def send_verification_code_mock(self):
        pass
    monkeypatch.setattr(Email, "send_verification_code", send_verification_code_mock)

    response = await ac.post("/users/register/details", json={
        "username": "test_user1",
        "password": "string1",
        "email": "test@example.com"
    })

    assert response.status_code == 201
    assert response.json()["message"] == "Registration successful. Please verify your email to gain full access."


async def test_register_step_2_submit_existing_username(ac: AsyncClient, existing_user):

    response = await ac.post("/users/register/details", json={
        "username": existing_user["username"],
        "password": "string1",
        "email": "test@example.com"
    })

    assert response.status_code == 422
    assert response.json()["detail"] == "This username is already registered!"


async def test_register_step_2_submit_existing_email(ac: AsyncClient, existing_user):

    response = await ac.post("/users/register/details", json={
        "username": "test_user2",
        "password": "string1",
        "email": existing_user["email"]
    })

    assert response.status_code == 422
    assert response.json()["detail"] == "This email is already registered!"
