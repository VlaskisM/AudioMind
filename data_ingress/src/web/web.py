from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.db.relational.db import init_db
from src.web.routes.service import router as service_router
from src.web.routes.recording import router as recording_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(service_router)
app.include_router(recording_router)