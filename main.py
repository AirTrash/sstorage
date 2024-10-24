from dotenv import load_dotenv
load_dotenv(".env")

from fastapi import Depends, FastAPI

from restAPI.routers import all_routers

app = FastAPI()


for router in all_routers:
    app.include_router(router)


@app.get("/")
async def root():
    return {"message": "sstorage main page"}
