import pytest

from ops.testing import State, Context, Relation

from charm import JGOLWorkerCharm


@pytest.fixture
def context() -> Context:
    relation = ops.testing.Relation(
        name="world",
        app_name="jgoll-worker",
        relation_id=1,
    )
    return Context(charm_cls=JGOLWorkerCharm, relations=[relation])

