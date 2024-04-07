from dirty_equals import IsStr
from httpx import AsyncClient
from starlette import status

from src.auth.schemas import UserSchema


class TestAllFunctional:

    async def test_base(
        self,
        async_client: AsyncClient,
        register_user_1: UserSchema,
        register_user_2: UserSchema,
    ) -> None:
        """
        Комплексный тест на проверку базового сценария работы с приложением:
        1. Авторизация двух пользователей.
        2. Создание команд пользователями.
        3. Обмен заявками на вступление в команду.
        4. Принятие заявок одним, отклонение заявки другим пользователем.
        5. Исключение пользователя из команды.
        6. Повторная заявка и прием пользователя в команду с последующим самостоятельным выходом из нее пользователя.
        7. Изменение данных и удаление команды.
        8. Изменение и удаление профиля пользователя.
        """

        """1.1. Авторизация первого пользователя."""
        user_data_1 = {
            "email": "test1@example.com",
            "password": "string",
        }
        response = await async_client.post(
            "/auth/login",
            json=user_data_1,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "access_token": IsStr,
            "refresh_token": IsStr,
            "user": {
                "id": str(register_user_1.id),
                "username": "test1",
                "email": "test1@example.com",
                'verified': True,
            }
        }
        user_1_cookies = {
            "find-team": response.cookies["find-team"],
            "rstoken": response.cookies["rstoken"]
        }

        """1.2. Авторизация второго пользователя."""
        user_data_2 = {
            "email": "test2",
            "password": "string",
        }
        response = await async_client.post(
            "/auth/login",
            json=user_data_2,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "access_token": IsStr,
            "refresh_token": IsStr,
            "user": {
                "id": str(register_user_2.id),
                "username": "test2",
                "email": "test2@example.com",
                'verified': True,
            }
        }
        user_2_cookies = {
            "find-team": response.cookies["find-team"],
            "rstoken": response.cookies["rstoken"]
        }

        """2.1 Создание команды первым пользователем."""

