"""Base configurations for all tests."""

# Copyright (c) 2025-2025
# This code is licensed under MIT license, see LICENSE.md for details.

import random

import pytest

# Import the broker module which imports the actor module to make sure
# that all code is loaded to coverage tracking.
import template_jobs.broker  # noqa: F401 # pylint: disable=unused-import


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale() -> list[str]:
    """Override the Faker fixture’s default locale."""
    return ["en-US"]


@pytest.fixture(autouse=True)
def faker_seed() -> float:
    """Override the Faker fixture’s default RNG seed."""
    return random.random()  # nosec B311
