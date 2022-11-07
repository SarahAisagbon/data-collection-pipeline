from lib2to3.pgen2 import driver
from urllib.request import urlcleanup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
import time 
from time import sleep
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import WebDriverException
import datetime

class Scraper:
    def __init__(self, URL, currency_list):
        self.currency_list = currency_list
        self.driver = webdriver.Safari()
        self.URL = URL
        self.url_list = []
        self.link_list = []
        self.image_list = []
        self.dict_currencies = {'Currency': [], 'Open': [], 'High': [], 'Low': [], 'Close': []}
    
    #Open the webpage and accept the consent cookie
    def open_and_accept_cookie(self):
        self.driver.get(self.URL)
        self.driver.maximize_window()
        time.sleep(2)
        
        try:
            accept_cookies_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@value="agree"]')))
            accept_cookies_button.click() 
            time.sleep(2)
        except TimeoutException:
            print("Loading took too much time!")
            pass
        except NoSuchFrameException:
            pass

    #For each currency in the list, creating the url and putting it in a list and method to find the page link for each currency
    def get_currency_link(self, currency_list):
        for curr in currency_list:
            self.dict_currencies['Currency'].append(curr)
            st_url = '//a[@title="' + str(curr) + '"]'
            c = self.driver.find_element(By.XPATH, st_url) # Change this xpath with the xpath the current page has in their properties
            a_tag = c.find_element(by=By.TAG_NAME, value='a')
            link = a_tag.get_attribute('href')
            self.link_list.append(link)
            time.sleep(2)
            
        return self.link_list
    
    def get_image(self):
        for curr in currency_list:
            # get the summary tab
            self.driver.find_element(by=By.XPATH, value='//*[@id="quote-nav"]/ul/li[1]/a/span').click()
            time.sleep(2)
            # get the graph for 1 day
            self.driver.find_element(by=By.XPATH, value='//*[@id="interactive-2col-qsp-m"]/ul/li[1]/button').click()
            time.sleep(2)
            curr.replace("/","")
            xp = '//*[@id="' +curr +'=X-interactive-2col-qsp-m"]'
            # identify image
            image = self.driver.find_element(by=By.XPATH, value=xp)
            # get src of image
            image_src = image.get_attribute("src")
            #add image link to image_list
            self.image_list.append(image_src) 
            
        return self.image_list
    
    def make_curr_dict(self):
        #Collecting the data and putting it in a dictionary
        for l in scrape.link_list:
            self.driver.get(l)
            self.driver.find_element(by=By.XPATH, value='//span[text() = "Historical Data"]').click()
            time.sleep(2)
            
            open = self.driver.find_element(by=By.XPATH, value='//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[1]/td[2]/span').text
            self.dict_currencies['Open'].append(open)
            high = self.driver.find_element(by=By.XPATH, value='//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[1]/td[3]/span').text
            self.dict_currencies['High'].append(high)
            low = self.driver.find_element(by=By.XPATH, value='//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[1]/td[4]/span').text
            self.dict_currencies['Low'].append(low)
            close = self.driver.find_element(by=By.XPATH, value='//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr[1]/td[5]/span').text
            self.dict_currencies['Close'].append(close)
            
            return self.dict_currencies
    
    def get_dict_of_dict(self):
        # ct stores current time
        ct = datetime.datetime.now()
        self.dict_currencies['Graph Link'] = self.image_list
        ct_dict = {ct : self.dict_currencies}
        return ct_dict
    
if __name__ == "__main__":
    currency_list = ['GBP/USD', 'GBP/EUR', 'GBPJPY', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF']
    URL = 'https://uk.finance.yahoo.com/currencies/'
    scrape = Scraper(URL, currency_list)
    scrape.open_and_accept_cookie()
    scrape.get_currency_link(currency_list)
    driver.quit()
    