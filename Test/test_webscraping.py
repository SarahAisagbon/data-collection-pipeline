import unittest
import sys
# tell interpreter where to look
sys.path.insert(0,"/Users/sarahaisagbon/Documents/GitHub/data-collection-pipeline")
from Project import Webscraping
from Project.Webscraping import Scraper
from selenium import webdriver
from selenium.webdriver.safari.service import Service

import json
import pathlib as pl
import random
import time
import warnings

from selenium.webdriver.safari.options import Options
import tracemalloc
tracemalloc.start()

class ScraperTestCase(unittest.TestCase): 

    def test_accept_cookie(self):
        URL = "https://uk.finance.yahoo.com/currencies"
        actual_value = Scraper.open_and_accept_cookie(URL)
        expected_value = "Cookie Accepted"
        self.assertEqual(expected_value,actual_value)

    def setUp(self, URL = "https://uk.finance.yahoo.com/currencies", currency_list = ['GBP/USD', 'GBP/EUR', 'GBP/JPY', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF']):
        
        self.driver = webdriver.Safari()
        self.scrape = Scraper(URL, currency_list)
        self.scrape.open_and_accept_cookie(URL)
        link_list = self.scrape.__get_list_of_currency_links(currency_list)
        random_index = random.randint(0, 4)
        random_link = link_list[random_index]

    # tearDown runs after each test case
    def tearDown(self):
        self.driver.quit()
 
    #Check that all links are from the right website
    def test_link_list(self, link_list):
        non_website_list = list(filter(lambda x: x[:40] != 'https://uk.finance.yahoo.com/currencies', link_list))
        self.assertEqual(len(non_website_list), 0)

    #Check the length of the currency dictionary
    def test_currency_dictionary_length(self, random_link):
        currency_dict = self.scrape.create_currency_dictionary(random_link)
        values = currency_dict.values()
        expected_length = 5
        actual_length = len(values)
        self.assertEqual(expected_length, actual_length)

    #Check to see if the function create_currency_dictionary returns a dictionary
    def test_currency_dictionary_type(self, random_link):
        expected_value = dict
        actual_value = type(self.scrape.create_currency_dictionary(random_link))
        self.assertEqual(expected_value,actual_value)

    #Check the values in the dictionary
    def test_currency_dictionary_values(self, random_link):
        self.currency_dict = self.scrape.create_currency_dictionary(random_link)
        values = self.currency_dict.values()
        self.assertNotIn("Unknown", values)

    def assertIsFile(self, path):
        if not pl.Path(path).resolve().is_file():
            raise AssertionError(f"File does not exist: {path}")

    def assertIsFolder(self, path):
        if not pl.Path(path).resolve().is_dir():
            raise AssertionError(f"Folder does not exist: {path}")

    def test_download_all_data(self):
        imagefilename = time.strftime('%d%m%Y_%H%M%S')
        path =  "/Users/sarahaisagbon/Documents/GitHub/data-collection-pipeline/raw_data/"
        path_1 = path
        path_2 = path + "data.json"
        path_3 = path + "images/"
        path_4 = path + f"images/{imagefilename}.jpg"
        self.assertIsFolder(pl.Path(path_1))
        self.assertIsFile(pl.Path(path_2))
        self.assertIsFolder(pl.Path(path_3))
        self.assertIsFile(pl.Path(path_4))

    '''
    def test_ScrapingTime(self):
        currency_list = ["GBP/EUR", "GBP/USD"]
        link_list = self.scrape.__get_list_of_currency_links(self, currency_list)
        random_index = random.randint(0, 4)
        random_link = link_list[random_index]
        
        self.driver.get(random_link)
        details_dict = self.scrape.create_currency_dictionary()
        self.driver.quit()
        self.scrape.download_all_data()
    ''' 
    
if __name__ == '__main__':
    warnings.filterwarnings(action ="ignore", category = DeprecationWarning)
    unittest.main(verbosity = 2)
   