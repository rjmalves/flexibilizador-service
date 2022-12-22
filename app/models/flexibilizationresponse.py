from pydantic import BaseModel
from typing import List

from app.models.flexibilizationresult import FlexibilizationResult


class FlexibilizationResponse(BaseModel):
    """
    Class for defining a flexibilization result for a given request.
    """

    result: List[FlexibilizationResult]
