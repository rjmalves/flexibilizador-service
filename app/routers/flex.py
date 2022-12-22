from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.internal.httpresponse import HTTPResponse
from app.models.flexibilizationrequest import FlexibilizationRequest
from app.models.flexibilizationresponse import FlexibilizationResponse

from app.adapters.uriparserrepository import AbstractURIParsingRepository
from app.services.unitofwork import factory as uow_factory

from app.internal.dependencies import uriParser
from app.adapters.flexibilizationrepository import factory as flex_factory

router = APIRouter(
    prefix="/flex",
    tags=["flex"],
)


responses = {
    201: {"detail": ""},
    202: {"detail": ""},
    404: {"detail": ""},
    500: {"detail": ""},
    503: {"detail": ""},
}


@router.post(
    "/",
    response_model=FlexibilizationResponse,
    responses=responses,
)
async def flexibilize(
    req: FlexibilizationRequest,
    uriParser: AbstractURIParsingRepository = Depends(uriParser),
):
    path = uriParser.parse(req.id)
    flex_repo = flex_factory(req.program)
    if isinstance(path, HTTPResponse):
        raise HTTPException(status_code=path.code, detail=path.detail)
    uow = uow_factory("FS", path)
    result = await flex_repo.flex([], uow)
    if isinstance(result, HTTPResponse):
        raise HTTPException(status_code=result.code, detail=result.detail)
    else:
        return FlexibilizationResponse(result=result)
