from fastapi import APIRouter


router = APIRouter(
    prefix="/test",
    tags=["test"],
    responses={404: {"description": "Not Found"}}
)


@router.get("/")
async def root():
    return {"message": "вы вошли в /test/"}


@router.get("/test")
async def test():
    return {"message": "вы вошли в /test/test"}
