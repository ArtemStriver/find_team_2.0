from dirty_equals import IsStr, IsUUID
from fastapi import status
from httpx import AsyncClient


class TestFindModule:

    async def test_team_list(
            self,
            async_client: AsyncClient,
            team: None,
            test_user_cookies: dict,
    ) -> None:
        """Тест на получение списка команд."""
        response = await async_client.get(
            "/find/teams_list",
            cookies=test_user_cookies,
        )
        team_id = response.json()[0]["id"]
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {"id": IsUUID,
             "title": "test",
             "number_of_members": 1,
             "tags": "test, ",
             "deadline_at": "2024-02-02T05:00:53",
             },
        ]
        """Тест на получение данных o команде."""
        response = await async_client.get(
            f"/find/team/{team_id}",
            cookies=test_user_cookies,
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": IsUUID,
            "owner": IsUUID,
            "title": "test",
            "number_of_members": 1,
            "contacts": "@test_telegram",
            "description": "We need a cool team to test this program.",
            "tags": "test, ",
            "deadline_at": "2024-02-02T05:00:53",
            "created_at": IsStr,
            "updated_at": IsStr,
            "members": [],
        }

    async def test_get_team_with_bad_team_id(
            self,
            async_client: AsyncClient,
            test_user_cookies: dict,
    ) -> None:
        """Тест на получение данных o команде c некорректным team_id."""
        response = await async_client.get(
            "/find/team/99407309-c938-492e-bc0f-08d93eff9183",
            cookies=test_user_cookies,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test(
            self,
            async_client: AsyncClient,
            test_user_cookies: dict,
    ) -> None: #
        """Тест на подачу заявки в команду."""

    async def test_leave_team(
            self,
            async_client: AsyncClient,
            test_user_cookies: dict,
    ) -> None:
        """Тест на выход из команды."""
