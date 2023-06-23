import pytest
from httpx import AsyncClient
from fastapi import status

from src.auth.jwt import create_registration_token
from src.auth.tasks import task_send_verification_code


async def test_registration_process(ac: AsyncClient, monkeypatch: pytest.MonkeyPatch, city_data, fill_city_table_with_custom_data):
    response = await ac.get("/users/register/city")

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

    response = await ac.get(f"/users/register/city/choose_city_name", params={"city_input": city_data["name"]})

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

    response = await ac.post("/users/register/city", json={"city_id": city_data["id"]})

    assert response.status_code == status.HTTP_302_FOUND
    assert response.cookies.get("registration_token") == create_registration_token(
        city_data["id"]
    )

    response = await ac.get("/users/register/details")

    assert response.status_code == status.HTTP_200_OK
    assert "text/html" in response.headers["content-type"]

    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123"
    }

    def send_verification_code_mock(*args, **kwargs):
        pass

    monkeypatch.setattr(task_send_verification_code, "delay", send_verification_code_mock)

    response = await ac.post("/users/register/details", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["message"] == "Registration successful. Please verify your email to gain full access."

    response = await ac.get("/users/register/success", params={"message": "message"})

    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.text
