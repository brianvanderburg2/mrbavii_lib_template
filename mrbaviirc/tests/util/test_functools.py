""" Tests for mrbaviirc.util.functools """

from __future__ import absolute_import

__author__      = "Brian AllenVanderburg II"
__copyright__   = "Copyright 2018"
__license__     = "Apache License 2.0"


from ...util import functools

# lazyprop
class LazyPropTester(object):

    def __init__(self):
        self.prop1_count = 0
        self.prop2_count = 0

    @functools.lazyprop
    def prop1(self):
        self.prop1_count += 1
        return 12

    @functools.lazyprop
    def prop2(self):
        self.prop2_count += 1
        return self.prop1 + 12

def test_lazyprop():
    tester1 = LazyPropTester()

    assert(tester1.prop1_count == 0)
    assert(tester1.prop2_count == 0)
    
    assert(tester1.prop1 == 12)
    assert(tester1.prop1_count == 1)
    assert(tester1.prop2_count == 0)

    assert(tester1.prop2 == 24)
    assert(tester1.prop1_count == 1)
    assert(tester1.prop2_count == 1)
    
