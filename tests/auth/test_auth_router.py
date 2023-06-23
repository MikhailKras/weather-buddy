import pytest
from httpx import AsyncClient

import src
from src.auth.email import Email
from src.auth.jwt import is_authenticated, create_reset_password_token
from src.auth.schemas import UserEmailVerificationInfo
from src.auth.tasks import task_send_verification_code, task_send_reset_password_mail
from src.config import RATE_LIMITER_FLAG
from src.main import app

pytest.importorskip("conftest_auth_router")


async def test_register_step_1_auth(ac: AsyncClient):
    def override_is_authenticated():
        return True

    app.dependency_overrides[is_authenticated] = override_is_authenticated

    response = await ac.get("/users/register/city")

    assert response.status_code == 307
    assert response.headers["location"] == "/users/me"

    app.dependency_overrides.pop(is_authenticated)


async def test_register_step_1_not_auth(ac: AsyncClient):
    response = await ac.get("/users/register/city")

    assert response.status_code == 200
    assert 'text/html' in response.headers["content-type"]


@pytest.mark.parametrize(
    "purpose, city_input, expected_status, expected_detail, expected_content_type",
    [
        ("not_purpose", "brussels", 400, "Invalid purpose!", None),
        ("register", "not_city", 400, "Invalid city!", None),
        ("register", "brussels", 200, None, "text/html"),
        ("settings", "brussels", 200, None, "text/html")
    ]
)
async def test_find_city_name_matches(
        ac: AsyncClient, purpose,
        city_input,
        expected_status,
        expected_detail,
        expected_content_type,
        fill_city_table_with_custom_data
):
    response = await ac.get(f"/users/{purpose}/city/choose_city_name", params={"city_input": city_input})

    assert response.status_code == expected_status
    if expected_detail:
        assert response.json()["detail"] == expected_detail
    if expected_content_type:
        assert expected_content_type in response.headers["content-type"]


async def test_register_step_1_submit(ac: AsyncClient, city_data, registration_token):
    response = await ac.post("users/register/city", json={"city_id": city_data["id"]})

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

    ac.cookies.delete("registration_token")


async def test_register_step_2_submit(
        ac: AsyncClient,
        fill_city_table_with_custom_data,
        monkeypatch: pytest.MonkeyPatch):
    def send_verification_code_mock(*args, **kwargs):
        pass

    monkeypatch.setattr(task_send_verification_code, "delay", send_verification_code_mock)

    response = await ac.post("/users/register/details", json={
        "username": "test_user1",
        "password": "string1",
        "email": "test@example.com"
    })

    assert response.status_code == 201
    assert response.json()["message"] == "Registration successful. Please verify your email to gain full access."


async def test_register_step_2_submit_existing_username(ac: AsyncClient, existing_user, fill_city_table_with_custom_data):
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


async def test_register_success(ac: AsyncClient):
    message = "Registration successful!"
    response = await ac.get(f"/users/register/success", params={"message": message})

    assert response.status_code == 200
    assert "registration_token" in response.headers["set-cookie"]
    assert 'text/html' in response.headers["content-type"]


async def test_verify_email_page(ac: AsyncClient, registration_token):
    response = await ac.get(f"/users/verify-email-page/{registration_token}")

    assert 'text/html' in response.headers["content-type"]


