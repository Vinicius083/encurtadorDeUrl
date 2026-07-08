from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import urls_routes, usuarios_routes
from app.core.config import get_settings
from app.db.cassandra import close_session, get_session
from app.db.schema import init_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    session = get_session()
    init_schema(session)
    yield
    close_session()


settings = get_settings()
app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_routes.router)
app.include_router(urls_routes.router)


@app.get("/")
def healthcheck():
    return {"status": "ok", "app": settings.app_name}
