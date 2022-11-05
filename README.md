# Data Collection Pipeline
## Milestone 1 & 2
### I set up a new environment in github and decided to collect data from yahoo.finance.
## Milestone 3
### I created a Scraper class that contain all methods used to scrape data from yahoo finance. I created a get_currency_urls method to get a list of urls for each currency. Then, I used the list in get_currency_driver method to navigate to the corresponding currency webpage. I also created an accept_cookie method to accept cookie and deals with any errors. make_curr_dict is a method to collect the data from yahoo finance and putting it in a dictionary.