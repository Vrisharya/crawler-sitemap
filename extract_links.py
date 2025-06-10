from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def extract_all_links(driver):
    elems = driver.find_elements(By.TAG_NAME, "a")
    links = []
    for elem in elems:
        href = elem.get_attribute("href")
        if href and href.startswith("https://www.hashinverse.com"):
            links.append(href)
    return links

def extract_blog_links(driver):
    links = []
    blog_elements = driver.find_elements(By.CSS_SELECTOR, "a[href^='/blog/']")
    for elem in blog_elements:
        href = elem.get_attribute("href")
        if href and href.startswith("https://www.hashinverse.com/blog/"):
            links.append(href)
    return links

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(), options=options)

all_links = []

driver.get("https://www.hashinverse.com")
time.sleep(2)
all_links.extend(extract_all_links(driver))

driver.get("https://www.hashinverse.com/blogs")
time.sleep(3)
all_links.extend(extract_all_links(driver))
all_links.extend(extract_blog_links(driver))

try:
    page2_button = driver.find_element(By.XPATH, "//button[text()='2'] | //a[text()='2']")
    driver.execute_script("arguments[0].click();", page2_button)
    time.sleep(3)
    all_links.extend(extract_all_links(driver))
    all_links.extend(extract_blog_links(driver))
except Exception as e:
    print(" Could not click page 2:", e)

unique_links = sorted(list(set(all_links)))

print("\n===  All Unique Hashinverse URLs ===")
print("[")
for i, link in enumerate(unique_links):
    comma = "," if i != len(unique_links) - 1 else ""
    print(f'    "{link}"{comma}')
print("]")
print(f"\n Total unique links collected: {len(unique_links)}")

driver.quit()
