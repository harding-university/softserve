from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel

from .routers import aivai, state
from .util import engine, get_actions


app = FastAPI(
    title="Softserve",
    version="0.1.0a",
    description="""""",
    openapi_tags=[
        {
            "name": "aivai",
            "description": """
AI versus AI interface. **Right now everything here is a stub and can be
safely tested against.**

The general usage is:

1.  Call `/aivai/play-state` to get a state and uuid
2.  Calculate which action to play on that state
3.  Submit that action and the uuid to `/aivai/submit-action`
4.  Go to step 1

During a tournament, your projects will run this loop while Softserve
coordinates the games being played.

""",
        },
        {
            "name": "state",
            "description": """
Basic operations on states and state transitions.

**This is abstract and unrelated to any actual games.** It may be useful
for debugging issues in your game engine or Softserve's game engine.

Every endpoint under this returns a `log` field with informational
output from the underlying game engine.
""",
        },
    ],
)


app.include_router(aivai.router)
app.include_router(state.router)
