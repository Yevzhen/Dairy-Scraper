"""
Scraper Demo - Educational Use Only

This script demonstrates the use of Selenium for scraping product information
from e-commerce sites. It does not interact with any real websites unless modified.

Author: Yevheniia Tychynska
"""

from selenium import webdriver
import mysql.connector
import utility

options = webdriver.ChromeOptions()
options.add_argument("--headless=new") # no GUI
options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(options=options)

# Placeholder URL (replace with actual product URL if permitted)
link_to_scrape = "https://example.com/product"
driver.get(link_to_scrape)

# classes depend on a particular web site 
class_names_dict = {
    "prod_name_class": "product-title-class",
    "prod_price_class": "product-price-class",
    "nutri_info_class": "nutri-data-class",
    "ingred_info_class": "ingredients-info-class"
    }

# get necessary data
product_data = utility.scrape_products_data(driver, class_names_dict)

#prepare database connection to store scraped data
db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="", # no pass
    database="dairy_db"
)

cursor=db.cursor()

#store to DB
utility.store_data_to_db(cursor, product_data, store_id=1)
db.commit() 

# clean up
cursor.close()
db.close()
driver.quit()
