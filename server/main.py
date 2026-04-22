from fastapi import FastAPI
from routes import model_router

app = FastAPI(title="Cymonic FastAPI")

app.include_router(model_router , prefix="/api/v1")

