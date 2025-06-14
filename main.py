import os
import uuid
import logging
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core import crawl_website, generate_sitemap_xml

os.makedirs("logs", exist_ok=True)

log_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "_" + str(uuid.uuid4())[:8]
log_file_path = f"logs/crawler_{log_id}.log"

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path, mode='a'),
        logging.StreamHandler()
    ]
)

app = FastAPI()

class URLRequest(BaseModel):
    url: str
    depth: int = 1

@app.get("/")
def root():
    return {
        "message": "Website Crawler API is running. Visit /docs for the Swagger UI."
    }

@app.post("/generate_sitemap")
def generate_sitemap(request: URLRequest):
    try:
        logging.info(f"Generating sitemap for URL: {request.url} | Depth: {request.depth}")
        internal_links = crawl_website(request.url, max_depth=request.depth)
        sitemap_xml = generate_sitemap_xml(internal_links)
        return {
            "total_links": len(internal_links),
            "depth_used": request.depth,
            "sitemap": sitemap_xml
        }
    except Exception as e:
        logging.error(f"Error generating sitemap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download_sitemap")
def download_sitemap(request: URLRequest):
    try:
        logging.info(f"Generating downloadable sitemap for URL: {request.url} | Depth: {request.depth}")
        internal_links = crawl_website(request.url, max_depth=request.depth)
        file_path = "sitemap.xml"
        generate_sitemap_xml(internal_links, filename=file_path)
        return FileResponse(path=file_path, filename="sitemap.xml", media_type="application/xml")
    except Exception as e:
        logging.error(f"Error downloading sitemap: {e}")
        raise HTTPException(status_code=500, detail=str(e))
