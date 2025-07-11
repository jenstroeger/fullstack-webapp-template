"""Collection of tests for the ``job`` actor."""

# Copyright (c) 2025-2025
# This code is licensed under MIT license, see LICENSE.md for details.

# flake8: noqa: D103
# pylint: disable=missing-function-docstring, import-outside-toplevel

import dramatiq
import dramatiq.brokers.stub
import pytest

# Glogal ordering of test modules.
pytestmark = pytest.mark.order(-1)


@pytest.mark.skip("Requires: https://gitlab.com/dalibo/dramatiq-pg/-/issues/42")
def test_job(broker: dramatiq.Broker) -> None:

    # The `broker` fixture created the Broker, for which the job
    # have been registered already.
    from template_jobs.actors import job

    # Send a message to the async job, and wait for the job to finish.
    message = job.send()
    broker.join(job.queue_name)  # type: ignore[no-untyped-call]

    # Ensure the result.
    assert message.get_result() == "done"
