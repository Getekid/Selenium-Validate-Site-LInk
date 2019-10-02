import unittest
from selenium_validate_site_links import SiteAllLinkValidator
from selenium import webdriver


class TestSiteAllLinkValidatorWebdriver(unittest.TestCase):

    @classmethod
    def setUp(self):
        driver = webdriver.Chrome()
        self.validator = SiteAllLinkValidator(driver, 'w3.org')

    def tearDown(self):
        self.validator.driver.quit()

    def test_visit_url(self):
        # Test the successful visits.
        self.validator.links_visited = []
        self.assertTrue(self.validator.visit_url('https://w3.org'))
        self.assertEqual(self.validator.driver.current_url, 'https://www.w3.org/')
        self.assertTrue(self.validator.is_visited(''))
        self.assertTrue(self.validator.visit_url('/standards/'))
        self.assertTrue(self.validator.is_visited('/standards'))
        # Test the unsuccessful visits.
        self.validator.set_visited('')
        self.assertFalse(self.validator.visit_url('https://w3.org'))
        self.assertTrue(self.validator.visit_url('w3.org'))
        self.assertFalse(self.validator.visit_url(''))
        self.assertFalse(self.validator.visit_url('mailto:mail@example.com'))
        self.assertFalse(self.validator.visit_url('tel:+000000000000'))
        self.assertFalse(self.validator.visit_url('ftp:server@example.com'))

    def test_validate_all_links(self):
        # Set the basic properties.
        self.validator.protocol = 'https://'
        self.validator.domain = 'w3.org'
        self.validator.starting_url = '/standards'
        self.validator.regex_to_check = '/?standards'
        self.validator.validate_all_links()
        # Make the assertions.
        self.assertEqual(len(self.validator.links_visited), 11)
        self.assertEqual(self.validator.links_visited[0], self.validator.starting_url)


if __name__ == '__main__':
    unittest.main()
