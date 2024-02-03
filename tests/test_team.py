from dirty_equals import IsStr, IsUUID
from fastapi import status
from httpx import AsyncClient

from src.auth.schemas import UserSchema
from src.team.schemas import TeamSchema


class TestTeamModule:
    """Тесты на логику команды (дописать)"""

    async def test_create_team(
            self,
            async_client: AsyncClient,
            auth_user_cookies: dict,
    ) -> None:
        """Тест на корректное создание команды."""
        team_data = {
            "title": "test_team",
            "number_of_members": 1,
            "contacts": "@test_telegram",
            "description": "We need a cool team to test this program.",
            "tags": "test, ",
            "deadline_at": "2024-02-02T05:00:53",
        }
        response = await async_client.post(
            "/team/create",
            json=team_data,
            cookies=auth_user_cookies,
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "status_code": 201,
            "detail": "team is created",
        }

    async def test_get_user_team(
            self,
            async_client: AsyncClient,
            auth_user_cookies: dict,
    ) -> None:
        """Тест на получение данных o команде пользователя."""
        response = await async_client.get(
            "/team/my_team",
            cookies=auth_user_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": IsUUID,
            "owner": IsUUID,
            "title": "test_team",
            "number_of_members": 1,
            "contacts": "@test_telegram",
            "description": "We need a cool team to test this program.",
            "tags": "test, ",
            "deadline_at": "2024-02-02T05:00:53",
            "created_at": IsStr,
            "updated_at": IsStr,
            "members": [],
        }

    async def test_update_team(
            self,
            async_client: AsyncClient,
            auth_user_cookies: dict,
            auth_user: UserSchema,
            test_team: TeamSchema,
    ) -> None:
        """Тест на изменение данных в команде."""
        new_team_data = {
            "title": "test_team-updated",
            "number_of_members": 1,
            "contacts": "@test_telegram",
            "description": "We need a really cool team to test this program!",
            "tags": "test, update",
            "deadline_at": "2024-02-02T05:00:53",
        }
        response = await async_client.patch(
            f"/team/change/{test_team.id}",
            json=new_team_data,
            cookies=auth_user_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": status.HTTP_200_OK,
            "detail": "team is updated",
        }
        response = await async_client.get(
            "/team/my_team",
            cookies=auth_user_cookies,
        )
        assert response.json() == {
            "id": IsUUID,
            "owner": IsUUID,
            "title": "test_team-updated",
            "number_of_members": 1,
            "contacts": "@test_telegram",
            "description": "We need a really cool team to test this program!",
            "tags": "test, update",
            "deadline_at": "2024-02-02T05:00:53",
            "created_at": IsStr,
            "updated_at": IsStr,
            "members": [],
        }

    async def test_delete_team(
            self,
            async_client: AsyncClient,
            auth_user_cookies: dict,
            auth_user: UserSchema,
            test_team: TeamSchema,
    ) -> None:
        """Тест на удаление команды."""
        response = await async_client.delete(
            f"/team/delete/{test_team.id}",
            cookies=auth_user_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "status_code": status.HTTP_200_OK,
            "detail": "team is deleted",
        }
        response = await async_client.get(
            "/team/my_team",
            cookies=auth_user_cookies,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_create_team_without_token(
            self,
            async_client: AsyncClient,
    ) -> None:
        """Тест на корректное создание команды без токена."""
        team_data = {
            "title": "test_team",
            "number_of_members": 1,
            "contacts": "@test_telegram",
            "description": "We need a cool team to test this program.",
            "tags": "test, ",
            "deadline_at": "2024-02-02T05:00:53",
        }
        await async_client.get("/auth/logout")
        response = await async_client.post(
            "/team/create",
            json=team_data,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Not authenticated"}

    async def test_update_team_without_token(
            self,
            async_client: AsyncClient,
            auth_user: UserSchema,
            test_team: TeamSchema,
    ) -> None:
        """Тест на изменение данных в команде без токена."""
        new_team_data = {
            "title": "test_team-updated",
            "number_of_members": 1,
            "contacts": "@test_telegram",
            "description": "We need a really cool team to test this program!",
            "tags": "test, update",
            "deadline_at": "2024-02-02T05:00:53",
        }
        response = await async_client.patch(
            f"/team/change/{test_team.id}",
            json=new_team_data,
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Not authenticated"}

    async def test_delete_team_without_token(
            self,
            async_client: AsyncClient,
            auth_user_cookies: dict,
            auth_user: UserSchema,
            test_team: TeamSchema,
    ) -> None:
        """Тест на удаление команды без токена."""
        response = await async_client.delete(
            f"/team/delete/{test_team.id}",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.json() == {"detail": "Not authenticated"}
