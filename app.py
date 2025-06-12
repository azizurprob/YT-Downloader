from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess
import os
import uuid

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/download", response_class=HTMLResponse)
def download(request: Request, url: str = Form(...)):
    video_id = str(uuid.uuid4())
    output_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")

    try:
        subprocess.run([
            "yt-dlp",
            url,
            "-o", output_path,
            "--no-playlist",
        ], check=True)

        for filename in os.listdir(DOWNLOAD_DIR):
            if video_id in filename:
                download_url = f"/static/{filename}"
                os.rename(os.path.join(DOWNLOAD_DIR, filename), f"static/{filename}")
                return templates.TemplateResponse("download.html", {"request": request, "file_url": download_url})

        return templates.TemplateResponse("error.html", {"request": request, "message": "File not found."})

    except subprocess.CalledProcessError:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Download failed."})
