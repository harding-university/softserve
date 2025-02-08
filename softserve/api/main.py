from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

from .routers import aivai, state
from .util import engine, get_actions


app = FastAPI(
    title="Softserve",
    description="""""",
    openapi_tags=[
        {
            "name": "aivai",
            "description": "AI versus AI interface.",
        },
        {
            "name": "state",
            "description": "Basic operations on states, including transitions. For convenience and testing.",
        },
    ],
)


app.include_router(aivai.router)
app.include_router(state.router)
