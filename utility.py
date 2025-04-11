"""
Scraper Demo - Educational Use Only

This script demonstrates the use of Selenium for scraping product information
from e-commerce sites. It does not interact with any real websites unless modified.

Author: Yevheniia Tychynska
"""

import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def close_cookie_banner(driver, cookies_banner):
    try:
        # Wait for the cookie banner to appear (if present)
        cookie_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, cookies_banner))
        )
        cookie_button.click()
        print("Cookie banner closed.")
    except:
        print("No cookie banner found.")

def scrape_links(driver, prod_list_class, link_class, pagination_path):
    
    scraped_links = []
    
    while True:
        products_list = driver.find_elements(By.CLASS_NAME, prod_list_class)

        for product in products_list:
            product_link = product.find_element(By.CLASS_NAME, link_class).get_attribute("href")
            scraped_links.append(product_link)
        
        try:
            next_button = driver.find_element(By.XPATH, pagination_path) 
            #next button in disabled when the scraper reached the last page
            if next_button.get_attribute("button-disabled") == "true": # mentioned attribute's name is an example 
                break
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            next_button.click()
            time.sleep(2) 
        except Exception as e:
            print(f"Error clicking next button: {e}")
            break
        
    return scraped_links

def scrape_products_data(driver, class_names_dict):
    
    product_name = driver.find_element(By.CLASS_NAME, class_names_dict["prod_name_class"]).text 
    product_price = driver.find_element(By.CLASS_NAME, class_names_dict["prod_price_class"]).text 
    nutritional_info = driver.find_elements(By.CLASS_NAME, class_names_dict["nutri_info_class"]) 
    ingredients_info = driver.find_element(By.CLASS_NAME, class_names_dict["ingred_info_class"]).text.lower() 
    product_price = float(re.sub(r"[^\d.]", "", product_price)) # clean price string, make it decimal number: "1.99" => 1.99

    nutri_data = {
        "Calories" : None,
        "Fat": None,
        "Sugar": None,
        "Protein": None,
    }

    for data in nutritional_info:
        text = data.text.lower()
        if "energy" in text:
            match = re.search(r'(\d+)\s*kcal', data.text)  # Match numbers followed by 'kcal'
            if match:
                nutri_data["Calories"] = float(match.group(1))  # Store the matched text 
        elif "fat" in text:
            match = re.search(r'(\d+(\.\d+)?)\s*g', data.text)  # Match the first number followed by 'g' (for fat)
            if match:
                nutri_data["Fat"] = float(match.group(1))
            else:
                nutri_data["Fat"] = 0.0
        elif "sugars" in text:
            start = text.rfind("sugars")
            match = re.search(r'(\d+(\.\d+)?)\s*g', data.text[start:])
            if match:
                nutri_data["Sugar"] = float(match.group(1))
            else:
                nutri_data["Sugar"] = 0.0
        elif "protein" in text:
            match = re.search(r'(\d+(\.\d+)?)\s*g', data.text)
            if match:
                nutri_data["Protein"] = float(match.group(1))
            else:
                nutri_data["Protein"] = 0.0
    
    sweeteners = [ # sweeteners approved by European Food Safety Authority 
        "sorbitol", 
        "mannitol",
        "acesulfame", 
        "aspartame",
        "cyclamate",
        "isomalt",
        "saccharin",
        "sucralose",
        "thaumatin",
        "neohesperidine",
        "steviol",
        "stevia",
        "neotame",
        "polyglycitol",
        "maltitol",
        "lactitol",
        "xylitol",
        "erythritol",
        "advantame"
        ]

    # store sweetener's name into a list if the name is found among ingredients of a product
    sweeteners_in_product = [s for s in sweeteners if s in ingredients_info]

    product_data = {
        "name": product_name, 
        "price": product_price, 
        "nutritional_data": nutri_data,
        "sweeteners": sweeteners_in_product,
        }
    
    return product_data

def store_data_to_db(cursor, product_item, store_id):
    # store products name and store
    cursor.execute("""
        INSERT INTO products(product_name, store_id)
        VALUES (%s, %s)
    """, (product_item["name"], store_id))

    product_id = cursor.lastrowid # get the inserted product_id

    nutrition = product_item["nutritional_data"]
    sweeteners = product_item.get("sweeteners", []) # extract list of sweeteners from dictionary
    sweeteners_present = bool(sweeteners) # return True if list isn't empty

    # store nutritional data
    cursor.execute("""
        INSERT INTO nutritions (product_id, energy, fat, sugar, protein, sweeteners_present, sweeteners)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        product_id,
        nutrition.get("Calories"),
        nutrition.get("Fat"),
        nutrition.get("Sugar"),
        nutrition.get("Protein"),
        sweeteners_present,
        ', '.join(sweeteners)
    ))

    # store prices
    cursor.execute("""
        INSERT INTO prices (product_id, store_id, price)
        VALUES (%s, %s, %s)
    """, (
        product_id,
        store_id,
        product_item["price"]
    ))


