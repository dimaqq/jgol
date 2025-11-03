"""Test it."""

# import concurrent.futures
import json
import re
from types import MappingProxyType
from typing import Mapping, NewType, cast

import ops
import ops.testing
import pytest
from ops.testing import Context, State, Relation

from charm import JGOLCoordinatorCharm

JSON = NewType("JSON", str)

# 3x3 map:
# --------
# 0 1 2
# 3 4 5
# 6 7 8

MAP_3X3 = {
    "app/0": ["app/1", "app/3", "app/4"],
    "app/1": ["app/0", "app/2", "app/3", "app/4", "app/5"],
    "app/2": ["app/1", "app/4", "app/5"],
    "app/3": ["app/0", "app/1", "app/4", "app/6", "app/7"],
    "app/4": ["app/0", "app/1", "app/2", "app/3", "app/5", "app/6", "app/7", "app/8"],
    "app/5": ["app/1", "app/2", "app/4", "app/7", "app/8"],
    "app/6": ["app/3", "app/4", "app/7"],
    "app/7": ["app/3", "app/4", "app/5", "app/6", "app/8"],
    "app/8": ["app/4", "app/5", "app/7"],
}


def test_boot():
    """Leader with blank config, etc."""
    rel = Relation(endpoint="world", id=1, local_app_data={})
    ctx = Context(JGOLCoordinatorCharm, app_name="app", unit_id=0)
    state = State(leader=True, relations={rel})
    state = ctx.run(ctx.on.update_status(), state)
    assert state.app_status == ops.WaitingStatus("Resetting... [.]")
    assert state.unit_status == ops.ActiveStatus()
