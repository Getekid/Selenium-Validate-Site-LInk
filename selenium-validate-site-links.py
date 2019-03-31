from selenium import webdriver
import time
from urllib.parse import urljoin


class SiteAllLinkValidator:

    def __init__(self, driver, domain, error_page_title, time_to_wait=0, protocol='https://'):
        """Initiate the class with the following variables

        Args:
            driver: The selenium webdriver object.
            domain (str): The domain of the website.
            error_page_title (str): The Title of the error page.
            time_to_wait (int): Number of seconds to wait after each link visit.
            protocol (str): The protocol to be used, defaults in 'https://'.
        """
        self.driver = driver
        self.domain = domain
        self.error_page_title = error_page_title
        self.protocol = protocol
        self.time_to_wait = time_to_wait
        # Initiate a list to store the visited links.
        self.visited_links = []

    def validate_link(self, link):
        """Validate a link recursively.

        Checks that the link leads to valid page and
        afterwards validates all of its internal ones.

        Returns nothing the links that are external
        or have been visited already.)

        Args:
            link (str): The link URL to be validated.
        """
        if not self.is_internal(link):
            return ''

        url = urljoin(self.driver.current_url, link)
        # Skip if URL has been visited already.
        if url in self.visited_links:
            return ''

        # Go to the URL and validate it.
        self.driver.get(url)
        time.sleep(self.time_to_wait)
        assert self.driver.title != self.error_page_title
        self.visited_links.append(url)

        # Iterate through all the a tags of the page.
        for a in self.driver.find_elements_by_xpath('.//a'):
            link = a.get_attribute('href')
            self.validate_link(link)

    def is_internal(self, uri):
        """Checks whether the uri is an internal domain,
        either relative or starts with the domain.

        Args:
            uri (str): The URI to be checked.

        Returns:
            bool: Whether the URI is internal or not.
        """
        if not isinstance(uri, str):
            return False
        if uri.startswith('https://') or uri.startswith('http://'):
            if not uri.startswith('https://' + self.domain) and not uri.startswith('http://' + self.domain):
                return False
        return True


driver = webdriver.Chrome()
validator = SiteAllLinkValidator(driver, 'www.w3.org', '404 error page', 2)
validator.validate_link('https://www.w3.org')
driver.quit()
