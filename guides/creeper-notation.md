# Creeper Notation

This document describes the state and action notation used by Softserve for the
game [Creeper](https://www.grahams-games.co.uk/creeper.html).

Examples of this notation in use can be found at the [UI
visualizer](https://softserve.harding.edu/ui/) and the [`/state`
API](https://softserve.harding.edu/docs#/state) endpoints.

## State Notation

The state is encoded as a string of 86 characters, divided into the following
sections:

- 49 characters representing the state of the pins
- 36 characters representing the state of the paths
- 1 character representing the next player to move

The grids are encoded top-to-bottom, left-to-right. `x` denotes the first
player, `o` denotes the second player, and `.` denotes an empty space. All
letters should be lowercase.

The pin grid does not have corners, but treat them as empty for the sake of
notation.

Thus, the [initial state](https://softserve.harding.edu/ui/) is encoded as:

\small
`.oo.xx.o.....xo.....x.......x.....ox.....o.xx.oo.o....x........................x....ox`
\normalsize

If we break this notation into the above setions and add newlines, we see it
forms two grids and a single character:

    .oo.xx.
    o.....x
    o.....x
    .......
    x.....o
    x.....o
    .xx.oo.

    o....x
    ......
    ......
    ......
    ......
    x....o

    x

## Action Notation

Actions are encoded as a string of 4 characters, which form a pair of
coordinates on the pin grid.

Columns are given a letter, and rows are given a number:

      abcdefg
    1 .oo.xx.
    2 o.....x
    3 o.....x
    4 .......
    5 x.....o
    6 x.....o
    7 .xx.oo.

All letters should be lowercase.

Actions consist of the starting and ending coordinate of the pin being moved.
For example, moving the `x` pin on a5 north one spot would be `a5a4`.

No additional notation in used for captures.

## Questions and Suggestions

If you have any questions, ambiguities, issues, or suggestions for this
notation, please [open a softserve
issue](https://github.com/harding-university/softserve/issues/new) or email
[rschneid@harding.edu](mailto:rschneid@harding.edu).
