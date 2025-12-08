from os import environ

import django
from fastapi import FastAPI, HTTPException, Path
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# We have to call this before our submodules can import Django models
django.setup()

from .routers import aivai, state
from .util import engine, get_actions


ui = environ.get("SOFTSERVE_UI")
ui_path = environ.get("SOFTSERVE_UI_PATH", "/")


app = FastAPI(
    title="Softserve",
    version="0.1.0a",
    description="""
# Overview
Softserve is an integration system for Harding University software
development capstone projects. Student projects interact with the system
using this API.

There are two versions of these docs:
1. [Swagger UI](docs)
2. [ReDoc](redoc)

Students should freely [create issues](https://github.com/harding-university/softserve/issues) for any problems, questions, or feature requests.

To get oriented, here are some things to try:

1. Get the initial state from `/state/initial` and walk through a game
from there using `/state/actions` and `/state/act`
2. Walk through the loop described in the `aivai` section.

""",
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

if ui:
    app.mount(ui_path, StaticFiles(directory=ui, html=True))
