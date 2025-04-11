"""
Scraper Demo - Educational Use Only

This script demonstrates the use of Selenium for scraping product information
from e-commerce sites. It does not interact with any real websites unless modified.

Author: Yevheniia Tychynska
"""

from selenium import webdriver
import utility

# Placeholder URL (replace with actual product URL if permitted)
link_to_scrape = "https://example.com/product"

# Set up headless Chrome
options = webdriver.ChromeOptions()
options.add_argument("--headless=new")  # Run without GUI
options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid bot detection
options.add_argument("user-agent=Mozilla/5.0")

driver = webdriver.Chrome(options=options)
driver.get(link_to_scrape) 

# handle cookie banner if it covers page content
cookies_banner = "trust-handler-class-example"
utility.close_cookie_banner(driver, cookies_banner)

# classes necessary to scrape required data, depend on a particular web site
# the classes below are not real classes but examples 
prod_list_class = "listing-class"
link_class = "link-holder-class"
pagination_path = "path-for-next-page-button"

# get links to the products 
products_links = utility.scrape_links(driver, prod_list_class, link_class, pagination_path)

# store links to a file if needed
for link in products_links:
    driver.get(link)
    with open("product_links.txt", "a") as file:
        file.write(link + "\n")
    
driver.quit()


