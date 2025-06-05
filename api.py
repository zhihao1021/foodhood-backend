from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import Headers
from starlette.middleware.base import RequestResponseEndpoint
from starlette.types import ASGIApp, Scope, Receive, Send

from contextlib import asynccontextmanager

from config import ORIGINS
from database.database import setup as setup_db
from routes.auth import router as auth_router
from routes.avatar import router as avatar_router
from routes.food import router as task_router
from routes.order import router as order_router
from routes.user import router as user_router


class SetAuthorizationFromCookiesMiddleware:
    app: ASGIApp

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers: dict[bytes, bytes] = dict(list(map(
            lambda pair: (pair[0].lower(), pair[1]),
            scope["headers"]
        )))
        if headers.get(b"authorization") is None and headers.get(b"cookie") is not None:
            token = headers[b"cookie"].split(b"token=")[-1].split(b";")[0]
            headers[b"authorization"] = b"Bearer " + token
            scope["headers"] = list(headers.items())
        await self.app(scope, receive, send)

    @classmethod
    def _add_custom_headers(cls, scope: Scope):
        scope["headers"].append((b"token", b"my_token"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_db()

    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(task_router)
app.include_router(avatar_router)
app.include_router(order_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SetAuthorizationFromCookiesMiddleware)
