import json
import structlog
from schemas import WriterSchema

logger = structlog.get_logger(__name__)
SYSTEM_PROMPT = """
You are a strict factual copywriter.

Rules:
- Use ONLY facts from the fact-sheet
- Do NOT convert claims into confirmed benefits
- If a claim is marked ambiguous, reflect uncertainty
- Do NOT add adjectives like "revolutionary", "cutting-edge"
- Do NOT generalize beyond given data
- Avoid repetition across formats

Writing:
- Blog must be detailed (300-500 words)
- Each format must highlight DIFFERENT aspects of the product
- Blog structure:
- Paragraph 1: Overview of product
- Paragraph 2: Core features (at least 3)
- Paragraph 3: Technical specs + limitations/uncertainty

Constraints:
- Total length: 250-350 words
- No fluff or repetition

Output:
- STRICT valid JSON only
"""

def build_generate_prompt(fact_sheet: dict, tone: str) -> str:
    return f"""
FACT SHEET:
{json.dumps(fact_sheet)}

TASK:
Generate content in tone: {tone}

1. blog_post
- 250 - 350 words
- Use \\n\\n for paragraphs

2. social_thread
- EXACTLY 5 posts
- Each 2-3 sentences and distinct

3. email_teaser
- 1 paragraph

Constraints:
- No new facts
- No repetition across formats
- Use concrete features and stats
- Blog must be between 250 and 350 words
- Do NOT exceed 350 words
- If longer, compress without losing facts
- Do NOT convert ambiguous claims into facts
- Use at least 3 distinct features in blog
- Each social post must highlight a DIFFERENT feature


OUTPUT FORMAT:
{{
  "blog_post": "string",
  "social_thread": ["string","string","string","string","string"],
  "email_teaser": "string"
}}
"""


def build_revise_prompt(piece: str, old_draft, correction_note: str, fact_sheet: dict) -> str:
    return f"""
FACT SHEET:
{json.dumps(fact_sheet)}

CONTENT TYPE: {piece}

ORIGINAL:
{json.dumps(old_draft)}

ISSUE:
{correction_note}

TASK:
- Modify ONLY necessary parts
- Keep structure unchanged
- Do NOT add new facts
- If removing → remove completely

OUTPUT:
{{
  "{piece}": "corrected content"
}}
"""


class WriterAgent:
    def __init__(self, groq_client):
        self.client = groq_client


    async def generate(self, fact_sheet: dict, tone: str = "professional") -> dict:
        if not fact_sheet:
            raise ValueError("Fact sheet is required")

        prompt = build_generate_prompt(fact_sheet, tone)

        try:
            data = await self.client.generate_json(
                system=SYSTEM_PROMPT,
                prompt=prompt
            )
            validated = WriterSchema(**data)

            return validated.model_dump()

        except Exception as e:
            logger.error("writer_generate_failed", error=str(e))

            return {
                "error": "writer_generation_failed",
                "details": str(e)
            }


    async def revise(
        self,
        piece: str,
        old_draft,
        correction_note: str,
        fact_sheet: dict
    ):
        prompt = build_revise_prompt(piece, old_draft, correction_note, fact_sheet)

        try:
            data = await self.client.generate_json(
                system=SYSTEM_PROMPT,
                prompt=prompt
            )

            if piece not in data:
                raise ValueError("Missing revision key")
            
            if piece == "social_thread":
                if not (isinstance(data[piece], list) and len(data[piece]) == 5):
                    raise ValueError("Invalid social_thread format")
            else:
                if not isinstance(data[piece], str):
                    raise ValueError("Invalid text format")

            return data[piece]

        except Exception as e:
            logger.error("writer_revision_failed", error=str(e))

            return {
                "error": "writer_revision_failed",
                "details": str(e)
            }