from selenium_testcase import SeleniumTestCase

URL = 'http://google.com'


class ProjectTestCase(SeleniumTestCase):

    def runTest(self):
        self.ordered_tests_runner()

    def ordered_tests_runner(self):
        pass

    def test_example_first(self, ctx):

        def given_test_url(ctx):
            ctx.url = URL

        def when_add_url_to_driver_dictionary(ctx):
            self.driver["url"] = URL

        def it_should_be_stored_in_dict(ctx):
            assert URL in self.driver["url"]

    def test_example_second(self, ctx):

        def given_correct_usermail_and_password(ctx):
            ctx.mail = "example@mail.com"
            ctx.password = "123456"

        def when_save_mail_and_pass_in_driver_dict(ctx):
            self.driver["mail"] = ctx.mail
            self.driver["pass"] = ctx.password

        def it_should_be_stored_in_dict(ctx):
            assert ctx.mail in self.driver["mail"]
            assert ctx.password in self.driver["pass"]