import os
import pathlib

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.internal.exceptions import FlexibilizadorException
from app.internal.settings import Settings
from app.models.errors import ErrorCode, ErrorResponse
from app.routers import flex, health
from app.utils.log import Log

BASEDIR = pathlib.Path().resolve()
os.environ["APP_INSTALLDIR"] = os.path.dirname(os.path.abspath(__file__))
load_dotenv(
    pathlib.Path(os.getenv("APP_INSTALLDIR")).joinpath(".env"),
    override=True,
)
Settings.read_environments()

app = FastAPI(
    title="Flexibilizador Service",
    description="REST API for applying flexibilizations to DECOMP executions with infeasibilities",
    version="2.0.0",
    root_path=Settings.root_path,
)


@app.exception_handler(FlexibilizadorException)
async def flexibilizador_exception_handler(
    request: Request,
    exc: FlexibilizadorException,
) -> JSONResponse:
    """Handle custom FlexibilizadorException errors."""
    Log.log().error(
        f"{exc.error_code}: {exc.message}", extra={"details": exc.details}
    )
    return JSONResponse(
        status_code=exc.http_status,
        content=ErrorResponse(
            error_code=ErrorCode(exc.error_code),
            message=exc.message,
            details=exc.details if exc.details else None,
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle unhandled exceptions."""
    Log.log().exception("Unhandled exception")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error_code=ErrorCode.INTERNAL_ERROR,
            message="An unexpected error occurred",
            details=None,
        ).model_dump(),
    )


app.include_router(health.router)
app.include_router(flex.router)

if __name__ == "__main__":
    Log.configure_logging(BASEDIR)
    uvicorn.run(
        "main:app", host=Settings.host, port=Settings.port, log_level="info"
    )
