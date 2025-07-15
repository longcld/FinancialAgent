import json
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from config import configs

from routers.chat import chat_router
from routers.health import health_router
from logger import logger

from dependencies.auth import get_api_key

debug = True
dependencies = [Depends(get_api_key)]

def configure_router(_app: FastAPI) -> None:

    _app.include_router(
        health_router,
        prefix='/api/v1/health',
        tags=['health'],
    )

    _app.include_router(
        chat_router,
        prefix='/api/v1/chat',
        tags=['core'],
        dependencies=dependencies
    )

def create_app():

    application = FastAPI(
        debug=debug,
        title="VPBank Financial Agent",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    configure_router(application)
    logger.info("Create app completed")
    return application


app = create_app()

def main():
    logger.info("Starting VPBank Financial Agent Server...")
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True if debug else False,
    )


if __name__ == "__main__":
    main()