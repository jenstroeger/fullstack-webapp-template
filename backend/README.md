# Backend

The backend folder structure is heavily inspired by the [python-package-template](https://github.com/jenstroeger/python-package-template), also an opinionated template that sets the foundation for a Python package.

## Architecture

TODO

## Developing

Ensure that the code is somewhat clean and healthy:

```
make check
```

In order to run and test the backend’s asynchronous jobs, both Alembic migrations and Dramatiq actors should run on the host instead of the container. To achieve that, run `make compose-up-develop` in a terminal which

- mounts the hosts `backend/alembic/versions/` folder into the Alembic container and runs this host migrations against the containered Postgres database; and
- does not run the Dramatiq container.

Next, run Dramatiq in another terminal:
```
DRAMATIQ_SQLA_URL=postgresql://dramatiq:dramatiq@localhost:5432/template_db dramatiq --verbose --processes 1 --threads 1 template_jobs.broker
```

which launches the message broker and workers, waiting for a message on the queue.

With the development containers running and the Dramatiq broker ready, run the tests:

```
make test
```

which runs all tests, collect statement and branch coverage, various statistics, and then dump the results of the test run.
