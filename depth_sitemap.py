import argparse
from urllib.parse import urlparse
from collections import deque
from selenium.webdriver.support.ui import WebDriverWait
from core import (
    crawl_website, generate_sitemap_xml,
    init_driver, is_html_response,
    scroll_to_bottom, extract_internal_links
)

def crawl_with_depth(start_url, max_depth):
    domain = urlparse(start_url).netloc
    visited = set()
    queue = deque([(start_url.rstrip('/'), 0)])
    all_links = set()
    driver = init_driver()

    while queue:
        current_url, depth = queue.popleft()
        if current_url in visited or depth > max_depth:
            continue

        try:
            driver.get(current_url)
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            if not is_html_response(driver):
                continue
            scroll_to_bottom(driver)
            links = extract_internal_links(driver, current_url, domain)
            new_links = links - visited
            queue.extend([(link, depth + 1) for link in new_links])
            all_links.add(current_url)
            visited.add(current_url)
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")
            visited.add(current_url)

    driver.quit()
    return sorted(all_links)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sitemap with optional crawling depth.")
    parser.add_argument("--url", required=True, help="Starting URL for crawling")
    parser.add_argument("--depth", type=int, default=1, help="Crawling depth (default is 1)")
    parser.add_argument("--output", default="sitemap.xml", help="Output sitemap file name")

    args = parser.parse_args()

    print(f"Crawling: {args.url} with depth {args.depth}")
    print("Generating sitemap...")

    links = crawl_with_depth(args.url, args.depth)
    generate_sitemap_xml(links, filename=args.output)

    print(f" Sitemap generated: {args.output} ({len(links)} links)")
