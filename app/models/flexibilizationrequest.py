from pydantic import BaseModel
from typing import Optional, List
from app.models.flexibilizationrule import FlexibilizationRule


class FlexibilizationRequest(BaseModel):
    """
    Class for defining a flexibilization request for a given program;
    """

    id: str
    program: Optional[str]
    # rules: List[FlexibilizationRule]
