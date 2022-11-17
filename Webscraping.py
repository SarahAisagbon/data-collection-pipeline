from lib2to3.pgen2 import driver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import WebDriverException
from urllib.request import urlcleanup
from uuid import uuid4
import datetime
import json
import os 
import requests
import time 
from time import sleep
import unittest

class Scraper:
    ### Google
    
    '''
    This class is used to scrape information from a chosen website and store it in files.

    Parameters:
        currency list (list): the list of currencies I'm interested in.
        URL (str): the string of the url we are interested in exploring.
        driver: Safari webdriver.
    
    Attributes:
        currency_link_list (list): empty list of currency link.
        currency_dictionary (dict): all the desired details for each currency.
    
    '''
    def __init__(self, URL, currency_list):
        '''
        See help(Scraper) for accurate signature
        '''
        self.currency_list = currency_list
        self.URL = URL
        self.driver = webdriver.Safari()
        self.currency_link_list = []
        self.required_details = ["Currency", "Currency Prices", "Timestamp", "Image", "UUID"]
        self.currency_dictionary = {self.required_details[i]: ["Unknown"] for i in range(len(self.required_details))}

    def scroll_page(self):
        '''
        This function is used to scroll a page.
        '''
        self.driver.get(self.URL)
        html = self.driver.find_element(by=By.TAG_NAME, value = "html")
        html.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)
    
    def open_and_accept_cookie(self):
        '''
        This function is used to open the webpage and accept the consent cookie.
        '''
        self.driver.get(self.URL)
        self.driver.maximize_window()
        time.sleep(2)
        
        try:
            accept_cookies_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@value="agree"]')))
            accept_cookies_button.click() 
            time.sleep(2)
            return("Cookie Accepted")
        except TimeoutException:
            print("Loading took too much time!")
            pass
        except NoSuchFrameException:
            pass

    def __create_list_of_currency_links(self, currency_list):
        '''
        This function is used to create the url for each currency in the currency_list, gets the link and return the list of currency links.
        
        Args:
            currency_list: list of string representation of the currencies.
            
        Returns:
            list: list of string representation of the currency link.
        '''
        for currency_element in currency_list:
            urlstr = '//a[@title="' + str(currency_element) + '"]'
            xpath = self.driver.find_element(By.XPATH, urlstr) # Change this xpath with the xpath the current page has in their properties
            link = xpath.get_attribute("href")
            self.currency_link_list.append(link)
            time.sleep(2)
        return self.currency_link_list

    def __extract_information(self, link):
        '''
        This function is used to navigate to the right page, scrapes the required information, puts it in a dictionary and return the dictionary.
        
        Args:
            link: the string representation of the link for a page. Will be from currency_link_list.
            
        Returns:
            dictionary
        '''
        # get links from website
        self.driver.get(link)
        # get the Historical Data tab
        self.driver.find_element(by=By.XPATH, value='//*[@id="quote-nav"]/ul/li[4]/a').click()
        time.sleep(2)
        
        # create a price_dictionary 
        price_dictionary = {"Date": [], "Open": [], "High": [], "Low": [], "Close": []}
        
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
        
        return price_dictionary
    
    def __assign_uuid(self):
            '''
        This generates a random uuid.
        
        Returns:
            uuid
        '''
        UUID = str(uuid4())
        return UUID
    
    def __download_image(self, image_scr, fp):
        '''
        This function is used to download a image from the website and saves it in a subfolder.
        
        Args:
            fp: the string representation of the path for the subfolder.
            image_src: the string representation of the scr for the image.
            
        '''
        img_data = requests.get(image_scr).content
        with open(fp, 'wb') as handler:
            handler.write(img_data)
    
    def __get_image_link(self, link):
        '''
        This function is used to get the link for a image on the website.
        
        Args:
            link: the string representation of the link for a page. Will be from currency_link_list.
            
        Returns:
            image_scr: the string representation of the scr for the image.
        '''
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
        image_src = image.img.attrs["src"]
        
        return image_src
    
    def create_currency_dictionary(self, link):
        '''
        This function puts all the above data into the currency dictionary.
        
        Args:
            link: the string representation of the link for a page. Will be from currency_link_list.
        '''
        # Update the dict_currencies dictionary with the new info for each currency
        index = self.__create_list_of_currency_links.index(link)
        currency_element = self.currency_list[index]
            
        # create new currency_data dictionary 
        self.currency_dictionary["Currency"] = currency_element
        self.currency_dictionary["UUID"] = Scraper.__assign_uuid(self)
        self.currency_dictionary["Currency Prices"] =  Scraper.__extract_information(self, link)
        self.currency_dictionary["Timestamp"] = datetime.datetime.now() #current time
        #self.currency_dictionary["Graph"] = local_filepath
            
        return self.currency_dictionary

    def check_if_file_exists(self, path):
        '''
        This function is used to check if image file exists. If it does, add the order in the title.

        Args:
            path: the string representation of the path for the new file.
        '''
        counter = 1
        while True:
            if not os.path.exists():
                return path
            else:
                path.split(".")
                path = path[0] + "_{counter}" + path[1]
                if not os.path.exists(path):
                    return path
                else:
                    counter += 1
                    
    def createFolder(self, path):
        '''
        This function is used to create a folder.
        
        Args:
            path: the string representation of the path for the new folder.
        '''
        try:
            if not os.path.exists(path):
                os.mkdir(path)
        except OSError:
            print ("Error: Creating directory. " +  path)
            pass
    
    def __currency_folder(self, link, path):
        '''
        This function is used to create a raw_data folder and a UUID subfolder and saves the dictionary in the subfolder as a file called data.json.

        Args:
            link: the string representation of the link for a page. Will be from currency_link_list.
            path: the string representation of the path for the new folder.
            
        '''
        
        currency_dict = Scraper.create_currency_dictionary(link)
        
        currency_id = currency_dict["UUID"]
        currency_path = path + f"/{currency_id}"
    
        # Create raw_data folder 
        Scraper.createFolder(currency_path)
        # Save the dictionary as a file called data.json in a subfolder named after the id 
        with open(f"{currency_path}/data.json", 'w') as fp:
            json.dump(currency_dict, fp)

    def __image_folder(self, link, path):
        '''
        This function is used to create a image folder and a image file and saves the image in the file.

        Args:
            link: the string representation of the link for a page. Will be from currency_link_list.
            path: the string representation of the path for the new folder.
            
        '''
        
        currency_dict = Scraper.create_currency_dictionary(link)
        
        currency_id = currency_dict["UUID"]
        image_src = Scraper.get_image_link(link)
        image_folder_path = path + f"/{currency_id}/images"
        # Create image folder 
        Scraper.createFolder(image_folder_path)
        
        #Create file with the title in the form <date>_<time>_<order of image>.<image file extension>
        timestr = time.strftime('%d%m%Y_%H%M%S')
        image_file_path = image_folder_path + f"/{timestr}.jpg"
        Scraper.check_if_file_exists(str(image_file_path))
        
        #Download and save the image in the file created above
        img = Scraper.download_image(image_src, image_file_path)
        
    def main(self):
        self.open_and_accept_cookie()
        self.create_list_of_currency_links(Scraper.currency_list)
        for link in self.currency_link_list:
            path = "/Users/sarahaisagbon/Documents/GitHub/data-collection-pipeline/raw_data/"
            # create currency dictionary for each currency 
            self.create_currency_dictionary(link)
            # create a json file named after the id
            self.__currency_folder(link, path)
            self.__image_folder(link, path)
        driver.quit()
    
if __name__ == "__main__":
    currency_list = ['GBP/USD', 'GBP/EUR', 'GBP/JPY', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF']
    URL = 'https://uk.finance.yahoo.com/currencies/'
    scrape = Scraper(URL, currency_list)
    scrape.main()
    