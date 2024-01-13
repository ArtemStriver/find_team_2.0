from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Find Team 2.0",
    docs_url="/",
)

"""Настройка CORS"""
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin", "Authorization"],
)

# TODO почитать надо ли это, если да, то настроить админку.
# admin.mount_to(app)

main_router = APIRouter(prefix='/api/')

"""Запуск роутеров"""
main_router.include_router(auth_router)
