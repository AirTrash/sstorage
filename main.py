from dotenv import load_dotenv
load_dotenv(".env")
import os
from fastapi import Depends, FastAPI

from restAPI.routers import all_routers

app = FastAPI()

for router in all_routers:
    app.include_router(router)


from restAPI.dependencies import SessionDep


@app.get("/")
async def root(sess: SessionDep):
    print(sess)
    return {"message": "sstorage main page"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        reload=True,
        #ssl_keyfile=os.getenv("FASTAPI_KEY"),
        #ssl_certfile=os.getenv("FASTAPI_CERT"),
    )