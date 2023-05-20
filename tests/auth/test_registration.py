import pytest
from httpx import AsyncClient
from fastapi import status

from src.auth.email import Email
from src.auth.jwt import create_registration_token


async def test_registration_process(ac: AsyncClient, monkeypatch: pytest.MonkeyPatch):
    city_data = {
        "city": "Brussels",
        "country": "Belgium",
        "latitude": 50.85045,
        "longitude": 4.34878
    }

    response = await ac.get("/users/register/city")

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

    response = await ac.get(f"/users/register/city/choose_city_name?city_input={city_data['city']}")

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

    response = await ac.post("/users/register/city", json=city_data)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.cookies.get("registration_token") == create_registration_token(
        city_data["city"],
        city_data["country"],
        city_data["latitude"],
        city_data["longitude"]
    )

    response = await ac.get("/users/register/details")

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }

    async def send_verification_code_mock(*args, **kwargs):
        pass

    monkeypatch.setattr(Email, "send_verification_code", send_verification_code_mock)

    response = await ac.post("/users/register/details", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Registration successful. Please verify your email to gain full access."

    response = await ac.get("/users/register/success?message=message")

    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.text
