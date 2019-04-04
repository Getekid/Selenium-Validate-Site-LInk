from time import sleep
from urllib.parse import urljoin
import re


class SiteAllLinkValidator:

    def __init__(self, driver, domain, error_page_title='404 not found', time_to_wait=0, protocol='https://'):
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
        # links_to_visit will contain all links left to be visited as keys,
        # pointing towards the URL of the page in which it was found.
        self.links_to_visit = []
        # Initiate a list to store the visited links.
        self.links_visited = []

    def validate_all_links(self):
        """Validate a link recursively.

        Checks that the link leads to valid page and
        afterwards validates all of its internal ones.

        Returns nothing the links that are external
        or have been visited already.)
        """
        self.links_to_visit.append(self.protocol + self.domain)
        while self.links_to_visit:
            url = self.links_to_visit.pop(0)

            if not self.is_internal(url):
                continue

            # Skip if URL has been visited already.
            if self.is_visited(url):
                continue

            # Go to the URL and validate it.
            self.driver.get(url)
            sleep(self.time_to_wait)
            assert self.driver.title != self.error_page_title
            self.set_visited(url)

            # Iterate through all the a tags of the page.
            for a in self.driver.find_elements_by_xpath('.//a'):
                link = a.get_attribute('href')
                # Validate the link before adding it to the list to visit.
                if not self.is_internal(link):
                    continue

                url = urljoin(self.driver.current_url, link)
                # Skip if URL has been visited already.
                if self.is_visited(url):
                    continue

                # Add the URL to the link list to visit.
                self.set_to_visit(url)

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
            # Remove any 'www.' from the beginning of the domain to
            # allow checking both formats later in the Regex check.
            if re.match('https?://(www.)?' + self.get_domain_strip_www(), uri) is None:
                return False
        return True

    def set_domain(self, domain):
        """Sets the domain of the class.

        Args:
            domain (str): The new domain.
        """
        self.domain = domain

    def set_to_visit(self, link):
        """Adds a link to the list (dictionary) with links to visit.

        Args:
            link (str): The link URL to check.
        """
        self.links_to_visit.append(link)

    def is_visited(self, link):
        """Checks whether the link has been visited already or not.
        
        Args:
            link (str): The link URL to check.
        
        Returns:
            bool: Whether the link is visited or not.
        """
        return link in self.links_visited

    def set_visited(self, link):
        """Adds a link to the visited list.

        Args:
            link (str): The link URL to check.
        """
        self.links_visited.append(link)
    
    def get_domain_strip_www(self):
        """Returns the domain stripped of any
        'www.' string it may have in the beginning.
        
        Returns:
            domain_no_www (str): The domain without 'www.'
        """
        domain_no_www = self.domain
        if domain_no_www.startswith('www.'):
            domain_no_www = self.domain[4:]
        
        return domain_no_www
