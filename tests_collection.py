import time
from project_testcase import ProjectTestCase


class TestsCollectionOne(ProjectTestCase):

    def ordered_tests_runner(self):
        self.test_common_part_first()
        self.test_common_part_second()
        self.test_assert_that_A_eq_B()
        self.test_open_tested_url()

    def test_assert_that_A_eq_B(self):

        def given_A_and_B(ctx):
            ctx.a = 10
            ctx.b = 10

        def it_should_be_A_eq_B(ctx):
            self.assertEqual(ctx.a, ctx.b)

    def test_open_tested_url(self):

        def given_tested_url(ctx):
            ctx.url = self.driver["url"]

        def when_open_test_url(ctx):
            time.sleep(2)
            print ctx.url

        def it_should_be_open_tested_page(ctx):
            self.assertEqual(ctx.url, self.driver["url"])


class TestsCollectionTwo(ProjectTestCase):

    def ordered_tests_runner(self):
        self.test_common_part_first()
        self.test_common_part_second()
        self.test_assert_that_Z_eq_Y()
        self.test_open_tested_url2()

    def test_assert_that_Z_eq_Y(self):

        def given_Z_and_Y(ctx):
            ctx.z = 1
            ctx.y = 1

        def it_should_be_A_eq_B(ctx):
            self.assertEqual(ctx.z, ctx.y)

    def test_open_tested_url2(self):

        def given_tested_url(ctx):
            self.driver["url"] = "http://yahoojeu.com"
            ctx.url = self.driver["url"]

        def when_open_test_url(ctx):
            time.sleep(1)
            print ctx.url

        def it_should_be_open_tested_page(ctx):
            self.assertEqual(ctx.url, self.driver["url"])


class TestsCollectionThree(ProjectTestCase):

    def ordered_tests_runner(self):
        self.test_common_part_first()
        self.test_common_part_second()
        self.test_assert_that_H_not_eq_T()
        self.test_open_tested_url3()

    def test_assert_that_H_not_eq_T(self):

        def given_H_and_T(ctx):
            ctx.h = 10
            ctx.t = 5

        def it_should_be_H_not_eq_T(ctx):
            self.assertNotEqual(ctx.h, ctx.t)

    def test_open_tested_url3(self):

        def given_tested_url(ctx):
            self.driver["url"] = "http://mail-mail.com"
            ctx.url = self.driver["url"]

        def when_open_test_url(ctx):
            time.sleep(3)
            print ctx.url

        def it_should_be_open_tested_page(ctx):
            self.assertEqual(ctx.url, self.driver["url"])