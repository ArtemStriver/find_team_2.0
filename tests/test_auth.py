# from dirty_equals import IsUUID
from starlette import status
from starlette.testclient import TestClient

from src.main import app


class TestAuthUser:
    """Тесты на регистрацию, логин и логаут."""

    async def test_user_registration(
            self,
            async_client: TestClient,
    ) -> None:
        """Тест на регистрацию пользователя."""
        user_data = {
            "email": "user@example.com",
            "password": "string"
        }
        response = await async_client.post(
            app.url_path_for("register:register"),
            json=user_data
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            # "id": IsUUID,
            "email": user_data.get("email"),
            "is_active": True,
            "is_superuser": False,
            "is_verified": False,
        }
