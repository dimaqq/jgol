#!/usr/bin/env python3
# Copyright 2025 dima.tisnek@canonical.com
# See LICENSE file for licensing details.
"""Juju's Game of Life."""

import json

import ops


class JGOLWorkerCharm(ops.CharmBase):
    """Juju's Game of Life."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on["world"].relation_joined, self.cell)
        framework.observe(self.on["world"].relation_changed, self.cell)
        framework.observe(self.on["world"].relation_departed, self.cell)

    def cell(self, _event: ops.EventBase):
        """Update this cell based on neighbours.

        Game of Life operates in lock-step.
        We decompose individual cell logic as follows:
            app = {"round": 42}
            n1 = {"42": 0}
            ...          ------->
            me = {"42": 1, "43": 0}

        * delete any outdated rounds
        * keep current round as is
        * post next round when all inputs are ready
        """
        try:
            world = self.model.get_relation("world")
            assert world, "waiting for peer relation"

            round_: int = json.loads(world.data[world.app]["round"])
            neighbours: dict[str, list[str]] = json.loads(world.data[world.app]["map"])
            board: str = world.data[world.app]["board"]

            if self.unit.name not in neighbours:
                self.unit.status = ops.ActiveStatus("unused")
                return

            own_index = list(neighbours).index(self.unit.name)
            live = int(board[own_index])
            neighbours_alive = sum(
                int(board[list(neighbours).index(n)])
                for n in neighbours[self.unit.name]
            )

            next_live = int(gol_step(bool(live), neighbours_alive))

            world.data[self.unit]["value"] = json.dumps(next_live)
            world.data[self.unit]["round"] = json.dumps(round_)
            self.unit.status = ops.ActiveStatus()
        except Exception as e:
            self.unit.status = ops.WaitingStatus(repr(e))


def gol_step(live: bool, neighbours_alive: int) -> bool:
    if live and neighbours_alive in (2, 3):
        return True
    elif live:
        return False
    elif neighbours_alive == 3:
        return True
    else:
        return False


if __name__ == "__main__":
    ops.main(JGOLWorkerCharm)
