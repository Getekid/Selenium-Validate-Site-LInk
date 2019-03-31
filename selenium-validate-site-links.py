from selenium import webdriver
import time


class SiteAllLinkValidator:

    # Initiate the class with the domain and protocol variables
    def __init__(self, driver, domain, protocol='https://'):
        self.driver = driver
        self.domain = domain
        self.protocol = protocol

    def validate_link(self):
        self.driver.get(self.protocol + self.domain)
        # Iterate through all the a tags of the page.
        for a in self.driver.find_elements_by_xpath('.//a'):
            uri = a.get_attribute('href')

            # Check whether the uri is an internal domain,
            # either relative or starts with the domain.
            if uri.startswith('http://') or uri.startswith('http://'):
                if not uri.startswith('https://' + self.domain) and not uri.startswith('http://' + self.domain):
                    continue
            print(uri)


driver = webdriver.Chrome()
validator = SiteAllLinkValidator(driver, 'www.w3.org')
validator.validate_link()
time.sleep(3)
driver.quit()
