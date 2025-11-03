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
        framework.observe(self.on.collect_unit_status, self.cell)

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
            assert world, "waiting for relation"

            # Determine which application databag contains the coordinator data.
            required = {"round", "map", "board"}
            app_bag = world.data[self.app]
            if not required.issubset(app_bag.keys()):
                # Fallback: look for a remote application databag that has all required keys.
                for entity, bag in world.data.items():
                    if isinstance(entity, ops.Application) and entity != self.app:
                        if required.issubset(bag.keys()):
                            app_bag = bag
                            break
            # Parse coordinator data (may still raise KeyError -> handled below)
            round_: int = json.loads(app_bag["round"])
            neighbours: dict[str, list[str]] = json.loads(app_bag["map"])
            board: str = app_bag["board"]
            if self.unit.name not in neighbours:
                self.unit.status = ops.ActiveStatus("unused")
                return
            own_index = list(neighbours).index(self.unit.name)
            live = int(board[own_index])

            neighbours_alive = sum(
                int(board[list(neighbours).index(n)]) for n in neighbours[self.unit.name]
            )
            if live and neighbours_alive in (2, 3):
                next_live = 1
            elif live:
                next_live = 0
            elif neighbours_alive == 3:
                next_live = 1
            else:
                next_live = 0

            world.data[self.unit]["value"] = json.dumps(next_live)
            world.data[self.unit]["round"] = json.dumps(round_)

            self.unit.status = ops.ActiveStatus()
        except Exception as e:
            self.unit.status = ops.WaitingStatus(repr(e))


if __name__ == "__main__":
    ops.main(JGOLWorkerCharm)
