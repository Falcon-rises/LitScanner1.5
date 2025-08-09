# Grobid call stub -- assumes a running GROBID instance for structured extraction
import requests
import config


def parse_pdf_binary(pdf_bytes: bytes):
    url = f"{config.GROBID_URL}/api/processFulltextDocument"
    files = {"input": ('paper.pdf', pdf_bytes)}
    r = requests.post(url, files=files, timeout=120)
    r.raise_for_status()
    return r.text  # XML returned by GROBID
