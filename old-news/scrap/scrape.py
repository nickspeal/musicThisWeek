'''Scrape webpage'''

from bs4 import BeautifulSoup

from subprocess import check_output

soup = BeautifulSoup(check_output(['curl', "http://www.sfweekly.com/concerts/"]))
print soup.prettify()