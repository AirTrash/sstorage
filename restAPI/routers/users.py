from fastapi import APIRouter
from restAPI.dependencies import SessionDep

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/")
async def root(session: SessionDep):
    print(session)
    return "pisa pipa"



