from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app import lifespan
from src.configs.cors import cors_settings
from src.web.routes.health_check import router as health_router
from src.web.routes.analysis import router as analysis_router
from src.web.routes.chat import router as chat_router
from src.web.routes.transcript import router as transcript_router

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(analysis_router)
app.include_router(chat_router)
app.include_router(transcript_router)
