from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.configs.cors import cors_settings
from src.web.routes.health_check import router as service_router
from src.web.routes.recording import router as recording_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(service_router)
app.include_router(recording_router)
