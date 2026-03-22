from fastapi import FastAPI

from llm_analysis_service.src.app import lifespan
from llm_analysis_service.src.web.routes.health_check import router as health_router
from llm_analysis_service.src.web.routes.analysis import router as analysis_router

app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(analysis_router)
