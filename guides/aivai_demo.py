#!/usr/bin/env python3


# Released under the Unlicense (https://unlicense.org/)
# This is free and unencumbered software released into the public domain.


import random
import time

# https://requests.readthedocs.io/en/latest/
import requests


SOFTSERVE_URL = "https://softserve.harding.edu"
PLAYER_NAME = "aivai-demo-player"
PLAYER_EMAIL = "student@example.edu"


# If we have already have a token, load it
try:
    with open(f"{PLAYER_NAME}_token.txt") as f:
        token = f.read()

# If we don't have a token, get one using /player/create
except FileNotFoundError:
    # For expected fields, see:
    # https://softserve.harding.edu/docs#/player/player_create_player_create_post
    r = requests.post(
        f"{SOFTSERVE_URL}/player/create",
        json={
            "name": PLAYER_NAME,
            "email": PLAYER_EMAIL,
        },
    )
    # (throw an error if the request failed)
    r.raise_for_status()

    # Get the token out of the returned JSON
    token = r.json()["token"]

    # Save it for next time
    with open(f"{PLAYER_NAME}_token.txt", "w") as f:
        f.write(token)


# Now that we have our token, we can start the /aivai loop
while True:
    # https://softserve.harding.edu/docs#/aivai/aivai_request_aivai_play_state_post
    r = requests.post(
        f"{SOFTSERVE_URL}/aivai/play-state",
        json={
            # The mirror event makes for simple testing; see linked docs
            "event": "mirror",
            "player": PLAYER_NAME,
            "token": token,
        },
    )
    # (throw an error if the request failed)
    r.raise_for_status()

    # Check for HTTP 204, which means that no games are currently
    # waiting for our player to move; try again in a few seconds
    if r.status_code == 204:
        time.sleep(5)
        continue

    # The state we're moving from
    state = r.json()["state"]
    # An identifier that needs to be returned to /aivai/submit-action
    action_id = r.json()["action_id"]

    print(f"state:\t{state}")

    # For demo purposes, we're going to grab a random action using the
    # /state/{state}/actions endpoints--you should call your AI here
    r = requests.get(f"{SOFTSERVE_URL}/state/{state}/actions")
    actions = r.json()["actions"]
    action = random.choice(actions)
    # Simulate some thinking time before responding to the server
    time.sleep(2)

    print(f"action:\t{action}")

    # Send that action back to Softserve with /aivai/submit-action
    # https://softserve.harding.edu/docs#/aivai/aivai_submit_action_aivai_submit_action_post
    r = requests.post(
        f"{SOFTSERVE_URL}/aivai/submit-action",
        json={
            "action": action,
            "action_id": action_id,
            "player": PLAYER_NAME,
            "token": token,
        },
    )
    # (throw an error if the request failed)
    r.raise_for_status()
