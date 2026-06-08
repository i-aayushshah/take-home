"""FastAPI application entry point."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    app = FastAPI(title="TechKraft Recruitment Dashboard")

    @app.get("/health")
    async def health() -> dict[str, str]:
        """Return service health status."""
        return {"status": "ok"}

    return app


app = create_app()
