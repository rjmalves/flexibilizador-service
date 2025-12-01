
from pydantic import BaseModel


class FlexibilizationResult(BaseModel):
    """
    Class for defining a flexibilization result for a given request.
    """

    flexType: str | None
    flexStage: int | None
    flexCode: int | None
    flexPatamar: str | None
    flexLimit: str | None
    flexSubsystem: str | None
    flexAmount: float | None
