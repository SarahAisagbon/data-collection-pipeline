from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException
from selenium.webdriver.firefox.options import Options


from uuid import uuid4
import datetime
import json
import io
import os 
import re
import requests
import time 

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
    def __init__(self, URL, currency_list, *args, **kwargs):
        '''
        See help(Scraper) for accurate signature
        '''
        super(Scraper, self).__init__(*args, **kwargs)
        
        self.currency_list = currency_list
        self.URL = URL
        firefoxOptions = Options()
        firefoxOptions.add_argument("--no-sandbox") #Bypass OS security model
        
        firefoxOptions.add_argument("--headless")
        firefoxOptions.add_argument("window-size=1920,1080")
        firefoxOptions.add_argument('--disable-extensions') #disabling extensions
        firefoxOptions.add_argument("--disable-dev-shm-usage") #overcome limited resource problems
        firefoxOptions.add_argument('--disable-gpu')

        self.driver = webdriver.Firefox(
            executable_path = "/usr/local/bin/geckodriver",
            options = firefoxOptions
        )
        
        self.currency_link_list = []
        self.required_details = ["Currency", "Currency Prices", "Image", "Timestamp", "UUID"]
        self.currency_dictionary = {self.required_details[i]: ["Unknown"] for i in range(len(self.required_details))}

    
    def scroll_page(self, URL):
        '''
        This function is used to scroll a page.
        '''
        
        self.driver.get(URL)
        html = self.driver.find_element(by=By.TAG_NAME, value = "html")
        html.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

    
    def open_and_accept_cookie(self, URL):
        '''
        This function is used to open the webpage and accept the consent cookie.
        '''
        
        self.driver.get(URL)
        self.driver.maximize_window()
        time.sleep(2)
        
        try:
            accept_cookies_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//button[@value="agree"]')))
            accept_cookies_button.click() 
            time.sleep(2)
            return('Cookie Accepted')
        except TimeoutException:
            print('Loading took too much time!')
            pass
        except NoSuchFrameException:
            pass
        
    def close_browser(self):
        self.driver.close()
        
    def get_list_of_currency_links(self, currency_list):
        '''
        This function is used to create the url for each currency in the currency_list, gets the link and return the list of currency links.
        
        Args:
            currency_list: list of string representation of the currencies.
            
        Returns:
            list: list of string representation of the currency link.
        '''
        
        for currency_element in currency_list:
            currencyurl = '//a[@title="' + str(currency_element) + '"]'
            xpath = self.driver.find_element(By.XPATH, currencyurl) # Change this xpath with the xpath the current page has in their properties
            link = xpath.get_attribute("href")
            self.currency_link_list.append(link)
            
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
        self.driver.find_element(by=By.XPATH, value='//*[@data-test="HISTORICAL_DATA"]').click()
        time.sleep(2)
        
        # create a price_dictionary 
        price_dictionary = {"Date": [], "Open": [], "High": [], "Low": [], "Close": []}
        
        counter = 0
        while counter < 5:
            j = counter + 1
            date = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[1]/span').text
            price_dictionary["Date"].append(date)
            open = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[2]/span').text
            price_dictionary["Open"].append(open)
            high = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[3]/span').text
            price_dictionary["High"].append(high)
            low = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[4]/span').text
            price_dictionary["Low"].append(low)
            close = self.driver.find_element(By.XPATH, '//*[@id="Col1-1-HistoricalDataTable-Proxy"]/section/div[2]/table/tbody/tr['+str(j)+']/td[5]/span').text
            price_dictionary["Close"].append(close)
            counter += 1
        print("Information has been scraped")
        return price_dictionary
    
    def __assign_uuid(self):
        '''
        This generates a random uuid.
        
        Returns:
            uuid
        '''
        UUID = str(uuid4())
        return UUID
    
    def create_currency_dictionary(self, link):
        '''
        This function puts all the above data into the currency dictionary.
        
        Args:
            link: the string representation of the link for a page. Will be from currency_link_list.
        '''
        
        index = self.currency_link_list.index(link)
        # Update the dict_currencies dictionary with the new info for each currency
        currency_element = self.currency_list[index]
            
        # create new currency_data dictionary 
        self.currency_dictionary["Currency"] = currency_element
        self.currency_dictionary["Currency Prices"] =  self.__extract_information(link)
        self.currency_dictionary["Image"] = self.__get_image_link(link)
        self.currency_dictionary["Timestamp"] = str(datetime.datetime.now()) #current time
        self.currency_dictionary["UUID"] = self.__assign_uuid()
        
        print("Information has been placed in dictionary")
        return self.currency_dictionary
    
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
        self.driver.find_element(by=By.XPATH, value='//*[@data-test="SUMMARY"]').click()
        time.sleep(1)
        
        # identify the website logo
        img_property = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='uh-logo']"))).value_of_css_property("background-image")
        
        # get src of image
        image_src = str(re.split('[()]',img_property)[1])
        image_src = image_src[1:-1]
        
        return image_src
    
    def __download_image(self, image_scr, path):
        '''
        This function is used to download a image from the website and saves it in a subfolder.
        
        Args:
            fp: the string representation of the path for the subfolder.
            image_src: the string representation of the scr for the image.
        '''
        
        try:
            # Download the image.  If timeout is exceeded, throw an error.
            image_content = requests.get(image_scr).content
            time.sleep(2)

        except Exception as e:
            print(f"ERROR - Could not download {image_scr} - {e}")
            
        try:
            # Convert the image into a bit stream, then save it.
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert("RGBA")
            with open(path, "wb") as f:
                image.save(f, "JPEG", quality=100)
            
        except Exception as e:
            print(f"ERROR - Could not save {image_scr} - {e}")
            
    def __check_if_file_exists(self, path):
        '''
        This function is used to check if image file exists. If it does, add the order in the title.

        Args:
            path: the string representation of the path for the new file.
        '''
        counter = 1
        while True:
            if not os.path.exists(path):
                return path
            else:
                path.split(".")
                path = path[0] + "_{counter}" + path[1]
                if not os.path.exists(path):
                    return path
                else:
                    counter += 1
                    
    def __createFolder(self, path):
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
    
    def __currency_folder(self, currency_dict, path):
        '''
        This function is used to create a raw_data folder and a UUID subfolder and saves the dictionary in the subfolder as a file called data.json.

        Args:
            link: the string representation of the link for a page. Will be from currency_link_list.
            path: the string representation of the path for the new folder.
        '''
        
        # Create raw_data folder 
        self.__createFolder(path)
        
        currency_id = currency_dict["Currency"]
        currency_id = currency_id.replace("/","")
        currency_path = path + f"{currency_id}"
    
        # Create ID folder 
        self.__createFolder(currency_path)
        
        # Save the dictionary as a file called data.json in a subfolder named after the id 
        with open(f"{currency_path}/data.json", "w") as fp:
            json.dump(currency_dict, fp)

    def __image_folder(self, currency_dict, link, path):
        '''
        This function is used to create a image folder and a image file and saves the image in the file.

        Args:
            currency_dict: the dictionary
            link: the string representation of the link for a page. Will be from currency_link_list.
            path: the string representation of the path for the new folder.
            
        '''
        
        currency_id = currency_dict["Currency"]
        currency_id = currency_id.replace("/","")
        image_scr = self.__get_image_link(link)
        image_folder_path = path + f"/{currency_id}/images"
        # Create image folder 
        self.__createFolder(image_folder_path)
        
        #Create file with the title in the form <date>_<time>_<order of image>.<image file extension>
        timestr = time.strftime('%d%m%Y_%H%M%S')
        image_file_path = image_folder_path + f"/{timestr}.jpg"
        self.__check_if_file_exists(str(image_file_path))
        
        #Download and save the image in the file created above
        
        img = self.__download_image(image_scr, image_file_path)
    
    def download_all_data(self, currency_dict, link, path):
        self.__currency_folder(currency_dict, path)
        self.__image_folder(currency_dict, link, path)
        print("Download completed!")
        
    def ScrapingTime(self):
        scrape.open_and_accept_cookie(URL)
        scrape.get_list_of_currency_links(currency_list)
        for link in self.currency_link_list:
            index = self.currency_link_list.index(link)
            path = "/Users/sarahaisagbon/Documents/GitHub/data-collection-pipeline/Project/raw_data/"
            currency_dict = self.create_currency_dictionary(link)
            # create a json file named after the id
            self.download_all_data(currency_dict, link, path)
        self.driver.quit()
    
if __name__ == "__main__":
    currency_list = ['GBP/USD', 'GBP/EUR', 'GBP/JPY', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF']
    URL = 'https://uk.finance.yahoo.com/currencies/'
    scrape = Scraper(URL, currency_list)
    scrape.ScrapingTime()
    