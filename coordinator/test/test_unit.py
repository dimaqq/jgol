"""Test it."""

import json
from typing import NewType
from unittest.mock import ANY

import ops
from ops.testing import Context, Relation, State

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
    rel = Relation(
        endpoint="world",
        id=1,
        local_app_data={},
        remote_units_data={0: {}, 1: {}, 2: {}, 3: {}},
    )
    ctx = Context(JGOLCoordinatorCharm, app_name="app", unit_id=0)
    state = State(leader=True, relations={rel})
    state = ctx.run(ctx.on.relation_changed(rel), state)
    assert state.app_status == ops.WaitingStatus("Resetting... [....]")
    rel = state.get_relation(1)
    assert rel.local_app_data == {
        "map": ANY,
        "board": "0001",
        "round": "0",
    }
    assert json.loads(rel.local_app_data["map"]) == {
        "remote/0": ["remote/1", "remote/2", "remote/3"],
        "remote/1": ["remote/0", "remote/2", "remote/3"],
        "remote/2": ["remote/0", "remote/1", "remote/3"],
        "remote/3": ["remote/0", "remote/1", "remote/2"],
    }


def test_waiting():
    """Leader with blank config, etc."""
    rel = Relation(
        endpoint="world",
        id=1,
        local_app_data={"round": "7"},
        remote_units_data={0: {"round": "6", "value": "1"},
                           1: {"round": "6"},
                           2: {"value": "0"},
                           3: {"round": "7", "value": "0"},
                           },
    )
    ctx = Context(JGOLCoordinatorCharm, app_name="app", unit_id=0)
    state = State(leader=True, relations={rel}, config={"run": True})
    state = ctx.run(ctx.on.relation_changed(rel), state)
    assert state.app_status == ops.ActiveStatus("7: [...0]")
    rel = state.get_relation(1)
    assert rel.local_app_data == {
        "map": ANY,
        "board": "0001",
        "round": "7",
    }
    assert json.loads(rel.local_app_data["map"]) == {
        "remote/0": ["remote/1", "remote/2", "remote/3"],
        "remote/1": ["remote/0", "remote/2", "remote/3"],
        "remote/2": ["remote/0", "remote/1", "remote/3"],
        "remote/3": ["remote/0", "remote/1", "remote/2"],
    }
