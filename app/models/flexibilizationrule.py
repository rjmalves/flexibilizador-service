from pydantic import BaseModel


class FlexibilizationRule(BaseModel):
    """
    Class for defining a flexibilization rule for a given program.
    """

    violationType: str | None
    violationCode: int | None
    violationAmount: float | None
    violationUnit: str | None
    constraintType: str | None
    constraintCode: str | None
    flexibilizationFactor: str | None
