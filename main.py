import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core import crawl_website, generate_sitemap_xml

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)

app = FastAPI()

class URLRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {
        "message": "Website Crawler API is running. Visit /docs for the Swagger UI."
    }

@app.post("/generate_sitemap")
def generate_sitemap(request: URLRequest):
    try:
        logging.info(f"Generating sitemap for URL: {request.url}")
        internal_links = crawl_website(request.url)
        sitemap_xml = generate_sitemap_xml(internal_links)
        return {
            "total_links": len(internal_links),
            "sitemap": sitemap_xml
        }
    except Exception as e:
        logging.error(f"Error generating sitemap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download_sitemap")
def download_sitemap(request: URLRequest):
    try:
        logging.info(f"Generating downloadable sitemap for URL: {request.url}")
        internal_links = crawl_website(request.url)
        file_path = "sitemap.xml"
        generate_sitemap_xml(internal_links, filename=file_path)
        return FileResponse(path=file_path, filename="sitemap.xml", media_type="application/xml")
    except Exception as e:
        logging.error(f"Error downloading sitemap: {e}")
        raise HTTPException(status_code=500, detail=str(e))
