"""Test it."""

import json
from typing import Mapping, NewType, cast

import ops
import ops.testing
import pytest
from ops.testing import Context, PeerRelation, State

from charm import JGOLPeerCharm

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


@pytest.fixture
def board():
    return json.dumps(MAP_3X3)


def test_boot():
    """Leader with blank config, etc."""
    rel = PeerRelation(endpoint="world", id=1, local_app_data={}, peers_data={})
    ctx = Context(JGOLPeerCharm, app_name="app", unit_id=0)
    state = State(leader=True, relations={rel})
    state = ctx.run(ctx.on.update_status(), state)
    assert state.app_status == ops.BlockedStatus(
        "AssertionError('Waiting for the initial state')"
    )
    assert state.unit_status == ops.BlockedStatus("KeyError('run')")


def test_boot_unit():
    """Leader with blank config, etc."""
    rel = PeerRelation(endpoint="world", id=1, local_app_data={}, peers_data={})
    ctx = Context(JGOLPeerCharm, app_name="app", unit_id=1)
    state = State(relations={rel})
    state = ctx.run(ctx.on.update_status(), state)
    assert state.unit_status == ops.BlockedStatus("KeyError('run')")


def test_init_unit(board):
    """Leader with blank config, etc."""
    rel = PeerRelation(
        endpoint="world",
        id=1,
        local_app_data={
            "run": "false",
            "round": "0",
            "init": '"000111000"',
            "map": board,
        },
        peers_data={},
    )
    ctx = Context(JGOLPeerCharm, app_name="app", unit_id=1)
    state = State(relations={rel})
    state = ctx.run(ctx.on.update_status(), state)
    assert state.unit_status == ops.ActiveStatus()
    rel = state.get_relation(1)
    assert rel.local_unit_data == {"0": "0"}


def excercise():
    init = "000111000"
    local_app_data={
        "run": "false",
        "round": "0",
        "init": json.dumps(init),
        "map": json.dumps(MAP_3X3),
    }
    # varies by unit
    local_unit_data={i: {} for i in range(9)}
    peers_data={f"app/{i}": {} for i in range(9)}

    for unit in range(9):
        a, b = step(unit, local_app_data, local_unit_data[i], peers_data)

def step(
    unit_id: int,
    local_app_data: Mapping[str, JSON],
    local_unit_data: Mapping[str, JSON],
    peers_data: Mapping[str, JSON],
) -> tuple[dict[str, str] | None, dict[str, str]]:
    is_leader = not unit_id
    rel = PeerRelation(
        endpoint="world",
        id=1,
        peers_data=cast(dict[ops.testing.UnitID, dict[str, str]], peers_data),
    )
    ctx = Context(JGOLPeerCharm, app_name="app", unit_id=unit_id)
    state = State(relations={rel}, leader=is_leader)
    state = ctx.run(ctx.on.update_status(), state)
    rel = state.get_relation(1)
    app_data = rel.local_app_data if is_leader else None
    unit_data = rel.local_unit_data
    return app_data, unit_data
