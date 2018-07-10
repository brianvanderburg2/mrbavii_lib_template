""" Tests for mrbaviirc.app.base """

from __future__ import absolute_import

__author__      = "Brian AllenVanderburg II"
__copyright__   = "Copyright 2018"
__license__     = "Apache License 2.0"

from ...app import base
from ...util import functools

class DerivedAppHelper(base.BaseAppHelper):

    @property
    def appname(self):
        return "Test"

def test_register_singleton():
    helper = DerivedAppHelper()

    called = [0]
    def db():
        called[0] += 1
        return 100
    helper.register_singleton("db", db)

    assert called[0] == 0
    assert helper.resolve_service("db") == 100
    assert called[0] == 1
    assert helper.resolve_service("db") == 100
    assert called[0] == 1

def test_register_factory():
    helper = DerivedAppHelper()

    called = [0]
    def db():
        called[0] += 1
        return 100
    helper.register_factory("db", db)

    assert called[0] == 0
    assert helper.resolve_service("db") == 100
    assert called[0] == 1
    assert helper.resolve_service("db") == 100
    assert called[0] == 2


def test_path():
    helper = DerivedAppHelper()
    path = helper.path
    assert("Test" in path.get_user_data_dir())
