import asyncio

import pytest
from dirty_equals import IsInt, IsUUID
from httpx import AsyncClient
from starlette import status

from src.auth import utils as auth_utils


@pytest.mark.skip
class TestAuthUser:
    """Тесты на регистрацию, логин, перевыпуск токенов и логаут пользователя."""

    async def test_user_registration(
            self,
            async_client: AsyncClient,
    ) -> None:
        """Тест на регистрацию пользователя."""
        user_data = {
            "username": "test_user",
            "email": "user@example.com",
            "hashed_password": "string",
            "confirmed_password": "string",
            "verified": True,
        }
        response = await async_client.post(
            "/auth/register",
            json=user_data,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "status_code": 201,
            "detail": "test_user",
        }

    async def test_user_cookies_after_register(
            self,
            async_client: AsyncClient,
    ) -> None:
        """Тест - проверка кук после регистрации пользователя."""
        assert auth_utils.decode_jwt(async_client.cookies["find-team"]) == {
            "email": "user@example.com",
            "exp": IsInt,
            "iat": IsInt,
            "sub": IsUUID,
            "type": "find-team",
        }

    async def test_user_login(
            self,
            async_client: AsyncClient,
    ) -> None:
        """Тест авторизации пользователя."""
        user_data = {
            "email": "user@example.com",
            "password": "string",
        }
        response = await async_client.post(
            "/auth/login",
            data=user_data,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "test_user",
        }

    async def test_user_cookies_after_login(
            self,
            async_client: AsyncClient,
    ) -> None:
        """Тест - проверка кук после авторизации пользователя."""
        assert auth_utils.decode_jwt(async_client.cookies["find-team"]) == {
            "email": "user@example.com",
            "exp": IsInt,
            "iat": IsInt,
            "sub": IsUUID,
            "type": "find-team",
        }

    async def test_refresh_token(
            self,
            async_client: AsyncClient,
    ) -> None:
        """Тест - перевыпуска access_token по refresh_token."""
        old_access_token = async_client.cookies["find-team"]
        old_refresh_token = async_client.cookies["rstoken"]

        await asyncio.sleep(1)

        response = await async_client.get(
            "/auth/refresh",
            cookies={"rstoken": old_refresh_token},
        )
        assert (response.cookies["find-team"] != old_access_token
                and async_client.cookies["find-team"] != old_access_token)
        assert (response.cookies["rstoken"] != old_refresh_token
                and async_client.cookies["rstoken"] != old_refresh_token)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "test_user",
        }

    async def test_user_logout(
            self,
            async_client: AsyncClient,
    ) -> None:
        """Тест выхода пользователя и удаление токенов."""
        response = await async_client.get(
            "/auth/logout",
            cookies={"find-team": async_client.cookies["find-team"]},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "Bye, test_user!",
        }
        with pytest.raises(KeyError):
            _ = response.cookies["find-team"]
        with pytest.raises(KeyError):
            _ = response.cookies["rstoken"]

    async def test_refresh_token_without_token(
            self,
            async_client: AsyncClient,
    ) -> None:
        """Тест обновления токенов без refresh_token и c некорректным токеном."""
        async_client.cookies.delete("find-team")
        async_client.cookies.delete("rstoken")

        response = await async_client.get(
            "/auth/refresh",
            cookies={"rstoken": ""},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {
            "detail": "Not authenticated",
        }

        response = await async_client.get(
            "/auth/refresh",
            cookies={"rstoken": "some.incorrect.refresh.token"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "could not refresh access token",
        }
