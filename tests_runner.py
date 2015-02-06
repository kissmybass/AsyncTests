import unittest
import sys
from teamcity.unittestpy import TeamcityTestRunner
from async_testsuite import AsyncTestSuite
from tests_collection import TestsCollectionOne, TestsCollectionTwo, TestsCollectionThree


def test_suite():
    suite = AsyncTestSuite()
    # suite = unittest.TestSuite()
    suite.addTest(TestsCollectionOne())
    suite.addTest(TestsCollectionTwo())
    suite.addTest(TestsCollectionThree())
    return suite

if __name__ == '__main__':
    # unittest.TextTestRunner(verbosity=1, ).run(test_suite())
    TeamcityTestRunner().run(test_suite())

