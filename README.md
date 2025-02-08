# Softserve
Softseve is an integration system for Harding University software development capstone projects.

Student projects interact with the system using the API. See https://softserve.harding.edu/docs or https://softserve.harding.edu/redoc for usage information. (The API server is only available on campus, and only active during capstone sessions.)

Students should freely [create issues](https://github.com/harding-university/softserve/issues) for any problems, questions, or feature requests.

## Code
The main API code is powered by [FastAPI](https://fastapi.tiangolo.com/) and located in `softserve/api/`. The [ORM](https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping) and ancillary features are powered by [Django](https://www.djangoproject.com/).

See the `Makefile` for typical invocations and other useful commands.

Students are also free to [submit pull requests](https://github.com/harding-university/softserve/pulls) for specialized features.

The actual game logic is powered by an external project that is not published until the class is completed. For the Spring 2025 session, that project will be available [here](https://github.com/richardjs/nico).
