from fastapi import APIRouter
from pipelines.agent_pipeline import AgentPipeline
from schemas.requests import TextRequest
model_router = APIRouter()

ap = AgentPipeline()

@model_router.post("/generate")
async def generate_content(request: TextRequest):
    
    text = request.text
    result = await ap.run(text)

    return {
        "input": text,
        "output": result
    }
