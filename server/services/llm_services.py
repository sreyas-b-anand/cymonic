import json
import os
from groq import AsyncGroq, APIError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not found in environment")


class GroqClient:
    def __init__(self, model: str):
        self.client = AsyncGroq(api_key=api_key)
        self.model = model

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=10),
        retry=retry_if_exception_type((APIError, json.JSONDecodeError, ValueError)),
        reraise=True
    )
    async def generate_json(self, system: str, prompt: str) -> dict:
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.1,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        )

        content = response.choices[0].message.content
        return json.loads(content)