@pytest.mark.parametrize(
    "token, expected_status, expected_detail, expected_message, user_data",
    [
        ("test_token_1", 200, None, "Email verification successful", "some user data"),
        ("test_token_2", 400, "Email already verified", None, "some user data"),
        ("test_token_3", 404, "User not found", None, None),
        ("fake_token", 404, "Email verification token not found", None, "some user data"),
    ]
)
async def test_verify_email(ac: AsyncClient,
                            existing_verifications,
                            token,
                            expected_status,
                            expected_detail,
                            expected_message,
                            user_data,
                            fill_city_table_with_custom_data,
                            monkeypatch: pytest.MonkeyPatch
                            ):
    def get_email_from_token_mock(*args, **kwargs):
        return "email"

    async def get_user_by_email_mock(*args, **kwargs):
        return user_data

    monkeypatch.setattr(src.auth.router, "get_email_from_token", get_email_from_token_mock)
    monkeypatch.setattr(src.auth.router, "get_user_by_email", get_user_by_email_mock)
    response = await ac.get(f"/users/verify-email/{token}", headers={"Rate-Limiter-Flag": RATE_LIMITER_FLAG})
    assert response.status_code == expected_status
    if expected_detail:
        assert response.json()["detail"] == expected_detail
    if expected_message:
        assert response.json()["message"] == expected_message


async def test_get_send_verification_email_page(ac: AsyncClient):
    response = await ac.get("/users/email-verification")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.parametrize(
    "is_auth, expected_status, location, content_type",
    [
        (True, 307, "/users/me", None),
        (False, 200, None, "text/html")
    ]
)
async def test_get_password_reset_page_with_email(
        ac: AsyncClient,
        is_auth,
        expected_status,
        location,
        content_type
):
    def override_is_authenticated():
        return is_auth

    app.dependency_overrides[is_authenticated] = override_is_authenticated

    response = await ac.get("/users/password-reset")

    assert response.status_code == expected_status

    if location:
        assert response.headers["location"] == location

    if content_type:
        assert content_type in response.headers["content-type"]


@pytest.mark.parametrize(
    "email_data, user_id, verified, expected_status, message, detail",
    [
        ({"email": "test_user_1@test.com"}, 1, False, 403, None, "Email not verified"),
        ({"email": "test_user_2@test.com"}, 2, True, 200, "Reset password email sent successfully", None),
        ({"email": "user_not_found@test.com"}, 3, False, 404, None, "User not found")
    ]
)
async def test_post_email_for_password_reset(
        ac: AsyncClient,
        existing_verifications,
        email_data,
        user_id,
        verified,
        expected_status,
        message,
        detail,
        fill_city_table_with_custom_data,
        monkeypatch: pytest.MonkeyPatch,
):

    def send_reset_password_mail_mock(*args, **kwargs):
        pass

    async def get_user_email_verification_info_mock(*args, **kwargs):
        return UserEmailVerificationInfo(id=user_id, user_id=user_id, token="test_token", verified=verified)

    monkeypatch.setattr(task_send_reset_password_mail, "delay", send_reset_password_mail_mock)
    monkeypatch.setattr(src.auth.router, "get_user_email_verification_info", get_user_email_verification_info_mock)

    response = await ac.post("/users/password-reset", headers={"Rate-Limiter-Flag": RATE_LIMITER_FLAG}, json=email_data)

    assert response.status_code == expected_status

    if message:
        assert response.json()["message"] == message

    if detail:
        assert response.json()["detail"] == detail


async def test_get_password_reset_page_with_passwords(
        ac: AsyncClient,
):
    reset_password_token_value = create_reset_password_token(
        user_id=1
    )
    response = await ac.get(
        f"/users/password-reset/form/{reset_password_token_value}"
    )

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.parametrize(
    "user_id, expected_status, detail, message",
    [
        (1, 200, None, "Password updated successfully"),
        (1000, 404, "User not found", None)
    ]
)
async def test_reset_password(
        ac: AsyncClient,
        existing_verifications,
        user_id,
        expected_status,
        detail,
        message,
        fill_city_table_with_custom_data
):
    reset_password_token_value = create_reset_password_token(
        user_id=user_id
    )
    password_reset = {
        "password": "string1",
        "password_confirm": "string1"
    }
    response = await ac.patch(
        f"/users/password-reset/update/{reset_password_token_value}",
        json=password_reset
    )

    assert response.status_code == expected_status
    if detail:
        assert response.json()["detail"] == detail
    if message:
        assert response.json()["message"] == message


