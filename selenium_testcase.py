from unitspec import SpecTestCase


class SeleniumTestCase(SpecTestCase):

    driver = None

    @classmethod
    def setUpClass(cls):
        cls.driver = {"key_one": "value_one",
                      "key_two": "value_two"}

    @classmethod
    def tearDownClass(cls):
        cls.driver.clear()