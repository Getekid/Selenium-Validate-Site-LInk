from time import sleep
import re


class SiteAllLinkValidator:
    """Validate the responses of all links in a website
    (contained in a specific area)"""

    def __init__(self, driver, domain):
        """Initiate the class.

        Args:
            driver: The selenium webdriver object.
            domain (str): The domain of the website to validate.
        """
        self.driver = driver
        self._domain = domain
        self._error_page_title = '404 not found'
        self._protocol = 'https://'
        self._time_to_wait = 0
        self._xpath_to_check = './/main'
        self.links_to_visit = []  # The list of the links left to be visited.
        self.links_visited = []  # The list to store the visited links.

    def validate_all_links(self):
        """Validate a link recursively.

        Checks that the link leads to valid page and
        afterwards validates all of its internal ones.

        Returns nothing if the links are external
        or have been visited already.
        """
        if not self.visit_url(self.protocol + self.domain):
            return
        sleep(self.time_to_wait)
        assert self.driver.title != self.error_page_title

        self.collect_current_page_links_to_visit(True)

        # Iterate through the links to visit.
        while self.links_to_visit:
            url = self.links_to_visit.pop(0)

            # Go to the URL and validate it.
            if not self.visit_url(self.protocol + self.domain + url):
                continue
            sleep(self.time_to_wait)
            try:
                assert self.driver.title != self.error_page_title
            except AssertionError:
                print('Invalid URL: ' + self.driver.current_url)

            self.collect_current_page_links_to_visit()

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

    @property
    def domain(self):
        """The domain of the website to validate."""
        return self._domain

    @domain.setter
    def domain(self, domain):
        # Strip the trailing slash, if any.
        if domain.endswith('/'):
            domain = domain[:-1]
        self._domain = domain

    @property
    def protocol(self):
        """The protocol to be used. Defaults to 'https://'."""
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        self._protocol = protocol

    @property
    def error_page_title(self):
        """The title of the error page of the website.
        The class will use that title to validate error pages.
        Defaults to '404 not found'

        TODO: Change this into an array to allow multiple page titles.
        """
        return self._error_page_title

    @error_page_title.setter
    def error_page_title(self, error_page_title):
        self._error_page_title = error_page_title

    @property
    def time_to_wait(self):
        """The number of seconds to wait after each link visit. Defaults to 0."""
        return self._time_to_wait

    @time_to_wait.setter
    def time_to_wait(self, time_to_wait):
        self._time_to_wait = time_to_wait

    @property
    def xpath_to_check(self):
        """The dom element to check for links to visit. Defaults to './/main'."""
        return self._xpath_to_check

    @xpath_to_check.setter
    def xpath_to_check(self, xpath_to_check):
        self._xpath_to_check = xpath_to_check

    def visit_url(self, url):
        """Visits the URL given.

        Args:
            url (str): The url to visit.

        Returns:
            bool: True if the URL was visited successfully.
                False in case the link is visited already.
        """
        # Stop if the URL has been visited already.
        if self.is_visited(url):
            return False
        # Go the URL.
        self.driver.get(url)
        # Nothing went wrong so set the URL as visited return True.
        self.set_visited(url)
        return True

    def collect_current_page_links_to_visit(self, check_full_page=False):
        """Iterates through all the 'a' tags of the current page,
        collects those not visited already and sets them to visit.

        By default, the function will gather all tags within
        xpath_to_check. If used with check_full_page=True then
        the full page will be checked.

        Args:
            check_full_page (bool): Whether to check the full page
                or within xpath_to_check. Defaults to False.
        """
        xpath = './/a' if check_full_page else self.xpath_to_check + '//a'
        for a in self.driver.find_elements_by_xpath(xpath):
            url = self.get_relative_url(a.get_attribute('href'))
            # Validate the URL before adding it to the list to visit.
            if not url:
                continue
            # Skip if URL has been visited already.
            if self.is_visited(url):
                continue
            # Add the URL to the list to visit.
            self.set_to_visit(url)

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

    def get_relative_url(self, link):
        """Returns the relative URL from a given internal link.
        Also for consistency the last slash ("/") is stripped, if any.

        Example:
            >>> print(self.get_relative_url("https://w3c.org/standards/"))
            "/standards".

        Args:
            link (str): The link URL.
        Returns:
            str|bool: The relative URL or False if link is not internal.
        """
        if not self.is_internal(link):
            return False
        if not link.startswith('https://') and not link.startswith('http://'):
            relative_url = link
        else:
            relative_url = link.split(self.get_domain_strip_www(), 1)[1]
        if relative_url.endswith("/"):
            relative_url = relative_url[:-1]
        return relative_url
