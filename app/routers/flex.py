from fastapi import APIRouter, HTTPException

from app.adapters.flexibilizationrepository import factory as flex_factory
from app.adapters.s3_repository import get_s3_repository
from app.internal.exceptions import (
    ArtifactNotFoundError,
    FlexibilizadorException,
    NoInfeasibilitiesError,
    ParseError,
)
from app.internal.httpresponse import HTTPResponse
from app.models.errors import ErrorCode, ErrorResponse
from app.models.flexibilizationrequest import FlexibilizationRequest
from app.models.flexibilizationresponse import FlexibilizationResponse
from app.models.flexibilizationresult import FlexibilizationResult
from app.services.unitofwork import S3UnitOfWork
from app.utils.log import Log

router = APIRouter(
    prefix="/flex",
    tags=["flexibilization"],
)


@router.post(
    "/",
    response_model=FlexibilizationResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        404: {"model": ErrorResponse, "description": "Artifacts not found"},
        422: {
            "model": ErrorResponse,
            "description": "Parse or processing error",
        },
        500: {"model": ErrorResponse, "description": "Internal error"},
    },
    summary="Apply flexibilization to DECOMP execution",
    description="""
    Applies flexibilization rules to a DECOMP execution that has
    encountered infeasibilities.

    Downloads artifacts from S3, processes infeasibilities, modifies
    constraint limits, and uploads the flexibilized deck back to S3.
    """,
)
async def flexibilize(req: FlexibilizationRequest) -> FlexibilizationResponse:
    """
    Apply flexibilization to a DECOMP execution.

    Args:
        req: Flexibilization request with S3 location

    Returns:
        FlexibilizationResponse with results and output location

    Raises:
        HTTPException: Various status codes based on error type
    """
    Log.log().info(
        f"Flexibilization request: bucket={req.bucket}, "
        f"hash={req.execution_hash}, program={req.program}"
    )

    try:
        s3_repo = get_s3_repository()
        output_prefix = req.output_prefix or "ingest"

        async with S3UnitOfWork(
            s3_repo=s3_repo,
            bucket=req.bucket,
            execution_hash=req.execution_hash,
            output_prefix=output_prefix,
        ) as uow:
            # Get appropriate flexibilization repository
            flex_repo = flex_factory(req.program)

            # Perform flexibilization
            results = await flex_repo.flex([], uow)

            # Check if results is an error response
            if isinstance(results, HTTPResponse):
                raise HTTPException(
                    status_code=results.code,
                    detail=ErrorResponse(
                        error_code=ErrorCode.FLEXIBILIZATION_ERROR,
                        message=results.detail,
                        details=None,
                    ).model_dump(),
                )

            # results is now guaranteed to be list[FlexibilizationResult]
            flex_results: list[FlexibilizationResult] = results

            Log.log().info(
                f"Flexibilization complete: {len(flex_results)} flexibilizations applied"
            )

            return FlexibilizationResponse(
                success=True,
                execution_hash=req.execution_hash,
                output_key=uow.output_key,
                flexibilizations=flex_results,
                message=f"Applied {len(flex_results)} flexibilizations",
            )

    except ArtifactNotFoundError as e:
        Log.log().warning(f"Artifact not found: {e.message}")
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                error_code=ErrorCode.ARTIFACT_NOT_FOUND,
                message=e.message,
                details=e.details,
            ).model_dump(),
        )

    except ParseError as e:
        Log.log().warning(f"Parse error: {e.message}")
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                error_code=ErrorCode.PARSE_ERROR,
                message=e.message,
                details=e.details,
            ).model_dump(),
        )

    except NoInfeasibilitiesError as e:
        Log.log().info(f"No infeasibilities found: {e.message}")
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                error_code=ErrorCode.NO_INFEASIBILITIES,
                message=e.message,
                details=e.details,
            ).model_dump(),
        )

    except FlexibilizadorException as e:
        Log.log().error(f"Flexibilization error: {e.message}", exc_info=True)
        raise HTTPException(
            status_code=e.http_status,
            detail=ErrorResponse(
                error_code=ErrorCode(e.error_code),
                message=e.message,
                details=e.details,
            ).model_dump(),
        )

    except Exception as e:
        Log.log().exception("Unexpected error during flexibilization")
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred",
                details={"error": str(e)},
            ).model_dump(),
        )