@pytest.mark.parametrize(
    "user_id, verified, expected_status, detail, message",
    [
        (1, False, 200, None, "Verification email sent successfully"),
        (2, True, 400, "Email already verified", None),
        (3, False, 500, "Failed to send verification email. Please try again later.", None)
    ]
)
async def test_send_verification_email(ac: AsyncClient,
                                       existing_verifications,
                                       user_id,
                                       verified,
                                       expected_status,
                                       detail,
                                       message,
                                       fill_city_table_with_custom_data,
                                       monkeypatch: pytest.MonkeyPatch,
                                       ):
    async def get_user_email_verification_info_mock(*args, **kwargs):
        return UserEmailVerificationInfo(id=user_id, user_id=user_id, token="test_token", verified=verified)

    def send_verification_code_mock(*args, **kwargs):
        if user_id == 3:
            raise Exception
        pass

    monkeypatch.setattr(src.auth.router, "get_user_email_verification_info", get_user_email_verification_info_mock)
    monkeypatch.setattr(task_send_verification_code, "delay", send_verification_code_mock)
    response = await ac.post("/users/email-verification", headers={"Rate-Limiter-Flag": RATE_LIMITER_FLAG})

    assert response.status_code == expected_status
    if detail:
        assert response.json()["detail"] == detail
    if message:
        assert response.json()["message"] == message


@pytest.mark.parametrize(
    "is_auth, expected_status, location, content_type",
    [
        (True, 307, "/users/me", None),
        (False, 200, None, "text/html")
    ]
)
async def test_login_user_get_form(
        ac: AsyncClient, is_auth,
        expected_status,
        location,
        content_type
):
    def override_is_authenticated():
        return is_auth

    app.dependency_overrides[is_authenticated] = override_is_authenticated

    response = await ac.get("/users/login")

    assert response.status_code == expected_status

    if location:
        assert response.headers["location"] == location
    if content_type:
        assert content_type in response.headers["content-type"]

    app.dependency_overrides.pop(is_authenticated)


@pytest.mark.parametrize(
    "form_data, expected_status, expected_detail",
    [
        (True, 200, None),
        (None, 401, "Incorrect username or password")
    ]
)
async def test_login_for_access_token(
        ac: AsyncClient,
        form_data,
        expected_status,
        expected_detail,
        monkeypatch: pytest.MonkeyPatch
):
    async def authenticate_user_mock(*args, **kwargs):
        if form_data:
            class fake_form_data:
                username = "test_user"

            return fake_form_data
        return None

    fake_token_value = "some_token"

    def create_access_token_mock(*args, **kwargs):
        return fake_token_value

    monkeypatch.setattr(src.auth.router, "authenticate_user", authenticate_user_mock)
    monkeypatch.setattr(src.auth.router, "create_access_token", create_access_token_mock)

    response = await ac.post("/users/token", data={
        "username": "test_user",
        "password": "string1"
    })

    assert response.status_code == expected_status

    if expected_detail:
        assert response.json()["detail"] == expected_detail

    if form_data:
        assert response.cookies["access_token"] == '"Bearer {}"'.format(fake_token_value)
        assert response.json()["access_token"] == fake_token_value
        assert response.json()["token_type"] == "bearer"


async def test_read_users_me(ac: AsyncClient, fill_city_table_with_custom_data, monkeypatch: pytest.MonkeyPatch):
    async def get_user_email_verification_info_mock(*args, **kwargs):
        return UserEmailVerificationInfo(id=1, user_id=1, token="test_token", verified=False)
    monkeypatch.setattr(src.auth.router, "get_user_email_verification_info", get_user_email_verification_info_mock)
    response = await ac.get("/users/me")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.parametrize(
    "is_auth, expected_status, location",
    [
        (True, 307, "/users/login"),
        (False, 307, "/users/login")
    ]
)
async def test_logout(
        ac: AsyncClient,
        is_auth,
        expected_status,
        location
):
    def override_is_authenticated():
        return is_auth

    app.dependency_overrides[is_authenticated] = override_is_authenticated

    response = await ac.get("/users/logout")
    if is_auth:
        assert "access_token" in response.headers["set-cookie"]

    assert response.status_code == expected_status
    app.dependency_overrides.pop(is_authenticated)


