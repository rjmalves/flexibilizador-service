from pydantic import BaseModel
from typing import Optional


class FlexibilizationResult(BaseModel):
    """
    Class for defining a flexibilization result for a given request.
    """

    flexType: Optional[str]
    flexStage: Optional[int]
    flexCode: Optional[int]
    flexPatamar: Optional[str]
    flexLimit: Optional[str]
    flexSubsystem: Optional[str]
    flexAmount: Optional[float]
