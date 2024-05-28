from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.admin.routers import admin_router
from src.auth.routers import auth_router
from src.config import settings
from src.find.routers import find_router
from src.team.routers import team_router
from src.user_profile.routers import profile_router

app = FastAPI(
    title="Find Team 2.0",
    docs_url=f"/{settings.SECRET_PATH}",
)


"""Настройка CORS"""
origins = [
    "http://localhost:80",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://92.63.178.130",
    "https://92.63.178.130",
    "http://find-team.site",
    "https://find-team.site",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)

"""Запуск роутеров"""
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(team_router)
app.include_router(find_router)
app.include_router(admin_router)
