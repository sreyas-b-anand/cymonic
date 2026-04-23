import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import model_router, campaign_router, ws_router
from middlewares import AuthMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Orkestr.ai FastAPI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

app.include_router(model_router, prefix="/api/v1")
app.include_router(campaign_router, prefix="/api/v1")
app.include_router(ws_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}
