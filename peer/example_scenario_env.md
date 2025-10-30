## The idea

Make `src/charm.py` the "boot" script:
- read stuff from files
- check few env vars
- maybe exit(0)
- import and run real code

The unit could keep track of:
- relation id
- set of neighbours

We'd only want to skip dispatching:
- only relation events, perhaps only changes
- within the correct relation
- remote unit not in our set

Extension:
- we do want to process the app data bag
- the leader must publish own name in the app data bag
- followers trigger on neighbours + leader
- if we're the leader, always trigger

We don't want to import (almost) anything, stick to pure Python:
- file with space-separated remote unit allow list
- file with latest leader
- hard-coded (?) hook name or dispatch path

Environment variables to check:
- `JUJU_HOOK_NAME` == "world-relation-changed"
- `JUJU_UNIT_NAME` == open("leader.txt").read()
- `JUJU_REMOTE_UNIT` in open("neighbours.txt").read().split() or leader

```py
import os
if os.environ.get("JUJU_HOOK_NAME") == "world-relation-changed":
    if os.path.exists("leader.txt") and os.path.exists("neighbours.txt"):
        leader = open("leader.txt").read()
        neighbours = set(open("neighbours.txt").read().split())
        if os.environ.get("JUJU_UNIT_NAME") != leader:
            if os.environ.get("JUJU_REMOTE_UNIT") not in (neighbours | {leader}):
                raise SystemExit(0)

import ops


class TheCharm(...):
    ...
    def cell(self, event):
        world = ...
        Path("leader.txt").write_text(world.data[self.app].get("leader", ""))
        neighbours = world.data[self.app]["map"][self.unit.name]
        Path("neighbours.txt").write_text(" ".join(neighbours))
        ...

    def god(self, event):
        ...
        if self.unit.is_leader: 
            world = ...
            ...
            world.data[self.app]["leader"] = self.unit.name


if __name__ == "__main__":
    ops.main(TheCharm)
```

## Example environment during a Scenario test

```
JUJU_VERSION 3.6.4
JUJU_UNIT_NAME app/0
JUJU_DISPATCH_PATH hooks/world-relation-changed
JUJU_HOOK_NAME world-relation-changed
JUJU_MODEL_NAME A1qZcPUAKzlmMxWSMsxo
JUJU_MODEL_UUID 6c5eac8e-92b4-418b-830e-cdeec16a15d6
JUJU_CHARM_DIR /var/folders/_w/29kl4lg13hb1r4mwm5cqhd8w0000gn/T/tmpwq0c50ri
JUJU_RELATION world
JUJU_RELATION_ID 1
JUJU_REMOTE_APP app
JUJU_REMOTE_UNIT app/2
JUJU_VERSION 3.6.4
JUJU_UNIT_NAME app/0
JUJU_DISPATCH_PATH hooks/update_status
JUJU_HOOK_NAME update_status
JUJU_MODEL_NAME A1qZcPUAKzlmMxWSMsxo
JUJU_MODEL_UUID 6c5eac8e-92b4-418b-830e-cdeec16a15d6
JUJU_CHARM_DIR /var/folders/_w/29kl4lg13hb1r4mwm5cqhd8w0000gn/T/tmpdzbmpmc8
```
