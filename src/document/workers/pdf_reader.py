from PyPDF2 import PdfReader
from io import BytesIO
from celery import Celery
import os 


app = Celery(
    "pdf_reader",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379")
)

@app.task
def extract_text_from_pdf(content:bytes) -> str:
    reader = PdfReader(BytesIO(content)) # create new file with BytesIO wrapper => keeps file properties like read
    pages = []
    for page in reader.pages:
        page_string = page.extract_text()
        pages.append(page_string)
    return "\n".join(pages)