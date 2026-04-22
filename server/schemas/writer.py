from pydantic import BaseModel, Field
from typing import List


class WriterSchema(BaseModel):
    blog_post: str = Field(..., min_length=50)
    social_thread: List[str] = Field(..., min_items=5, max_items=5)
    email_teaser: str = Field(..., min_length=10)