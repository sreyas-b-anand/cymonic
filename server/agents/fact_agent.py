from services.llm_services import GroqClient
from schemas import FactSchema
import logging

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
You are a strict Fact-Check Agent.

Extract only verifiable facts.
Flag ambiguous or unsupported claims.
Do not hallucinate.

All technical_specs values must be strings.
If a value proposition is implied but not explicitly labeled, infer it conservatively.
Include all meaningful product features, including named systems or components
Return valid JSON only.
"""


def build_prompt(source_text: str) -> str:
    return f"""
Extract a structured fact sheet.

Schema:
{{
  "product_name": "string or null",
  "core_features": ["list"],
  "technical_specs": {{"key": "value"}},
  "target_audience": "string",
  "value_proposition": "string",
  "key_stats_or_numbers": ["list"],
  "tone_and_positioning": "string",
  "ambiguous_statements": [
    {{
      "statement": "text",
      "reason": "text"
    }}
  ],
  "source_summary": "string"
}}

Rules:
- Use null or [] if missing
- Do not add new information

Source:
<source_document>
{source_text}
</source_document>
"""


class FactAgent:
    def __init__(self, groq_client: GroqClient):
        self.client = groq_client

    async def run(self, source_text: str) -> dict:
        if not source_text:
            raise ValueError("No source text provided")

        prompt = build_prompt(source_text)

        try:
            data = await self.client.generate_json(
                system=SYSTEM_PROMPT,
                prompt=prompt
            )

            validated = FactSchema(**data)

            return validated.model_dump()

        except Exception as e:
            logger.error("fact_agent_failed: %s", str(e))
            return {
                "error": "fact_extraction_failed",
                "details": str(e)
            }