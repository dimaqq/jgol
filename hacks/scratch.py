import logging
import os
import pathlib
import signal

import ops


class Charm(ops.CharmBase):
    def __init__(self, framework: ops.Framework):
        super().__init__(framework)
        framework.observe(self.on.collect_unit_status, self.foo)
        print("init done")

    def foo(self, event: ops.EventBase):
        print("print", event)
        logging.warning("warn %s", event)
        if self.unit.is_leader():
            logging.warning("Lead me plenty")
        

if __name__ == "__main__":
    pathlib.Path("charm.pid").write_text(str(os.getpid()))
    while True:
        si = signal.sigwaitinfo({signal.SIGCONT})  # type: ignore
        env = dict(item.split("=", 1) for item in filter(None, pathlib.Path(f"/proc/{si.si_pid}/environ").read_text().split("\0")))
        os.environ.clear()
        os.environ.update(env)
        ops.main(Charm)
