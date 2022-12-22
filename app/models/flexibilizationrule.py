from pydantic import BaseModel
from typing import Optional


class FlexibilizationRule(BaseModel):
    """
    Class for defining a flexibilization rule for a given program.
    """

    violationType: Optional[str]
    violationCode: Optional[int]
    violationAmount: Optional[float]
    violationUnit: Optional[str]
    constraintType: Optional[str]
    constraintCode: Optional[str]
    flexibilizationFactor: Optional[str]
