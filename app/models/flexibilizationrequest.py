from pydantic import BaseModel
from typing import Optional


class FlexibilizationRequest(BaseModel):
    """
    Class for defining a flexibilization request for a given program;
    """

    id: str
    program: Optional[str]
    # rules: List[FlexibilizationRule]
