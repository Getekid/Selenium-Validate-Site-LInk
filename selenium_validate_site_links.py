from time import sleep
import re
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException


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
        self._starting_url = ''
        self._time_to_wait = 0
        self._xpath_to_check = './/main'
        self._check_anchors = False
        self._regex_to_check = ''
        self.links_to_visit = []  # The list of the links left to be visited.
        self.links_visited = []  # The list to store the visited links.
        self.esn_error_pages = [
            'about:blank',
            'https://esn.org/content/national-level',
            'https://esn.org/content/international-board',
            'https://esn.org/star-awards',
            'https://esn.org/%23',
            'https://esn.org/ESNSurvey/automatic-recognition-full-degrees',
            'https://esn.org/~sigfried/newsite/ESNSurvey',
            'https://esn.org/content/mission-vision-values',
            'https://esn.org/content/section-information',
            'https://esn.org/content/research-study-visas-and-residence-permits',
            'https://esn.org/researchreleases',
            'https://esn.org/sites/default/files/Reaction%20of%20the%20Erasmus%20Student%20Network%20AISBL%20to%20the%20EU2020%20Consultation.pdf',
            'https://esn.org/survey',
            'https://esn.org/publications/ESNSurvey2014',
            'https://esn.org/content/prime-problems-recognition-making-erasmus',
            'https://esn.org/content/students-guidebook',
            'https://esn.org/webform/student-guidebook-order'
        ]

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
    def starting_url(self):
        """The URL to start checking the links."""
        return self._starting_url

    @starting_url.setter
    def starting_url(self, starting_url):
        self._starting_url = self.get_relative_url(starting_url)

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

    @property
    def check_anchors(self):
        """Whether to check the links containing an anchor or not. Defaults to False"""
        return self._check_anchors

    @check_anchors.setter
    def check_anchors(self, check_anchors):
        self._check_anchors = check_anchors

    @property
    def regex_to_check(self):
        """A Regular expression where a matching URL will be visited to be checked."""
        return self._regex_to_check

    @regex_to_check.setter
    def regex_to_check(self, regex_to_check):
        self._regex_to_check = regex_to_check

    def set_to_visit(self, link):
        """Adds a link to the list (dictionary) with links to visit.

        Args:
            link (str): The link URL to check.
        """
        self.links_to_visit.append(link)

    def set_visited(self, link):
        """Adds a link to the visited list.

        Args:
            link (str): The link URL to check.
        """
        self.links_visited.append(link)

    def is_visited(self, link):
        """Checks whether the link has been visited already or not.

        Args:
            link (str): The link URL to check.

        Returns:
            bool: Whether the link is visited or not.
        """
        return link in self.links_visited

    def validate_all_links(self):
        """Validate a link recursively.

        Checks that the link leads to valid page and
        afterwards validates all of its internal ones.

        Returns nothing if the links are external
        or have been visited already.
        """
        if not self.visit_url(self.protocol + self.domain + self.starting_url):
            return
        sleep(self.time_to_wait)
        # self.validate_current_page()
        self.collect_current_page_links_to_visit(True)

        # Iterate through the links to visit.
        while self.links_to_visit:
            url = self.links_to_visit.pop(0)

            # Go to the URL and validate it.
            if not self.visit_url(self.protocol + self.domain + url):
                continue
            sleep(self.time_to_wait)
            # self.validate_current_page()
            self.collect_current_page_links_to_visit()

    def visit_url(self, url):
        """Visits the URL given.

        Args:
            url (str): The url to visit.

        Returns:
            bool: True if the URL was visited successfully.
                False in case the link is visited already.
        """
        # Get the relative URL for managing the visited links status.
        relative_url = self.get_relative_url(url)
        # Stop if the URL is not a link or has been visited already.
        if relative_url is False or self.is_visited(relative_url):
            return False
        # Go to the URL.
        link = self.protocol + self.domain + relative_url
        try:
            self.driver.get(link)
        except WebDriverException as exception:
            # print('Error loading url: ' + url + ', attempted to go to: ' + link)
            # print(exception.msg)
            return False
        # Nothing went wrong so set the URL as visited and return True.
        self.set_visited(relative_url)
        return True

    def validate_current_page(self):
        """Validates that the current page does not show an error."""
        try:
            assert self.driver.title != self.error_page_title
        except AssertionError:
            print('Error page was found at URL: ' + self.driver.current_url)

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
            # In case of an error while getting the link, print the Exception message and continue.
            try:
                link = a.get_attribute('href')
            except StaleElementReferenceException as exception:
                # print('Invalid "a" tag has been skipped in URL: ' + self.driver.current_url)
                # print(exception.msg)
                continue
            # Validate the link before adding it to the list to visit.
            if link == '':
                # print('Empty "a" tag was found in URL: ' + self.driver.current_url)
                continue
            url = self.get_relative_url(link)
            if not url:
                continue
            if not self.is_for_check(link):
                continue
            if url in self.esn_error_pages:
                print('Error link "' + link + '" was found in page: ' + self.driver.current_url)
            # Skip if URL has been visited already.
            if self.is_visited(url):
                continue
            # Add the URL to the list to visit.
            self.set_to_visit(url)

    def get_relative_url(self, link):
        """Returns the relative URL from a given internal link.
        Also, for consistency, the last slash ("/") is stripped, if any.

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
        if not self.is_absolute_url(link):
            relative_url = link
        else:
            relative_url = link.split(self.get_domain_strip_www(), 1)[1]
        # Remove any anchors if needed.
        if not self.check_anchors:
            relative_url = self.get_link_no_anchor(relative_url)
        if relative_url.endswith("/"):
            relative_url = relative_url[:-1]
        return relative_url

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

    @staticmethod
    def get_link_no_anchor(link):
        """Returns a link without any anchors.

        Args:
            link (str): The link URL.

        Returns:
            str|bool: The link without any anchors or False when
                input is not a string.
        """
        if not isinstance(link, str):
            return False
        return link.split('#', 1)[0]

    def is_internal(self, uri):
        """Checks whether the uri is an internal domain,
        either relative or starts with the domain.

        Args:
            uri (str): The URI to be checked.

        Returns:
            bool: Whether the URI is internal or not.
        """
        if not isinstance(uri, str) or not self.is_link(uri):
            return False
        if self.is_absolute_url(uri):
            # Remove any 'www.' from the beginning of the domain to
            # allow checking both formats later in the Regex check.
            if re.match('https?://(www.)?' + self.get_domain_strip_www(), uri) is None:
                return False
        return True

    def is_for_check(self, uri):
        """Checks whether the uri is eligible to be checked
        according to the Regular expression set.

        Args:
            uri (str): The URI to be checked.

        Returns:
            bool: True if the URI matched the class' regex_to_check property, False otherwise.
                Also False when the regex_to_check property is not set or False.
        """
        if not self.regex_to_check:
            # If no valid Regex has been set therefore check all links.
            return True
        url = self.get_relative_url(uri)
        if url:
            return bool(re.match(self.regex_to_check, url))

    @staticmethod
    def is_absolute_url(uri):
        """Checks whether the given URI is an absolute URL or not.

        Args:
            uri (str): The given URI.

        Returns:
            bool: True is the URI is an absolute URL, False otherwise.
        """
        if not isinstance(uri, str):
            return False
        return re.match('https?://', uri)

    @staticmethod
    def is_link(uri):
        """Checks whether the given URI is a link or not.

        Args:
            uri (str): The given URI.

        Returns:
            bool: True if the uri is a link, False otherwise.
        """
        if not isinstance(uri, str):
            return False
        if uri == '':
            return False
        return not re.match('((mailto)|(tel)|(ftp)):', uri)
