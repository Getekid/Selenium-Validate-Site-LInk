from selenium import webdriver
import time

protocol = 'https://'
domain = 'www.w3.org'

driver = webdriver.Chrome()
driver.get(protocol + domain)
# Iterate through all the a tags of the page.
for a in driver.find_elements_by_xpath('.//a'):
    uri = a.get_attribute('href')

    # Check whether the uri is an internal domain,
    # either relative or starts with the domain.
    if uri.startswith('http://') or uri.startswith('http://'):
        if not uri.startswith('https://' + domain) and not uri.startswith('http://' + domain):
            continue
    print(uri)

time.sleep(3)
driver.quit()
