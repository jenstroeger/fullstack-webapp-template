![license](https://img.shields.io/badge/license-MIT-blue) [![semver](https://img.shields.io/badge/semantic%20versioning-2.0.0-yellow)](https://semver.org/) [![conventional-commits](https://img.shields.io/badge/conventional%20commits-1.0.0-yellow)](https://www.conventionalcommits.org/en/v1.0.0/)

# A Full-Stack Web Application Template

This repository is an opinionated implementation of a full-stack web application template.

## Prerequisites

The following tools should be available on your machine to get started:

- [GNU make](https://www.gnu.org/software/make/) and related GNU tools to run the Makefiles which, in turn, orchestrate checking, building, testing, and deploying the entire software stack.
- [pre-commit](https://pre-commit.com/) to manage various [git hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks) to enforce coding standards.
- [commitizen](https://commitizen-tools.github.io/commitizen/) manages automatic version bumps for _semantic versioning_ based on the _conventional commit messages_ in this repository.
- [Docker](https://www.docker.com/) to build and deploy application containers.

## Quick start

After checking out this repository the following steps should stand up the entire stack locally on your machine:

```
make init
. backend/.venv/bin/activate
make setup
make build
make compose-up
```

Now navigate to [localhost:3001](http://localhost:3001/) to read the interactive Swagger documentation for the API…

## Architecture

There are three main componenst in this repository, structured into three directories:

- **Frontend**: TBD. For more details see [here](frontend/README.md).
- **Backend**: the backend is composed of a [PostgREST](https://github.com/PostgREST/postgrest) web server, a message queue based on Postgres, and asynchronous workers implemented in Python using the [Dramatiq](https://github.com/Bogdanp/dramatiq) framework. For more details see [here](backend/README.md).
- **Infrastructure**: both frontend and backend build Docker images which are then orchestrated using [Docker Compose](https://docs.docker.com/compose/). For more details see [here](infra/README.md).

## Development

All of the development — checking and compiling code, running tests, and building Docker images — is managed by `make` and each component has its own Makefile.

To set up this project for development, follow these steps:

1. `make init`: initialize both frontend and backend.
2. `make setup`: set up and install all tools and packages to build and test and run.
3. `make check`: run code checks for both frontend and backend.
4. `make test`: run all tests.
5. `make build`: build both frontend and backend packages, then build the Docker images.
6. `make docs`: generate documentation.
7. `make compose-up` and `make compose-down` stand up and tear down the application locally.
8. `make clean` and `make nuke` reset the build environment and remove all generated artifacts.

More details can be found in the documentation for each of the components.
