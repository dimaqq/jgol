"""Test it."""

import json

import ops
import pytest
from ops.testing import Context, PeerRelation, State

from charm import JGOLPeerCharm

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
    ctx = Context(JGOLPeerCharm, app_name="app")
    state = State(leader=True, relations={rel})
    state = ctx.run(ctx.on.update_status(), state)
    assert state.app_status == ops.BlockedStatus("AssertionError('Waiting for the initial state')")
    assert state.unit_status == ops.BlockedStatus("KeyError('run')")


def test_boot_unit():
    """Leader with blank config, etc."""
    rel = PeerRelation(endpoint="world", id=1, local_app_data={}, peers_data={})
    ctx = Context(JGOLPeerCharm, app_name="app")
    state = State(relations={rel})
    state = ctx.run(ctx.on.update_status(), state)
    assert state.unit_status == ops.BlockedStatus("KeyError('run')")


def test_init_unit(board):
    """Leader with blank config, etc."""
    rel = PeerRelation(
        endpoint="world",
        id=1,
        local_app_data={"run": "false", "round": "0", "init": '"000111000"', "map": board},
        peers_data={},
    )
    ctx = Context(JGOLPeerCharm, app_name="app")
    state = State(relations={rel})
    state = ctx.run(ctx.on.update_status(), state)
    assert state.unit_status == ops.ActiveStatus()
    rel = state.get_relation(1)
    assert rel.local_unit_data == {"0": "0"}
