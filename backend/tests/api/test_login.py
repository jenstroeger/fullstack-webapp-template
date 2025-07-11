"""Collection of tests for the ``/rpc/login`` endpoint."""

# Copyright (c) 2025-2025
# This code is licensed under MIT license, see LICENSE.md for details.

# flake8: noqa: D103
# pylint: disable=missing-function-docstring

import pytest
import requests
from faker import Faker

# Glogal ordering of test modules.
pytestmark = pytest.mark.order(2)


# Resource under test.
_URL = "http://localhost:3000/rpc/login"


@pytest.fixture(name="signup")
def _signup(faker: Faker) -> tuple[str, str]:
    email = faker.email()
    password = faker.password()

    response = requests.post(
        "http://localhost:3000/rpc/signup", data={"email": email, "password": password}, timeout=0.5
    )
    assert response.status_code == 200

    return email, password


def test_invalid_no_payload() -> None:
    response = requests.post(_URL, data={}, timeout=0.5)
    assert response.status_code == 404
    assert response.json()["code"] == "PGRST202"


def test_invalid_incomplete_payload(faker: Faker) -> None:
    response = requests.post(_URL, data={"email": faker.email()}, timeout=0.5)
    assert response.status_code == 404
    assert response.json()["code"] == "PGRST202"

    response = requests.post(_URL, data={"password": faker.password()}, timeout=0.5)
    assert response.status_code == 404
    assert response.json()["code"] == "PGRST202"


def test_email_not_exist() -> None:
    pass


def test_wrong_password() -> None:
    pass


def test_valid(signup: tuple[str, str]) -> None:
    email, password = signup
    response = requests.post(_URL, data={"email": email, "password": password}, timeout=0.5)
    assert response.status_code == 200
    assert "token" in response.json()


# TODO expired token
# TODO invalid token
