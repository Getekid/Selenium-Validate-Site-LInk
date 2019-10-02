import unittest
from selenium_validate_site_links import SiteAllLinkValidator


class TestSiteAllLinkValidator(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.validator = SiteAllLinkValidator('', 'w3.org')

    def test_get_domain_strip_www(self):
        self.validator.domain = 'www.w3.org'
        self.assertEqual(self.validator.get_domain_strip_www(), 'w3.org')
        self.validator.domain = 'w3.org'
        self.assertEqual(self.validator.get_domain_strip_www(), 'w3.org')

    def test_get_set_methods(self):
        # Test the domain property.
        self.assertEqual(self.validator.domain, 'w3.org')
        self.validator.domain = 'www.w3.org'
        self.assertEqual(self.validator.domain, 'www.w3.org')
        self.validator.domain = 'www.w3.org/'
        self.assertEqual(self.validator.domain, 'www.w3.org')
        # Test the protocol property.
        self.assertEqual(self.validator.protocol, 'https://')
        self.validator.protocol = 'http://'
        self.assertEqual(self.validator.protocol, 'http://')
        # Test the starting_url property.
        self.assertEqual(self.validator.starting_url, '')
        self.validator.starting_url = '/standards'
        self.assertEqual(self.validator.starting_url, '/standards')
        self.validator.starting_url = 'https://google.com'
        self.assertFalse(self.validator.starting_url)
        self.validator.starting_url = 'https://w3.org/standards/'
        self.assertEqual(self.validator.starting_url, '/standards')
        # Test the error_page_title property.
        self.assertEqual(self.validator.error_page_title, '404 not found')
        self.validator.error_page_title = 'Page not found'
        self.assertEqual(self.validator.error_page_title, 'Page not found')
        # Test the time_to_wait property.
        self.assertEqual(self.validator.time_to_wait, 0)
        self.validator.time_to_wait = 10
        self.assertEqual(self.validator.time_to_wait, 10)
        # Test the xpath_to_check property.
        self.assertEqual(self.validator.xpath_to_check, './/main')
        self.validator.xpath_to_check = './/body'
        self.assertEqual(self.validator.xpath_to_check, './/body')
        # Test the check_anchors property.
        self.assertFalse(self.validator.check_anchors)
        self.validator.check_anchors = True
        self.assertTrue(self.validator.check_anchors)
        # Test the regex_to_check property.
        self.assertEqual(self.validator.regex_to_check, '')
        self.validator.regex_to_check = '/?standards'
        self.assertEqual(self.validator.regex_to_check, '/?standards')

    def test_get_relative_url(self):
        # Check the valid cases.
        self.validator.domain = 'w3.org'
        self.assertEqual(self.validator.get_relative_url('http://www.w3.org/'), '')
        self.validator.domain = 'www.w3.org'
        self.assertEqual(self.validator.get_relative_url('https://w3.org/'), '')
        self.assertEqual(self.validator.get_relative_url('https://w3.org/standards/'), '/standards')
        self.assertEqual(self.validator.get_relative_url('https://www.w3.org/standards/'), '/standards')
        self.assertEqual(self.validator.get_relative_url(
            'https://w3.org/standards/w3.org/standards'),
            '/standards/w3.org/standards'
        )
        self.assertFalse(self.validator.get_relative_url(''))
        self.assertEqual(self.validator.get_relative_url('/'), '')
        # Test with check_anchors False.
        self.validator.check_anchors = False
        self.assertEqual(self.validator.get_relative_url('https://w3.org/#top'), '')
        self.assertEqual(self.validator.get_relative_url('https://w3.org/standards#top'), '/standards')
        self.assertEqual(self.validator.get_relative_url('https://w3.org/standards/#top'), '/standards')
        self.assertEqual(self.validator.get_relative_url('#top'), '')
        self.assertEqual(self.validator.get_relative_url('/standards'), '/standards')
        self.assertEqual(self.validator.get_relative_url('/standards#top'), '/standards')
        self.assertEqual(self.validator.get_relative_url('/standards/#top'), '/standards')
        # Test with check_anchors True.
        self.validator.check_anchors = True
        self.assertEqual(self.validator.get_relative_url('https://w3.org/#top'), '/#top')
        self.assertEqual(self.validator.get_relative_url('https://w3.org/standards#top'), '/standards#top')
        self.assertEqual(self.validator.get_relative_url('https://w3.org/standards/#top'), '/standards/#top')
        self.assertEqual(self.validator.get_relative_url('#top'), '#top')
        self.assertEqual(self.validator.get_relative_url('/standards'), '/standards')
        self.assertEqual(self.validator.get_relative_url('/standards#top'), '/standards#top')
        self.assertEqual(self.validator.get_relative_url('/standards/#top'), '/standards/#top')
        # Check the invalid cases.
        self.assertFalse(self.validator.get_relative_url('https://google.com/search'))
        self.assertFalse(self.validator.get_relative_url('mailto:mail@example.com'))
        self.assertFalse(self.validator.get_relative_url('tel:+000000000000'))
        self.assertFalse(self.validator.get_relative_url('ftp:server@example.com'))

    def test_get_link_no_anchor(self):
        self.assertEqual(self.validator.get_link_no_anchor('https://w3.org/standards#top'), 'https://w3.org/standards')
        self.assertEqual(self.validator.get_link_no_anchor('https://w3.org/standards/#top'), 'https://w3.org/standards/')
        self.assertEqual(self.validator.get_link_no_anchor('https://w3.org/standards'), 'https://w3.org/standards')
        self.assertEqual(self.validator.get_link_no_anchor('/standards#top'), '/standards')
        self.assertEqual(self.validator.get_link_no_anchor('/standards/#top'), '/standards/')
        self.assertEqual(self.validator.get_link_no_anchor('https://w3.org/standards'), 'https://w3.org/standards')

    def test_is_internal(self):
        self.validator.domain = 'www.w3.org'
        # Check the valid cases.
        self.assertTrue(self.validator.is_internal('/page/path'))
        self.assertTrue(self.validator.is_internal('page/path'))
        self.assertTrue(self.validator.is_internal('http://www.w3.org/page/path'))
        self.assertTrue(self.validator.is_internal('http://w3.org/page/path'))
        self.assertTrue(self.validator.is_internal('https://www.w3.org/page/path'))
        self.assertTrue(self.validator.is_internal('https://w3.org/page/path'))
        self.assertTrue(self.validator.is_internal('http://www.w3.org/page/path'))
        self.assertTrue(self.validator.is_internal('http://www.w3.org/page/path'))
        self.assertTrue(self.validator.is_internal('http://www.w3.org/page/path'))
        self.assertTrue(self.validator.is_internal('http://www.w3.org/page/path'))
        # Check the invalid cases.
        self.assertFalse(self.validator.is_internal('http://www.google.com/'))
        self.assertFalse(self.validator.is_internal('http://google.com/'))
        self.assertFalse(self.validator.is_internal('https://www.google.com/'))
        self.assertFalse(self.validator.is_internal('https://google.com/'))
        self.assertFalse(self.validator.is_internal('https://google.com/http://w3.org/standards'))
        self.assertFalse(self.validator.is_internal('mailto:mail@example.com'))
        self.assertFalse(self.validator.is_internal('tel:+000000000000'))
        self.assertFalse(self.validator.is_internal('ftp:server@example.com'))
        # Check the special cases.
        self.assertFalse(self.validator.is_internal(''))
        self.assertFalse(self.validator.is_internal(None))

    def test_is_for_check(self):
        self.assertTrue(self.validator.is_for_check('/standards/'))
        self.assertTrue(self.validator.is_for_check('https://w3.org/standards/'))
        self.validator.regex_to_check = '/?standards'
        self.assertTrue(self.validator.is_for_check('standards/'))
        self.assertFalse(self.validator.is_for_check('participate/'))

    def test_is_absolute_url(self):
        self.assertFalse(self.validator.is_absolute_url('/standards'))
        self.assertFalse(self.validator.is_absolute_url('standards'))
        self.assertFalse(self.validator.is_absolute_url('standards#top'))
        self.assertTrue(self.validator.is_absolute_url('https://w3.org/'))
        self.assertTrue(self.validator.is_absolute_url('http://w3.org/standards'))

    def test_is_link(self):
        self.assertTrue(self.validator.is_link('https://w3.org'))
        self.assertTrue(self.validator.is_link('https://www.w3.org'))
        self.assertTrue(self.validator.is_link('/standards'))
        self.assertTrue(self.validator.is_link('/standards/#top'))
        self.assertFalse(self.validator.is_link(''))
        self.assertFalse(self.validator.is_link('mailto:mail@example.com'))
        self.assertFalse(self.validator.is_link('tel:+000000000000'))
        self.assertFalse(self.validator.is_link('ftp:server@example.com'))


if __name__ == '__main__':
    unittest.main()
