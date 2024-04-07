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

        """2.1. Создание команды первым пользователем."""
        team_data_1 = {
            "title": "test_team_1",
            "type_team": "lifestyle",
            "number_of_members": 8,
            "team_description": "First test team/",
            "team_deadline_at": "2012-12-12",
            "team_city": "Интернет",
            "tags": {
                "tag1": "test1",
                "tag2": "1",
                "tag3": None,
                "tag4": None,
                "tag5": None,
                "tag6": None,
                "tag7": None,
            },
        }
        response = await async_client.post(
            "/team/create",
            json=team_data_1,
            cookies=user_1_cookies,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "status_code": 201,
            "detail": "team created",
        }

        """2.2. Создание команды вторым пользователем."""
        team_data_2 = {
            "title": "test_team_2",
            "type_team": "work",
            "number_of_members": 2,
            "team_description": "Second test team/",
            "team_deadline_at": "2012-12-12",
            "team_city": "Интернет",
            "tags": {
                "tag1": "test2",
                "tag2": "2",
                "tag3": "2",
                "tag4": None,
                "tag5": None,
                "tag6": None,
                "tag7": None,
            },
        }
        response = await async_client.post(
            "/team/create",
            json=team_data_2,
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "status_code": 201,
            "detail": "team created",
        }

        """2.3. Получение данных созданных команд."""
        response = await async_client.get(
            "/find/teams_list",
        )
        assert response.status_code == status.HTTP_200_OK
        if response.json()[0]["title"] == "test_team_1":
            team_data_1, team_data_2 = response.json()[0], response.json()[1]
        else:
            team_data_1, team_data_2 = response.json()[1], response.json()[2]

        """3.1. Заявка первого пользователя на вступление в команду второго пользователя."""
        response = await async_client.post(
            "/find/join",
            json={
                "team_id": team_data_2["id"],
                "cover_letter": "Is user 1",
            },
            cookies=user_1_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "your application has been submitted"
        }

        """3.2. Заявка второго пользователя на вступление в команду первого пользователя."""
        response = await async_client.post(
            "/find/join",
            json={
                "team_id": team_data_1["id"],
                "cover_letter": "Is user 2",
            },
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "your application has been submitted"
        }

        """3.3. Проверка заявок пользователей на вступление в команды."""