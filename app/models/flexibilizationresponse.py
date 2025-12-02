from pydantic import BaseModel, Field

from app.models.flexibilizationresult import FlexibilizationResult


class FlexibilizationResponse(BaseModel):
    """
    Response model for flexibilization results.

    Includes the output S3 key and list of applied flexibilizations.
    """

    success: bool = Field(
        ...,
        description="Whether flexibilization completed successfully",
    )
    execution_hash: str = Field(
        ...,
        description="Execution identifier that was processed",
    )
    output_key: str | None = Field(
        default=None,
        description="S3 key of the uploaded flexibilized deck",
        examples=["ingest/abc123def456_flexibilizado.zip"],
    )
    flexibilizations: list[FlexibilizationResult] = Field(
        default_factory=list,
        description="List of flexibilizations applied",
    )
    message: str | None = Field(
        default=None,
        description="Human-readable result message",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "execution_hash": "abc123def456",
                "output_key": "ingest/abc123def456_flexibilizado.zip",
                "flexibilizations": [
                    {
                        "flexType": "RE",
                        "flexStage": 1,
                        "flexCode": 45,
                        "flexPatamar": "MED",
                        "flexLimit": "FOLGAINF",
                        "flexSubsystem": "SE",
                        "flexAmount": 100.0,
                    }
                ],
                "message": "Applied 1 flexibilizations",
            }
        }
    }
