import pytest
from collections import OrderedDict
from .config2db import config2db


@pytest.fixture
def rundir(tmpdir_factory):
    res = tmpdir_factory.mktemp("ModelOptimisationDB")
    return res


@pytest.fixture
def cfg():

    class CFG:
        Config = OrderedDict([
            ("Name", "study"),
            ("Scenario", "scenario"),
            ("Parameters", OrderedDict([
                ('minmax', OrderedDict([
                    ("comment", "some random stuff"),
                    ("A", [0, 10]),
                    ("B", [-1, 2])])
                 )])
             )])

    return CFG()


def test_config2db_fail(cfg, rundir):
    del cfg.Config['Scenario']
    with pytest.raises(RuntimeError):
        config2db(cfg, rundir)


def test_config2db(cfg, rundir):
    config2db(cfg, rundir)
