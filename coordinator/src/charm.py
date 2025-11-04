#!/usr/bin/env python3
# Copyright 2025 dima.tisnek@canonical.com
# See LICENSE file for licensing details.
"""Juju's Game of Life."""

import json
import logging
from typing import cast

import ops

INIT = "0001110001010101111110001110010101010101001010101000111101010111" * 99


class JGOLCoordinatorCharm(ops.CharmBase):
    """Juju's Game of Life."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on["world"].relation_joined, self.god)
        framework.observe(self.on["world"].relation_changed, self.god)
        framework.observe(self.on["world"].relation_departed, self.god)

    def god(self, _event: ops.EventBase):
        """Play God with the cells."""
        if not self.unit.is_leader():
            return

        try:
            world = self.model.get_relation("world")
            assert world, "Waiting for peer relation to come up"

            run = bool(cast(bool | None, self.config.get("run")))

            cells = sorted(unit.name for unit in world.units)
            neighbours = neighbourhood(cells)
            assert len(neighbours) <= len(INIT), "Initial map is too small"

            cells = cells[: len(neighbours)]

            curr_round = json.loads(world.data[self.app].get("round", "0"))
            board, next_round = self.board_state(world, cells, curr_round)

            # co->wo: round, map, board
            # wo->co: round, value
            world.data[self.app]["map"] = json.dumps(neighbours)
            if not run:
                # Reset the board
                world.data[self.app]["board"] = INIT[: len(neighbours)]
                world.data[self.app]["round"] = json.dumps(0)
                if next_round == 0:
                    self.app.status = ops.ActiveStatus(msg := f"Reset [{board}]")
                    logging.warning(msg)
                else:
                    # None -> inconsistent map, wait for some units
                    # int, !=0 -> map is consistent but not reset, wait for all units
                    self.app.status = ops.WaitingStatus(
                        msg := f"Resetting... [{board}]"
                    )
                    logging.warning(msg)
                    # FIXME we could compare the map to initial...
            elif next_round is not None:
                # All units completed this step, kick off the next round
                world.data[self.app]["round"] = json.dumps(next_round)
                self.app.status = ops.ActiveStatus(
                    msg := f"{curr_round}: [{board}] --> {next_round}"
                )
                world.data[self.app]["board"] = board
                world.data[self.app]["round"] = json.dumps(next_round)
                logging.warning(msg)
            else:
                curr_round = json.loads(world.data[self.app].get("round", "0"))
                # Still waiting for some units
                self.app.status = ops.ActiveStatus(msg := f"{curr_round}: [{board}]")
                logging.warning(msg)
        except Exception as e:
            self.app.status = ops.BlockedStatus(repr(e))

    def board_state(
        self, world: ops.Relation, cells: list[str], curr_round: int
    ) -> tuple[str, int | None]:
        """Determine if all units have completed the current round.

        Returns current map, e.g. "...00..101...." and the target round.
        """
        active_rounds = set()
        board = ""
        for cell in cells:
            try:
                data = world.data[self.model.get_unit(cell)]
                round_ = data.get("round", -1)
                value = data.get("value", ".")
                active_rounds.add(round_)
                board += value
            except Exception as e:
                raise ValueError(f"{cell}: {e}")

        if not active_rounds:
            return "." * len(cells), None

        completed = len(active_rounds) == 1
        return board, max(active_rounds) if completed else None


def neighbourhood(cells: list[str]) -> dict[str, list[str]]:
    """Compute the map of neighbours {unit/1: [unit/3, unit/4, ...], ...}."""
    # Square N x N map
    N = int(len(cells) ** 0.5)  # noqa: N806
    cells = cells[: N * N]

    rv: dict[int, set[int]] = {i: set() for i in range(len(cells))}
    for index in range(len(cells)):
        mey, mex = divmod(index, N)
        # FIXME this can be more elegant if I used slices
        for y in (-1, 0, 1):
            for x in (-1, 0, 1):
                ny = mey + y
                nx = mex + x
                if ny < 0 or ny >= N:
                    continue
                if nx < 0 or nx >= N:
                    continue
                if (ny, nx) == (mey, mex):
                    continue
                neighbour = ny * N + nx
                rv[index].add(neighbour)

    return {cells[k]: sorted(cells[vv] for vv in v) for k, v in rv.items()}


if __name__ == "__main__":
    ops.main(JGOLCoordinatorCharm)
