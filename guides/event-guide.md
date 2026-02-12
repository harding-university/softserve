# Custom Event Guide

This guide explains how to use Softserve's event API to create custom
tournaments. This is not a requirement for the class, but it can help you
develop and assess your AIs. For example, you can play different versions of
your AI against itself, or play another group's AI in an exhibition match.

## Creating a custom event

The key endpoint for this is
[`/event/create`](https://softserve.harding.edu/docs#/event/event_create_event_create_post).
POST to it as documented, including a list of player names to include in the
tournament and the number of game pairs for each matchup to play. You can also
include an event name, or omit the name field to have a generic name generated.

The request returns the event name (necessary for you to know the name if you
didn't specify one) and a token for use with `/event/data`. You should mostly be
able to ignore the token, because Softserver will also email a dashboard link
(with the token) to every event player's address. Use that link to access the
event dashboard and follow game results. 

## The `random` player

The player `random` can be included in events. Its moves are entirely random
across the possible actions from a state. It is useful to test against as a
baseline sanity check that your AI is making better-than-random moves.

## Wildcard events

If you work with many events, you may find it cumbersome to start new clients
for each event. If you pass an asterisk (`*`) to the `event` field of
`/aivai/play-state`, your client will be given states from any event its player
is part of. This will let you leave a client running while you create events for
it, e.g. having your current-best version running while testing modified
versions against it.

## Issues and feature requests

If you have any issues using the event creation API or a request for a feature
<a href="https://github.com/harding-university/softserve/issues/new">create an
issue</a> or email <a
href="mailto:rschneid@harding.edu">rschneid@harding.edu</a>.</p>
