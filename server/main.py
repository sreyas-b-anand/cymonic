from fastapi import FastAPI
from routes import model_router , campaign_router
from middlewares import AuthMiddleware
app = FastAPI(title="Cymonic FastAPI")

app.add_middleware(AuthMiddleware)

app.include_router(model_router , prefix="/api/v1")
app.include_router(campaign_router , prefix="/api/v1")

