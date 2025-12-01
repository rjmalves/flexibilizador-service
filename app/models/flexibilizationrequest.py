from pydantic import BaseModel, Field


class FlexibilizationRequest(BaseModel):
    """
    Request model for flexibilization with S3 integration.

    Contains the S3 bucket and execution hash to locate DECOMP artifacts.
    """

    bucket: str = Field(
        ...,
        description="S3 bucket name containing DECOMP artifacts",
        examples=["decomp-bucket"],
    )
    execution_hash: str = Field(
        ...,
        description="Execution identifier (hash) used in S3 key paths",
        examples=["abc123def456"],
    )
    program: str | None = Field(
        default="DECOMP",
        description="Program type (currently only DECOMP supported)",
        examples=["DECOMP"],
    )
    output_prefix: str | None = Field(
        default="ingest",
        description="S3 key prefix for output zip file",
        examples=["ingest"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "bucket": "decomp-bucket",
                "execution_hash": "abc123def456",
                "program": "DECOMP",
                "output_prefix": "ingest",
            }
        }
    }
