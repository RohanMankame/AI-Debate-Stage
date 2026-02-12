from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import routes

def create_app() -> FastAPI:
    app = FastAPI(title="AI Debate Stage - Backend")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(routes.router, prefix="/v1")
    return app

app = create_app()