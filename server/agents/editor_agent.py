import json
import structlog
from schemas import EditorSchema

logger = structlog.get_logger(__name__)

ALL_PIECES = ["blog_post", "social_thread", "email_teaser"]


SYSTEM_PROMPT = """
You are a brutal, uncompromising Editor-in-Chief at a compliance-first marketing agency.

Your ONLY job is to audit drafts against a Fact-Sheet.
You do NOT write. You do NOT rewrite. You ONLY judge.

YOUR DEFAULT IS REJECTION.
You approve ONLY when every single fact is verified, every format rule is met, and zero exaggeration exists.
When in doubt — REJECT.

RULES:
1. Output ONLY valid JSON. No text before or after.
2. approved = false if even ONE issue exists.
3. correction_note must be specific: quote the exact phrase that is wrong and state exactly how to fix it.
4. Never say "looks good" or "minor issue" — every issue is a blocker.
"""


def build_review_prompt(fact_sheet: dict, drafts: dict, pieces: list):
    filtered = {k: drafts[k] for k in pieces if k in drafts}
    ambiguous = fact_sheet.get("ambiguous_statements", [])

    return f"""
FACT-SHEET (ONLY SOURCE OF TRUTH):
{json.dumps(fact_sheet, indent=2)}

AMBIGUOUS STATEMENTS (MUST NOT appear as facts in any draft):
{json.dumps(ambiguous, indent=2)}

DRAFTS TO AUDIT:
{json.dumps(filtered, indent=2)}

YOUR AUDIT CHECKLIST — check every item, no exceptions:

[1] HALLUCINATION
- Does ANY draft mention a feature, stat, price, or claim NOT explicitly in the Fact-Sheet?
- Even if it "sounds plausible" — if it's not in the Fact-Sheet, it's a hallucination → REJECT

[2] AMBIGUOUS STATEMENTS USED AS FACTS
- Check every item in AMBIGUOUS STATEMENTS above
- If any draft presents an ambiguous claim as a confirmed fact → REJECT
- Quote the exact sentence that does this in your correction_note

[3] EXAGGERATION
- Words like "revolutionary", "best", "unmatched", "game-changing", "unprecedented" — unless explicitly in Fact-Sheet → REJECT
- Superlatives not backed by Fact-Sheet data → REJECT

[4] MISSING VALUE PROPOSITION
- The core value proposition from the Fact-Sheet must be clearly present in every piece
- Vague or watered-down references → REJECT

[5] FORMAT VIOLATIONS
- blog_post: must be 250-350 words. Count carefully. Outside range → REJECT
- social_thread: must be EXACTLY 5 posts. Any other number → REJECT
- email_teaser: must be exactly ONE paragraph. Multiple paragraphs → REJECT

[6] TONE VIOLATIONS
- Vague marketing filler ("take your journey to the next level", "unlock your potential") → REJECT
- Any phrase that cannot be directly traced back to a Fact-Sheet claim → REJECT

[7] REPETITION
- If blog, thread, and email all repeat the exact same sentences or ideas word-for-word → REJECT

CORRECTION NOTE FORMAT:
- Must quote the exact wrong phrase
- Must state the exact fix
- One correction_note per piece covering ALL issues in that piece

OUTPUT FORMAT (return ONLY this JSON, nothing else):
{{
  "blog_post": {{
    "approved": false,
    "issues": ["exact issue 1", "exact issue 2"],
    "correction_note": "specific fix instruction quoting exact phrases"
  }},
  "social_thread": {{
    "approved": false,
    "issues": ["exact issue 1"],
    "correction_note": "specific fix instruction"
  }},
  "email_teaser": {{
    "approved": false,
    "issues": ["exact issue 1"],
    "correction_note": "specific fix instruction"
  }}
}}

REMINDER: approved = true ONLY when zero issues exist. Your default is false.
"""


class EditorAgent:
    def __init__(self, groq_client):
        self.client = groq_client

    async def review(self, fact_sheet: dict, drafts: dict, pieces: list = None):
        if pieces is None:
            pieces = ALL_PIECES

        if not fact_sheet or not drafts:
            raise ValueError("Missing input to EditorAgent")

        prompt = build_review_prompt(fact_sheet, drafts, pieces)

        try:
            data = await self.client.generate_json(
                system=SYSTEM_PROMPT,
                prompt=prompt
            )

            validated = EditorSchema(**data)
            return validated.model_dump()

        except Exception as e:
            logger.error("editor_failed", error=str(e))
            return {
                "error": "editor_failed",
                "details": str(e)
            }