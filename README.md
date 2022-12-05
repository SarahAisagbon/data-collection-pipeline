# Data Collection Pipeline
## Milestone 1 & 2
### I set up a new environment in github and decided to collect data from yahoo.finance.
## Milestone 3
### I created a Scraper class that contain all methods used to scrape data from yahoo finance. A list of currencies and the url for the website will be inputs. I created a get_currency_link method that iterates through the given list. We get a list of links that will be used to navigate to the corresponding currency webpage. I also created an accept_cookie method to accept cookie and deals with any errors. make_curr_dict is a method to collect the data from yahoo finance and putting it in a dictionary.

### Code Used
```
    def __init__(self, URL, currency_list):
        self.currency_list = currency_list
        self.URL = URL
        self.driver = webdriver.Safari()
        self.id = str(uuid4())
        self.curr_link_list = []

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
    def create_list_of_curr_links(self, currency_list):
        for curr in currency_list:
            urlstr = '//a[@title="' + str(curr) + '"]'
            xpath = self.driver.find_element(By.XPATH, urlstr) # Change this xpath with the xpath the current page has in their properties
            link = xpath.get_attribute('href')
            self.currency_link_list.append(link)
            time.sleep(2)
            
        return self.currency_link_list
    
    def create_curr_dict(self, link):
        # get links from 
        self.driver.get(link)
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

```

## Milestone 4
### I focused on retrieving the information that I need. I created a method to get a image link on the website and then download it. I created a method to save the dictionary as a Json File. Depending on if the image has been saved before, the image is saved as <date>_<time>_<order of image>.<image file extension>.

```
    def create_currency_dictionary(self, link):
        
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
        
        self.driver.get(link)
        # get the summary tab
        self.driver.find_element(by=By.XPATH, value='//*[@id="quote-nav"]/ul/li[1]/a/span').click()
        time.sleep(1)
        
        # idetify the graph for logo
        img_property = WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//*[@id='uh-logo']"))).value_of_css_property("background-image")

        # get src of image
        image_src = str(re.split('[()]',img_property)[1])
        image_src = image_src[1:-1]
        
        return image_src

    def __download_image(self, image_scr, path):
        
        try:
            # Download the image.  If timeout is exceeded, throw an error.
            image_content = requests.get(image_scr).content
            time.sleep(2)

        except Exception as e:
            print(f"ERROR - Could not download {image_scr} - {e}")
            
        try:
            # Convert the image into a bit stream, then save it.
            image_file = io.BytesIO(image_content)
            image = Image.open(image_file).convert("RGB")
            with open(path, "wb") as f:
                image.save(f, "JPEG", quality=100)
            
        except Exception as e:
            print(f"ERROR - Could not save {image_scr} - {e}")
        
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
    
        def __currency_folder(self, currency_dict, path):
        
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

    def createjsonFile(self, dir,):
        # Create raw_data folder and a subfolder named after the id 
        self.createFolder(dir)
        # Save the dictionary as a file called data.json
        with open('{dir}/{self.id}/data.json', 'w') as fp:
            json.dump(self.currency_data, fp)

```
## Milestone 5
### First, I renamed some of the functions to be more clear. I rearranged the imports and from statement alphabetically. I made open_and_accept_cookie(self, URL), create_currency_dictionary(self, link), download_all_data(self, currency_dict, link, path) and ScrapingTime(self) into public methods. I added a Google docstring to each method. 

### Next, I created a unittest called Webscraping_Test. 

```

class ScraperTestCase(unittest.TestCase): 

    def test_accept_cookie(self):
        URL = "https://uk.finance.yahoo.com/currencies"
        actual_value = Scraper.open_and_accept_cookie(URL)
        expected_value = "Cookie Accepted"
        self.assertEqual(expected_value,actual_value)
    
    def setUp(self, URL = "https://uk.finance.yahoo.com/currencies", currency_list = ['GBP/USD', 'GBP/EUR', 'GBP/JPY', 'GBP/AUD', 'GBP/CAD', 'GBP/CHF']):
        self.scrape = Scraper(URL, currency_list) 
        self.URL = URL
        safariOptions = Options()
        safariOptions.headless = True
        
        '''
        desired_caps = {
            "platformName": 'MacOS Monterey',
            "browserName": 'safari',
            "browserVersion": '16.0'
        }
        '''
        
        safariOptions.BrowserName = "safari"
        safariOptions.BrowserVersion = "16.0"
        safariOptions.PlatformName = "MacOS Monterey"
        safariOptions.add_argument('--disable-extensions')
        
        #self.driver = webdriver.Safari(options = safariOptions)
        
        self.driver = webdriver.Safari(
            #command_executor='/usr/bin/safaridriver',
            executable_path = "/usr/bin/safaridriver",
            options = safariOptions
            #desired_capabilities= desired_caps
        )
        
        self.scrape.open_and_accept_cookie(self)
        self.link_list = self.scrape.__get_list_of_currency_links()
        self.currency_dict = self.scrape.create_currency_dictionary()
        self.currency_id = self.currency_dict["UUID"]
        self.path = "/Users/sarahaisagbon/Documents/GitHub/data-collection-pipeline/raw_data/"
    
    # tearDown runs after each test case
    def tearDown(self):
        self.driver.quit()
    
    #Check that all links are from the right website
    def test_link_list(self):
        non_website_list = list(filter(lambda x: x[:40] != 'https://uk.finance.yahoo.com/currencies', self.link_list))
        self.assertEqual(len(non_website_list), 0)
    
    #Check the length of the currency dictionary
    def test_currency_dictionary_length(self):
        values = self.currency_dict.values()
        expected_length = 5
        actual_length = len(values)
        self.assertEqual(expected_length, actual_length)
    
    #Check to see if the function create_currency_dictionary returns a dictionary
    def test_currency_dictionary_type(self):
        expected_value = dict
        actual_value = type(self.scrape.create_currency_dictionary("GBP/EUR"))
        self.assertEqual(expected_value,actual_value)
    
    #Check the values in the dictionary
    def test_currency_dictionary_values(self):
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
        path = self.path
        path_1 = path
        path_2 = path + "data.json"
        path_3 = path + "images/"
        path_4 = path + f"images/{imagefilename}.jpg"
        self.assertIsFolder(pl.Path(path_1))
        self.assertIsFile(pl.Path(path_2))
        self.assertIsFolder(pl.Path(path_3))
        self.assertIsFile(pl.Path(path_4))
    
    def test_ScrapingTime(self):
        link_list = self.scrape.currency_link_list
        random_index = random.randint(0, 4)
        random_link = link_list[random_index]
        
        self.driver.get(random_link)
        details_dict = self.scrape.create_currency_dictionary()
        self.driver.quit()
        self.scrape.download_all_data()
    
    ```

    ### I had troubles will running the unittest as it returns a selenium.common.exceptions.SessionNotCreatedException for each test.
   