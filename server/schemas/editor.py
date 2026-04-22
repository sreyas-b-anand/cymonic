from pydantic import BaseModel
from typing import List, Optional


class ReviewBlock(BaseModel):
    approved: bool
    issues: List[str]
    correction_note: Optional[str]


class EditorSchema(BaseModel):
    blog_post: ReviewBlock
    social_thread: ReviewBlock
    email_teaser: ReviewBlock