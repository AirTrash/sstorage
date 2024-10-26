from dotenv import load_dotenv
load_dotenv(".env")
import os
from fastapi import FastAPI

from restAPI.routers import all_routers

app = FastAPI()

for router in all_routers:
    app.include_router(router)



@app.get("/")
async def root():
    return {"message": "документация к API /docs"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        reload=True,
        ssl_keyfile=os.getenv("FASTAPI_KEY"),
        ssl_certfile=os.getenv("FASTAPI_CERT"),
    )