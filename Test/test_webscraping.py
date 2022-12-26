import unittest
import sys
# tell interpreter where to look
sys.path.insert(0,"/Users/sarahaisagbon/Documents/GitHub/data-collection-pipeline")
from Project import Webscraping
from Project.Webscraping_GC import Scraper
from selenium import webdriver
from selenium.webdriver.firefox.service import Service

import json
import pathlib as pl
import random
import time

from selenium.webdriver.firefox.options import Options
import tracemalloc
tracemalloc.start()

class ScraperTestCase(unittest.TestCase): 
    '''
    def test_accept_cookie(self): 
        #URL = 'https://uk.finance.yahoo.com/currencies'
        actual_value = Scraper.open_and_accept_cookie(self.URL)
        expected_value = 'Cookie Accepted'
        self.assertEqual(expected_value,actual_value)
    '''
    
    @classmethod
    def setUp(self) -> None:
        self.URL = 'https://uk.finance.yahoo.com/currencies'
        self.currency_list = ['GBP/USD', 'GBP/EUR', 'GBP/JPY', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF']
        self.scrape = Scraper(self.URL, self.currency_list)
        self.scrape.open_and_accept_cookie(self.URL)
        self.link_list = self.scrape.get_list_of_currency_links(self.currency_list)
        
        self.random_index = random.randint(0, len(self.currency_list)-1)
        self.random_link = self.link_list[self.random_index]
        print("Setup Complete")

    # tearDown runs after each test case
    @classmethod
    def tearDown(self) -> None:
        self.scrape.close_browser()
        print("Close browser")
 
    #Check that all links are from the right website
    def test_link_list(self):
        non_link_list = list(filter(lambda x: x[:35] != 'https://uk.finance.yahoo.com/quote/', self.link_list))
        self.assertEqual(len(non_link_list), 0)

    #Check the length of the currency dictionary
    def test_currency_dictionary_length(self):
        currency_dict = self.scrape.create_currency_dictionary(self.random_link)
        values = currency_dict.values()
        expected_length = 5
        actual_length = len(values)
        self.assertEqual(expected_length, actual_length)

    #Check to see if the function create_currency_dictionary returns a dictionary
    def test_currency_dictionary_type(self):
        expected_value = dict
        actual_value = type(self.scrape.create_currency_dictionary(self.random_link))
        self.assertEqual(expected_value,actual_value)

    #Check the values in the dictionary
    def test_currency_dictionary_values(self):
        self.currency_dict = self.scrape.create_currency_dictionary(self.random_link)
        values = self.currency_dict.values()
        self.assertNotIn("Unknown", values)

    def assertIsFile(self, path):
        if not pl.Path(path).resolve().is_file():
            raise AssertionError(f"File does not exist: {path}")

    def assertIsFolder(self, path):
        if not pl.Path(path).resolve().is_dir():
            raise AssertionError(f"Folder does not exist: {path}")

    def test_download_all_data(self):
        random_curr = self.currency_list[self.random_index]
        random_curr = random_curr.replace("/","")
        imagefilename = time.strftime('%d%m%Y_%H%M%S')
        path =  "/Users/sarahaisagbon/Documents/GitHub/data-collection-pipeline/raw_data"
        path_1 = path + "/" + random_curr
        path_2 = path_1 +  "/data.json"
        path_3 = path_1 + "/images/"
        path_4 = path_1 + f"/images/{imagefilename}.jpg"
        self.assertIsFolder(pl.Path(path_1))
        self.assertIsFile(pl.Path(path_2))
        self.assertIsFolder(pl.Path(path_3))
        self.assertIsFile(pl.Path(path_4))
    
if __name__ == '__main__':
    unittest.main(verbosity = 2)
   