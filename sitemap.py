from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

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

def write_urls_to_sitemap(urls, output_file="sitemap.xml"):
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in urls:
        url_tag = ET.SubElement(urlset, "url")
        loc_tag = ET.SubElement(url_tag, "loc")
        loc_tag.text = url
    rough_string = ET.tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
    print(pretty_xml)

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(), options=options)

all_links = []

driver.get("https://www.hashinverse.com")
time.sleep(2)
scroll_to_bottom(driver)
all_links.extend(extract_all_links(driver))

driver.get("https://www.hashinverse.com/blogs")
time.sleep(2)
scroll_to_bottom(driver)
all_links.extend(extract_all_links(driver))
all_links.extend(extract_blog_links(driver))

try:
    page2_button = driver.find_element(By.XPATH, "//button[text()='2'] | //a[text()='2']")
    driver.execute_script("arguments[0].click();", page2_button)
    time.sleep(2)
    scroll_to_bottom(driver)
    all_links.extend(extract_all_links(driver))
    all_links.extend(extract_blog_links(driver))
except Exception as e:
    print(" Could not click page 2:", e)

unique_links = sorted(set(all_links))

write_urls_to_sitemap(unique_links, "sitemap.xml")

print(f"\n sitemap.xml created successfully with {len(unique_links)} URLs")

driver.quit()
