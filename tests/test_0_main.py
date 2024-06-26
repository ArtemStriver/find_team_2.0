import asyncio

from dirty_equals import IsStr, IsUUID
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
        Комплексный тест на проверку базового сценария работы c приложением:
        1. Авторизация двух пользователей.
        2. Создание команд пользователями.
        3. Обмен заявками на вступление в команду.
        4. Принятие заявок одним, отклонение заявки другим пользователем.
        5. Исключение пользователя из команды.
        6. Повторная заявка и прием пользователя в команду c последующим самостоятельным выходом из нее пользователя.
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
                "verified": True,
            },
        }
        user_1_cookies = {
            "find-team": response.cookies["find-team"],
            "rstoken": response.cookies["rstoken"],
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
                "verified": True,
            },
        }
        user_2_cookies = {
            "find-team": response.cookies["find-team"],
            "rstoken": response.cookies["rstoken"],
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
        response = await async_client.get(
            f"/find/team/{team_data_1['id']}",
            cookies=user_1_cookies,
        )
        team_data_1 = response.json()

        response = await async_client.get(
            f"/find/team/{team_data_2['id']}",
            cookies=user_2_cookies,
        )
        team_data_2 = response.json()

        """3.1. Заявка второго пользователя на вступление в команду первого пользователя."""
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
            "detail": "your application has been submitted",
        }

        """3.2. Заявка первого пользователя на вступление в команду второго пользователя."""
        _ = await async_client.post(
            "/auth/login",
            json=user_data_1,
        )
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
            "detail": "your application has been submitted",
        }

        """3.3. Проверка заявки на вступление в команду первого пользователя вторым."""
        response = await async_client.get(
            f"/team/applications_list?team_id={team_data_1['id']}",
            cookies=user_1_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{
            "user_id": str(register_user_2.id),
            "team_id": team_data_1["id"],
            "cover_letter": "Is user 2",
        }]

        """3.4. Проверка заявки на вступление в команду второго пользователя первым."""
        _ = await async_client.post(
            "/auth/login",
            json=user_data_2,
        )
        response = await async_client.get(
            f"/team/applications_list?team_id={team_data_2['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{
            "user_id": str(register_user_1.id),
            "team_id": team_data_2["id"],
            "cover_letter": "Is user 1",
        }]

        """4.1. Принятие заявки вторым пользователем."""
        response = await async_client.post(
            f"/team/take_comrade?comrade_id={register_user_1.id}&team_id={team_data_2['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "comrade added into team",
        }

        """4.2. Проверка списка членов второй команды."""
        response = await async_client.get(
            f"/team/members_list?team_id={team_data_2['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{
            "team_id": team_data_2["id"],
            "user_id": str(register_user_1.id),
            "username": register_user_1.username,
        }]

        """4.3. Отклонение заявки первым пользователем."""
        _ = await async_client.post(
            "/auth/login",
            json=user_data_1,
        )
        response = await async_client.post(
            f"/team/reject_comrade?comrade_id={str(register_user_2.id)}&team_id={team_data_1['id']}",
            cookies=user_1_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "comrade's application rejected",
        }

        """4.4. Проверка списка членов первой команды."""
        response = await async_client.get(
            f"/team/members_list?team_id={team_data_1['id']}",
            cookies=user_1_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

        """4.5. Проверка списка заявок первой команды."""
        response = await async_client.get(
            f"/team/applications_list?team_id={team_data_1['id']}",
            cookies=user_1_cookies,
        )
        await asyncio.sleep(1)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

        """5.1. Исключение первого пользователя из второй команды."""
        _ = await async_client.post(
            "/auth/login",
            json=user_data_2,
        )
        response = await async_client.post(
            f"/team/exclude_comrade?comrade_id={register_user_1.id}&team_id={team_data_2['id']}",
            cookies=user_1_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "comrade excluded",
        }

        """
        6.1. Повторная заявка и прием второго пользователя в команду первого
            c последующим самостоятельным выходом из нее пользователя.
        """
        response = await async_client.post(
            "/find/join",
            json={
                "team_id": team_data_1["id"],
                "cover_letter": "Is user 2, again",
            },
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK

        _ = await async_client.post(
            "/auth/login",
            json=user_data_1,
        )
        response = await async_client.post(
            f"/team/take_comrade?comrade_id={register_user_2.id}&team_id={team_data_1['id']}",
            cookies=user_1_cookies,
        )
        assert response.status_code == status.HTTP_200_OK

        _ = await async_client.post(
            "/auth/login",
            json=user_data_2,
        )

        response = await async_client.get(
            f"/team/members_list?team_id={team_data_1['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [{
            "team_id": team_data_1["id"],
            "user_id": str(register_user_2.id),
            "username": register_user_2.username,
        }]

        response = await async_client.post(
            f"/find/quit/{team_data_1['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "you leaved the team",
        }

        response = await async_client.get(
            f"/team/members_list?team_id={team_data_1['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

        """7.1. Изменение данных второй команды."""
        update_team_data = {
            "title": "test_team_2 (updated)",
            "type_team": "work",
            "number_of_members": 3,
            "team_description": "Updated second test team/",
            "team_deadline_at": "2010-10-10",
            "team_city": "Интернет",
            "tags": {
                "tag1": "test2 - update",
                "tag2": "new",
                "tag3": "new",
                "tag4": "2 new",
                "tag5": None,
                "tag6": None,
                "tag7": None,
            },
        }
        response = await async_client.patch(
            f"/team/change/{team_data_2['id']}",
            json=update_team_data,
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "team is updated",
        }

        """7.2. Проверка обновленных данных второй команды."""
        response = await async_client.get(
            f"/find/team/{team_data_2['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": str(team_data_2["id"]),
            "owner": str(register_user_2.id),
            "owner_name": register_user_2.username,
            "title": "test_team_2 (updated)",
            "type_team": "work",
            "number_of_members": 3,
            "team_description": "Updated second test team/",
            "team_deadline_at": "2010-10-10",
            "team_city": "Интернет",
            "created_at": IsStr,
            "updated_at": IsStr,
            "members": [],
            "tags": {
                "tag1": "test2 - update",
                "tag2": "new",
                "tag3": "new",
                "tag4": "2 new",
                "tag5": None,
                "tag6": None,
                "tag7": None,
            },
        }

        """7.3. Удаление второй команды."""
        response = await async_client.delete(
            f"/team/delete/{team_data_2['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "team is deleted",
        }

        """7.4. Проверка отсутствия данных второй команды."""
        response = await async_client.get(
            f"/find/team/{team_data_2['id']}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {
            "detail": "there is no such team",
        }

        """8.1. Изменение профиля пользователя."""
        update_team_data = {
            "username": "new_test_user_2_name",
            "image_path": "string",
            "contacts": {
                "email": register_user_2.email,
                "vk": None,
                "telegram": None,
                "discord": None,
                "other": "some link",
            },
            "description": "My new description.",
            "hobbies": {
                "lifestyle1": "faith",
                "lifestyle2": "love",
                "lifestyle3": "hope",
                "sport1": None,
                "sport2": None,
                "sport3": "sport",
                "work1": "hard-work",
                "work2": None,
                "work3": None,
            },
        }
        response = await async_client.patch(
            "/profile/change",
            json=update_team_data,
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "profile is updated",
        }

        """8.2 Проверка изменений профиля пользователя."""
        response = await async_client.get(
            f"/profile/{register_user_2.id}",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": IsUUID,
            "user_id": str(register_user_2.id),
            "username": "new_test_user_2_name",
            "image_path": "string",
            "contacts": {
                "email": register_user_2.email,
                "vk": None,
                "telegram": None,
                "discord": None,
                "other": "some link",
            },
            "description": "My new description.",
            "hobbies": {
                "lifestyle1": "faith",
                "lifestyle2": "love",
                "lifestyle3": "hope",
                "sport1": None,
                "sport2": None,
                "sport3": "sport",
                "work1": "hard-work",
                "work2": None,
                "work3": None,
            },
        }

        """8.3. Удаление профиля пользователя."""
        response = await async_client.delete(
            "/profile/delete",
            cookies=user_2_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": 200,
            "detail": "user and his profile deleted",
        }

        """8.4. Проверка отсутствия профиля пользователя."""
        _ = await async_client.post(
            "/auth/login",
            json=user_data_1,
        )
        response = await async_client.get(
            f"/profile/{register_user_2.id}",
            cookies=user_1_cookies,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
