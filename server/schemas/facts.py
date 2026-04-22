from pydantic import BaseModel
from typing import List, Dict, Optional

class AmbiguousStatement(BaseModel):
    statement: str
    reason: str


class FactSchema(BaseModel):
    product_name: Optional[str]
    core_features: List[str]
    technical_specs: Dict[str, str]  
    target_audience: Optional[str]
    value_proposition: Optional[str]
    key_stats_or_numbers: List[str]
    tone_and_positioning: Optional[str]
    ambiguous_statements: List[AmbiguousStatement]
    source_summary: str