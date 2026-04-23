from fastapi import FastAPI
from routes import model_router , campaign_router

app = FastAPI(title="Cymonic FastAPI")

app.include_router(model_router , prefix="/api/v1")
app.include_router(campaign_router , prefix="/api/v1")
