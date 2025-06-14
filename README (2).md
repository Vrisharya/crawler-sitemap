# Website Sitemap Crawler and API

This project provides a comprehensive solution for crawling a website, extracting internal links, and generating a valid `sitemap.xml` file. It supports both command-line and REST API interfaces and can handle dynamic content, depth control, logging, and file output.

---

## Project Structure

| File              | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `core.py`         | Core crawling and sitemap generation logic                                  |
| `main.py`         | FastAPI application with endpoints to generate and download sitemaps        |
| `depth_sitemap.py`| Command-line interface for crawling a website with specified depth          |

---

## Features

- Depth-controlled recursive crawling of websites
- Dynamic content handling (JavaScript-loaded elements)
- Internal link filtering
- XML sitemap generation
- FastAPI-based REST interface
- Unique logging for each API session
- Command-line tool for standalone use

---

## Prerequisites

Ensure Python 3.8 or above is installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

Required libraries include:
- `selenium`
- `fastapi`
- `uvicorn`
- `pydantic`
- `webdriver-manager`

---

## How to Run

### 1. Run as API

Start the API server:

```bash
uvicorn main:app --reload
```

Access the API Swagger UI at:
```
http://127.0.0.1:8000/docs
```

### 2. API Endpoints

#### `POST /generate_sitemap`

Input:
```json
{
  "url": "https://example.com",
  "depth": 2
}
```

Response:
- `total_links`: Number of internal pages found
- `depth_used`: Depth used for crawling
- `sitemap`: XML string of sitemap content

#### `POST /download_sitemap`

Same input as above. Triggers a download of the generated `sitemap.xml`.

---

### 3. Run via CLI

Use the command-line interface using:

```bash
python depth_sitemap.py --url https://example.com --depth 2 --output sitemap.xml
```

This saves the sitemap to `sitemap.xml`.

---

## Logging

Each API session generates a unique log file in the `/logs` directory:

Example log filename:
```
logs/crawler_20250614-143211_4c8e3f2d.log
```

Log entries include:
- Sitemap generation requests
- Crawled URLs with depth
- Retry attempts and warnings

---

## File Breakdown

### `core.py`

Defines the following core functions:
- `init_driver()`: Initializes Selenium WebDriver
- `scroll_to_bottom()`: Handles dynamic content loading
- `extract_internal_links()`: Gathers internal links
- `crawl_website()`: Depth-aware recursive crawler
- `generate_sitemap_xml()`: Writes links to formatted XML file

### `depth_sitemap.py`

CLI wrapper that:
- Parses arguments for URL, depth, and output file
- Uses BFS traversal to crawl with depth control
- Outputs `sitemap.xml` with link structure

### `main.py`

Defines FastAPI application with:
- `/`: Root check
- `/generate_sitemap`: Returns sitemap XML and link count
- `/download_sitemap`: Returns sitemap XML as downloadable file
- Uses session-based logging to store logs in `logs/`

---

## Notes

- Only internal links are included in the sitemap.
- External or non-HTML content (e.g., PDFs) is ignored.
- Dynamic sites are supported via scrolling and wait mechanisms.
- Logging helps with debugging and performance analysis.

---

## Author and Acknowledgement

Developed by Shravya as part of academic project work under the guidance of Rakshith Kalmadi.

For any questions, refer to the Swagger UI or log files.