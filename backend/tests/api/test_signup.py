"""Collection of tests for the ``/rpc/signup`` endpoint."""

# Copyright (c) 2025-2025
# This code is licensed under MIT license, see LICENSE.md for details.

# flake8: noqa: D103
# pylint: disable=missing-function-docstring

import pytest
import requests
from faker import Faker

# Glogal ordering of test modules.
pytestmark = pytest.mark.order(1)

# Resource under test.
_URL = "http://localhost:3000/rpc/signup"


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


def test_invalid_email() -> None:
    pass


def test_invalid_password() -> None:
    pass


def test_duplicate_email() -> None:
    pass


def test_valid(faker: Faker) -> None:
    response = requests.post(_URL, data={"email": faker.email(), "password": faker.password()}, timeout=0.5)
    assert response.status_code == 200
    assert "created_at" in response.json()
    assert "email" in response.json()
