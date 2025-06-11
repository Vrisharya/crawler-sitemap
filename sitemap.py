from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, urljoin
from webdriver_manager.chrome import ChromeDriverManager
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import logging
import time
import datetime
import mimetypes

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def init_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def scroll_to_bottom(driver, pause_time=2, max_scrolls=10):
    """ Scrolls to the bottom of the page to load dynamic content """
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def is_html_response(driver):
    try:
        content_type = driver.execute_script("return document.contentType")
        return content_type.startswith("text/html")
    except:
        return False

def extract_internal_links(driver, base_url, domain):
    internal_links = set()
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    except:
        logging.warning(f"⏳ Timeout waiting for links on {base_url}")
    anchors = driver.find_elements(By.TAG_NAME, "a")
    for anchor in anchors:
        href = anchor.get_attribute("href")
        if href:
            href = urljoin(base_url, href.split('#')[0].split('?')[0].strip())
            parsed_href = urlparse(href)
            if parsed_href.netloc == domain and parsed_href.scheme in ["http", "https"]:
                internal_links.add(href.rstrip('/'))
    return internal_links

def crawl_website(start_url):
    domain = urlparse(start_url).netloc
    visited = set()
    queue = [start_url.rstrip('/')]
    all_links = set()
    driver = init_driver()

    while queue:
        current_url = queue.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)

        try:
            driver.get(current_url)
            if not is_html_response(driver):
                logging.warning(f"⚠️ Skipping non-HTML content: {current_url}")
                continue
            scroll_to_bottom(driver)
            links = extract_internal_links(driver, current_url, domain)
            new_links = links - visited - set(queue)
            queue.extend(new_links)
            all_links.add(current_url)
            logging.info(f"Crawled: {current_url} | Found: {len(links)} links")
        except Exception as e:
            logging.error(f"❌ Failed to crawl {current_url}: {e}")

    driver.quit()
    return sorted(all_links)

def convert_to_sitemap_xml(urls, filename="sitemap.xml"):
    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    today = datetime.datetime.now(datetime.UTC).date().isoformat()

    for url in urls:
        url_element = SubElement(urlset, "url")
        SubElement(url_element, "loc").text = url
        SubElement(url_element, "lastmod").text = today
        SubElement(url_element, "changefreq").text = "monthly"
        SubElement(url_element, "priority").text = "0.8"

    rough_string = tostring(urlset, 'utf-8')
    reparsed = parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    logging.info(f"✅ Sitemap generated and saved to: {filename}")
    print("\n📄 Generated sitemap.xml content:\n")
    print(pretty_xml)

if __name__ == "__main__":
    url = input("Enter the URL to extract internal links: ").strip()
    internal_links = crawl_website(url)
    convert_to_sitemap_xml(internal_links, "sitemap.xml")
