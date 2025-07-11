"""Asynchronous `Dramatiq <https://github.com/Bogdanp/dramatiq>`_ workers."""

# Copyright (c) 2025-2025
# This code is licensed under MIT license, see LICENSE.md for details.

import dramatiq

# When this module run it initializes the Dramatiq actors below.
# It therefore needs a broker to register the actors with.
assert dramatiq.broker.global_broker is not None


@dramatiq.actor(queue_name="job_q", store_results=True)
def job() -> str:
    """Do a job."""
    return "done"
