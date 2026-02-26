from fastapi import FastAPI
from src.web.routes.service import router as service_router
from src.web.routes.recording import router as recording_router

app = FastAPI()

app.include_router(service_router)
app.include_router(recording_router)
