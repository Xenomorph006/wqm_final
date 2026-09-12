from fastapi import FastAPI

from app.api.routes import (
    router,
)


app = FastAPI(

    title=(
        "Water Quality Agent API"
    ),

    description=(
        "AI Agent API for water "
        "quality monitoring, prediction "
        "and hardware control"
    ),

    version="1.0.0",

)


app.include_router(

    router,

    prefix="/api/v1",

)


@app.get("/")
def root():

    return {

        "message":
            "Water Quality Agent API",

        "status":
            "running",

    }