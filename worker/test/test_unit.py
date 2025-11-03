from __future__ import annotations

import json

import pytest
from ops.testing import Context, Relation, State

from charm import JGOLWorkerCharm

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
def ctx() -> Context[JGOLWorkerCharm]:
    return Context(JGOLWorkerCharm, app_name="app", unit_id=4)


def test_reset(ctx: Context[JGOLWorkerCharm]):
    """Test that the charm can be instantiated and reset without errors."""
    rel = Relation(
        endpoint="world",
        remote_app_name="coordinator",
        id=1,
        remote_app_data={
            "map": json.dumps(MAP_3X3),
        },
    )
    state = State(relations={rel})
    state = ctx.run(ctx.on.relation_changed(rel), state)
    rel = state.get_relation(rel.id)


def test_worker_processes_state(ctx: Context):
    """Test that worker processes state and updates cell."""
    rel = Relation(
        endpoint="world",
        remote_app_name="coordinator",
        id=1,
        remote_app_data={
            "round": "0",
            "map": json.dumps(MAP_3X3),
            "board": "010110010",  # 3x3 board state as string
        },
    )
    state = State(relations={rel})
    state = ctx.run(ctx.on.relation_changed(rel), state)
    rel = state.get_relation(rel.id)
    # Worker charm writes to local unit data with "value" and "round" keys
    assert "value" in rel.local_unit_data
    assert "round" in rel.local_unit_data


def test_worker_without_map(ctx: Context):
    """Test that worker handles missing map gracefully."""
    rel = Relation(
        endpoint="world", remote_app_name="coordinator", id=1, remote_app_data={}
    )
    state = State(relations={rel})
    state = ctx.run(ctx.on.relation_changed(rel), state)
    rel = state.get_relation(rel.id)


def test_worker_with_incomplete_state(ctx: Context):
    """Test that worker handles incomplete state data."""
    rel = Relation(
        endpoint="world",
        remote_app_name="coordinator",
        id=1,
        remote_app_data={
            "map": json.dumps(MAP_3X3),
            "app/0": "1",
            "app/1": "0",
        },
    )
    state = State(relations={rel})
    state = ctx.run(ctx.on.relation_changed(rel), state)
    rel = state.get_relation(rel.id)
