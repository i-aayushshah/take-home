"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.auth.domain.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.api.v1.candidates.domain.exceptions import AISummaryError, CandidateNotFoundError, InvalidScoreError
from app.api.v1.router import router as v1_router
from app.config import get_settings
from app.seed import seed_database
from app.shared.redis import get_redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify Redis connectivity on startup, seed data, and close resources on shutdown."""
    if os.getenv("TESTING") == "true":
        yield
        return

    redis = get_redis_client()
    await redis.ping()
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await seed_database(session)
    await engine.dispose()
    yield
    await redis.aclose()


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(title="TechKraft Recruitment Dashboard", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(v1_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Return service health status."""
        return {"status": "ok"}

    @app.exception_handler(InvalidCredentialsError)
    async def handle_invalid_credentials(_: Request, exc: InvalidCredentialsError) -> JSONResponse:
        """Translate invalid credential errors to HTTP 401."""
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(UserAlreadyExistsError)
    async def handle_user_exists(_: Request, exc: UserAlreadyExistsError) -> JSONResponse:
        """Translate duplicate registration errors to HTTP 409."""
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(CandidateNotFoundError)
    async def handle_candidate_not_found(_: Request, exc: CandidateNotFoundError) -> JSONResponse:
        """Translate missing candidate errors to HTTP 404."""
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidScoreError)
    async def handle_invalid_score(_: Request, exc: InvalidScoreError) -> JSONResponse:
        """Translate invalid score errors to HTTP 400."""
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(AISummaryError)
    async def handle_ai_summary_error(_: Request, exc: AISummaryError) -> JSONResponse:
        """Translate GitHub Models failures to HTTP 502."""
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    return app


app = create_app()