async def test_get_account_settings(ac: AsyncClient):
    response = await ac.get("/users/settings")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


@pytest.mark.parametrize(
    "new_data, expected_status, detail, message",
    [
        ({"username": "new_username", "email": "new_email@mail.com"}, 200, None, "Data changed successfully!"),
        ({"username": "test_user", "email": "new_email@mail.com"}, 422, "This username is already registered!", None),
        ({"username": "new_username", "email": "test_user@gmail.com"}, 422, "This email is already registered!", None),
        ({"username": "my_user", "email": "my_user@gmail.com"}, 400, "No changes detected", None)
    ]
)
async def test_update_user_data(
        ac: AsyncClient,
        new_data,
        expected_status,
        detail,
        message,
        existing_user
):
    response = await ac.patch("/users/settings/update_data", json=new_data)
    if detail:
        assert response.json()["detail"] == detail
    if message:
        assert response.json()["message"] == message
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "city_id, expected_status, detail, message",
    [
        (2, 200, None, "City changed successfully!"),
        (1, 400, "City already chosen", None),
    ]
)
async def test_change_city_data(
        ac: AsyncClient,
        city_id,
        expected_status,
        detail,
        message,
):
    response = await ac.patch("/users/settings/change_city_data", json={"city_id": city_id})

    if detail:
        assert response.json()["detail"] == detail
    if message:
        assert response.json()["message"] == message


@pytest.mark.parametrize(
    "passwords, password_in_db, expected_status, message, detail",
    [
        ({
             "current_password": "correct_password1",
             "new_password": "new_password1",
             "repeat_password": "new_password1",
         }, "correct_password1", 200, "Password changed successfully!", None),
        ({
            "current_password": "correct_password1",
            "new_password": "new_password1",
            "repeat_password": "another_password1",

        }, "correct_password1", 400, None, "The provided passwords do not match"),
        ({
            "current_password": "correct_password1",
            "new_password": "correct_password1",
            "repeat_password": "correct_password1",

        }, "correct_password1", 400, None, "New password must be different from current password"),
        ({
            "current_password": "correct_password1",
            "new_password": "bad_pattern",
            "repeat_password": "bad_pattern",
        }, "correct_password1", 400, None, "New password must contain at least one digit, at least one letter"),
        ({
            "current_password": "correct_password1",
            "new_password": "short1",
            "repeat_password": "short1",
        }, "correct_password1", 400, None, "Password must contain at least 7 characters"),
        ({
            "current_password": "incorrect_password1",
            "new_password": "new_password1",
            "repeat_password": "new_password1",
        }, "correct_password1", 401, None, "Current password is incorrect")
    ]
)
async def test_change_password(
        ac: AsyncClient,
        passwords,
        password_in_db,
        expected_status,
        message,
        detail,
        monkeypatch: pytest.MonkeyPatch
):
    def verify_password_mock(*args, **kwargs):
        return passwords["current_password"] == password_in_db

    monkeypatch.setattr(src.auth.router, "verify_password", verify_password_mock)

    response = await ac.patch("/users/settings/change_password", json=passwords)

    assert response.status_code == expected_status

    if detail:
        assert response.json()["detail"] == detail

    if message:
        assert response.json()["message"] == message


async def test_delete_user(ac: AsyncClient):
    response = await ac.delete("/users/settings/delete_user")

    assert response.status_code == 204
    assert "access_token" in response.headers["set-cookie"]


async def test_get_my_city_info(ac: AsyncClient, city_data):
    response = await ac.get("/users/my_city_info")

    assert response.status_code == 307
    assert response.headers["location"] == f"/weather/info?city_id={city_data['id']}"
