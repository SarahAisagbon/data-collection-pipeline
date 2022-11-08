from lib2to3.pgen2 import driver
from urllib.request import urlcleanup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import unittest
import time 
from time import sleep
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import WebDriverException
import requests
import datetime
import os 
import json
from uuid import uuid4

class Scraper:
    def __init__(self, URL, currency_list):
        self.currency_list = currency_list
        self.URL = URL
        self.driver = webdriver.Safari()
        self.id = str(uuid4())
        self.currency_link_list = []

    #scroll the page
    def scroll_page(self):
        self.driver.get(self.URL)
        html = self.driver.find_element(by=By.TAG_NAME, value = 'html')
        html.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
    
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
    def create_list_of_currency_links(self, currency_list):
        for currency_element in currency_list:
            urlstr = '//a[@title="' + str(currency_element) + '"]'
            xpath = self.driver.find_element(By.XPATH, urlstr) # Change this xpath with the xpath the current page has in their properties
            link = xpath.get_attribute('href')
            self.currency_link_list.append(link)
            time.sleep(2)
            
        return self.currency_link_list
    
    def create_currency_dictionary(self, link):
        # get links from 
        self.driver.get(currency_link)
        # get the Historical Data tab
        self.driver.find_element(by=By.XPATH, value='//*[@id="quote-nav"]/ul/li[4]/a').click()
        time.sleep(2)
        
        # create a price_dictionary 
        price_dictionary = {'Date': [], 'Open': [], 'High': [], 'Low': [], 'Close': []}
        
        counter = 0
        while i < 5:
            j = counter + 1
            date = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[1]/span').text
            price_dictionary['Date'].append(date)
            open = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[2]/span').text
            price_dictionary['Open'].append(open)
            high = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[3]/span').text
            price_dictionary['High'].append(high)
            low = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[4]/span').text
            price_dictionary['Low'].append(low)
            close = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[5]/span').text
            price_dictionary['Close'].append(close)
            i += 1
            
        # Update the dict_currencies dictionary with the new info for each currency
        index = self.currency_link_list.index(link)
        currency_element = self.currency_list[index]
            
        # create new currency_data dictionary 
        self.currency_data = {"title": currency_element,
                        "id": self.id,
                        "currency price": price_dictionary,
                        "timestamp": datetime.datetime.now() #current time
                        #"Graph": local_filepath
        }
            
        return self.currency_data
    
    def download_image(img_url, fp):
        img_data = requests.get(img_url).content
        with open(fp, 'wb') as handler:
            handler.write(img_data)
    
    def get_image_link(self, link):
        self.driver.get(link)
        # get the summary tab
        self.driver.find_element(by=By.XPATH, value='//*[@id="quote-nav"]/ul/li[1]/a/span').click()
        time.sleep(2)
        
        # get the graph for 5 day
        self.driver.find_element(by=By.XPATH, value='//*[@id="interactive-2col-qsp-m"]/ul/li[2]/button').click()
        time.sleep(2)
        
        index = self.currency_link_list.index(link)
        currency_element = self.currency_list[index]
        currency_element = currency_element.replace("/","")
        xp = '//*[@id="' + currency_element +'=X-interactive-2col-qsp-m"]'
        
        # identify image
        image = self.driver.find_element(by=By.XPATH, value=xp)
        # get src of image
        image_src = image.img.attrs['src']

    def check_if_file_exists(self, path):
        counter = 1
        while True:
            if not path.exists():
                return path
            else:
                path.split('.')
                path = path[0] + '_' + counter + path[1]
                if not path.exists():
                    return path
                else:
                    counter += 1
        
    def createFolder(self, dir):
        try:
            if not os.path.exists(dir):
                os.mkdir(dir)
        except OSError:
            print ('Error: Creating directory. ' +  dir)
            pass
    
    def createjsonFile(self, dir,):
        # Create raw_data folder and a subfolder named after the id 
        self.createFolder(dir)
        # Save the dictionary as a file called data.json
        with open('{dir}/{self.id}/data.json', 'w') as fp:
            json.dump(self.currency_data, fp)

    def main(self):
        self.open_and_accept_cookie()
        self.create_list_of_currency_links(currency_list)
        for link in self.currency_link_list:
            image_src = self.get_image_link(link)
            dir = './raw_data/'
            timestr = time.strftime('%d%m%Y_%H%M%S')
            subfolder = 'image'
            path = dir/subfolder/timestr.jpg
            self.check_if_file_exists(self, str(path))
            img = self.download_image(image_src, str(path))
            
            # create currency dictionary for each currency 
            self.create_currency_dictionary(link)
            # create a json file named after the id
            self.createjsonFile(dir)
            
            
        driver.quit()
        
if __name__ == "__main__":
    currency_list = ['GBP/USD', 'GBP/EUR', 'GBP/JPY', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF']
    URL = 'https://uk.finance.yahoo.com/currencies/'
    scrape = Scraper(URL, currency_list)
    scrape.main()
    