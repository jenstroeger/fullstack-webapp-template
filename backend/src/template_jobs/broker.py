"""Asynchronous `Dramatiq <https://github.com/Bogdanp/dramatiq>`_ workers."""

# Copyright (c) 2025-2025
# This code is licensed under MIT license, see LICENSE.md for details.

import os

import dramatiq
import dramatiq_pg

# Create the Postgres Broker instance that manages reading from and writing
# to the message queue (which is implemented by PG).
dramatiq.set_broker(
    dramatiq_pg.PostgresBroker(url=os.environ["DRAMATIQ_SQLA_URL"], results=True, schema="data", prefix="dramatiq_")
)

# Importing the actor module registers the Dramatiq actors with the broker.
from . import actors  # noqa: F401,E402 # pylint: disable=unused-import,wrong-import-position
