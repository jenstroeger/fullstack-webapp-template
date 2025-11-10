"""Collection of tests to exercise the message queue.."""

# Copyright (c) 2025-2025
# This code is licensed under MIT license, see LICENSE.md for details.

# flake8: noqa: D103
# pylint: disable=missing-function-docstring

import time

import pytest
import requests
from faker import Faker

# Glogal ordering of test modules.
pytestmark = pytest.mark.order(4)


@pytest.fixture(name="bearer")
def _signup_login(faker: Faker) -> str:
    email = faker.email()
    password = faker.password()

    response = requests.post(
        "http://localhost:3000/rpc/signup", data={"email": email, "password": password}, timeout=0.5
    )
    assert response.status_code == 200
    response = requests.post(
        "http://localhost:3000/rpc/login", data={"email": email, "password": password}, timeout=0.5
    )
    assert response.status_code == 200

    json = response.json()
    return f"Bearer {json['token']}"


def test_job(bearer: str) -> None:

    # Post to the `job` endpoint which pushes a message into the queue
    # and thus triggers the async worker. The immediate response from
    # the web server is the job's id.
    response = requests.post(
        "http://localhost:3000/rpc/job",
        headers={"Authorization": bearer, "Prefer": "return=representation"},
        timeout=0.5,
    )
    assert response.status_code == 200  # TODO Return 201?

    # Get the job id from the response.
    message_id = response.json()["job_id"]

    # Get all current jobs from the server, there should be exactly
    # one for this user.
    response = requests.get("http://localhost:3000/job", headers={"Authorization": bearer}, timeout=0.5)
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Now poll the job with the above id until a result becomes available.
    for _ in range(5):
        response = requests.get(
            f"http://localhost:3000/job?job_id=eq.{message_id}",
            headers={"Authorization": bearer, "Accept": "application/vnd.pgrst.object+json"},
            timeout=0.5,
        )
        assert response.status_code == 200

        # Once the job's `state` is done, its result is available.
        payload = response.json()
        if payload["state"] == "done":
            assert payload["result"] == "done"
            break

        # The job's not yet done, so wait and poll again.
        time.sleep(0.5)

    else:
        pytest.fail("Job did not produce a result before timeout!")


# TODO multiple users pushing jobs, can see only their own
