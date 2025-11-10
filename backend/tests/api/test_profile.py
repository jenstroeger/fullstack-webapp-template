"""Collection of tests for the ``/profile`` endpoint."""

# Copyright (c) 2025-2025
# This code is licensed under MIT license, see LICENSE.md for details.

# flake8: noqa: D103
# pylint: disable=missing-function-docstring

import datetime

import pytest
import requests
from faker import Faker

# Glogal ordering of test modules.
pytestmark = pytest.mark.order(3)


# Resource under test.
_URL = "http://localhost:3000/profile"


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


def test_get_no_bearer() -> None:
    response = requests.get(_URL, timeout=0.5)
    assert response.status_code == 401
    assert response.json()["code"] == "42501"  # insufficient privileges


def test_invalid_verb(faker: Faker, bearer: str) -> None:
    response = requests.post(_URL, headers={"Authorization": bearer}, timeout=0.5)
    assert response.status_code == 400
    assert response.json()["code"] == "PGRST102"  # Empty or invalid json

    response = requests.post(
        _URL, data={"first_name": faker.first_name()}, headers={"Authorization": bearer}, timeout=0.5
    )
    assert response.status_code == 403
    assert response.json()["code"] == "42501"  # permission denied for view profile

    response = requests.put(_URL, headers={"Authorization": bearer}, timeout=0.5)
    assert response.status_code == 400
    assert response.json()["code"] == "PGRST102"  # Empty or invalid json

    response = requests.put(
        _URL, data={"first_name": faker.first_name()}, headers={"Authorization": bearer}, timeout=0.5
    )
    assert response.status_code == 405
    assert response.json()["code"] == "PGRST105"  # Filters must include all and only primary key columns ...

    response = requests.delete(_URL, headers={"Authorization": bearer}, timeout=0.5)
    assert response.status_code == 403
    assert response.json()["code"] == "42501"  # permission denied for view profile


def test_get(bearer: str) -> None:
    response = requests.get(_URL, headers={"Authorization": bearer}, timeout=0.5)
    assert response.status_code == 200

    (profile,) = response.json()
    assert "email" in profile
    assert "first_name" in profile
    assert "last_name" in profile

    response = requests.get(
        _URL, headers={"Authorization": bearer, "Accept": "application/vnd.pgrst.object+json"}, timeout=0.5
    )
    assert response.status_code == 200

    profile = response.json()
    assert "email" in profile
    assert "first_name" in profile
    assert "last_name" in profile


def test_patch_no_payload(bearer: str) -> None:
    response = requests.patch(_URL, headers={"Authorization": bearer}, timeout=0.5)
    assert response.status_code == 400
    assert response.json()["code"] == "PGRST102"


def test_patch_invalid_payload(faker: Faker, bearer: str) -> None:
    response = requests.patch(_URL, data={"some": "data"}, headers={"Authorization": bearer}, timeout=0.5)
    assert response.status_code == 400
    assert response.json()["code"] == "PGRST204"

    response = requests.patch(
        _URL, data={"first_name": faker.random_int()}, headers={"Authorization": bearer}, timeout=0.5
    )
    assert response.status_code == 204
    assert response.content == b""

    response = requests.patch(_URL, data={"email": faker.email()}, headers={"Authorization": bearer}, timeout=0.5)
    assert response.status_code == 403
    assert response.json()["code"] == "42501"  # permission denied for view profile

    response = requests.patch(
        _URL, data={"created_at": faker.date_time(tzinfo=datetime.UTC)}, headers={"Authorization": bearer}, timeout=0.5
    )
    assert response.status_code == 403
    assert response.json()["code"] == "42501"  # permission denied for view profile


def test_patch(faker: Faker, bearer: str) -> None:
    response = requests.patch(
        _URL, data={"first_name": None, "last_name": None}, headers={"Authorization": bearer}, timeout=0.5
    )
    assert response.status_code == 204

    response = requests.patch(
        _URL,
        data={"first_name": faker.first_name(), "last_name": faker.last_name()},
        headers={"Authorization": bearer},
        timeout=0.5,
    )
    assert response.status_code == 204
