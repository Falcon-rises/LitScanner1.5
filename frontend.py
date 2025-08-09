"""
frontend.py
Streamlit frontend to:
- Poll /api/projects/:id/status
- Fetch /api/projects/:id/papers (full metadata)
- Format all papers into APA 7th entries
- Allow streaming download as .txt (chunked, memory-conscious)
"""
import os
import time
import json
import requests
import streamlit as st
from typing import List, Dict, Any
from io import StringIO, BytesIO
import tempfile

# CONFIG - set your deployed API base (or localhost for local dev)
API_BASE = os.getenv("API_BASE", "https://your-vercel-domain.vercel.app")  # Replace or set env

st.set_page_config(page_title="LitHybrid APA Export", layout="wide")

st.title("LitHybrid — APA 7th Bibliography Export (Streamlit)")

with st.sidebar:
    st.header("Settings")
    api_base_input = st.text_input("API base URL", API_BASE)
    API_BASE = api_base_input.strip().rstrip("/")
    project_id = st.text_input("Project ID (UUID)", "")

    poll_interval = st.number_input("Poll interval (sec)", min_value=1, max_value=60, value=3)
    max_preview = st.number_input("Preview first N entries", min_value=1, max_value=5000, value=20)

if not project_id:
    st.info("Enter a project ID to get started (created by API /api/projects).")
    st.stop()

# helper requests
def api_get(path: str):
    url = API_BASE + path
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

# Basic status poller
status_box = st.empty()
progress_bar = st.progress(0)
if st.button("Fetch status now"):
    try:
        status = api_get(f"/api/projects/{project_id}/status")
        status_box.json(status)
        try:
            progress_bar.progress(int(status.get("progress", 0)))
        except Exception:
            pass
    except Exception as e:
        st.error(f"Status fetch error: {e}")

# Auto-poll until done
if st.button("Start auto-poll until done"):
    with st.spinner("Polling..."):
        while True:
            try:
                status = api_get(f"/api/projects/{project_id}/status")
                status_box.json(status)
                prog = int(status.get("progress", 0))
                progress_bar.progress(min(max(prog, 0), 100))
                if status.get("status") in ("done", "failed"):
                    st.success(f"Status: {status.get('status')}")
                    break
            except Exception as e:
                st.error(f"Polling error: {e}")
                break
            time.sleep(poll_interval)

# Fetch papers endpoint
if st.button("Fetch papers (HEADS UP: large!)"):
    try:
        st.info("Requesting papers list from server...")
        papers = api_get(f"/api/projects/{project_id}/papers")
        # Expecting JSON: { "project_id": ..., "papers": [ {paper metadata}, ... ] }
        papers_list = papers.get("papers") or []
        st.success(f"Fetched {len(papers_list)} papers")
        st.write("Preview (first entries):")
        st.write(papers_list[:max_preview])
        st.session_state['papers_list'] = papers_list
    except Exception as e:
        st.error(f"Fetch papers error: {e}")

# Format authors to APA
def format_authors_apa(authorships: List[Dict[str, Any]]) -> str:
    """
    Convert OpenAlex-style authorship list to APA author string.
    authorship: list of {'author': {'display_name':'First Last', 'id':...}, 'raw_affiliation_string':...}
    APA rules (simplified):
     - 1 author: Last, F. M.
     - 2 authors: A & B
     - 3-20 authors: comma separated with & before last
     - >20 authors: first 19, ellipsis, last author
    This function is a best-effort; for production, use a dedicated bibliographic parser.
    """
    if not authorships:
        return ""
    names = []
    for a in authorships:
        au = a.get('author') or {}
        name = au.get('display_name') or au.get('name') or ""
        # split into parts
        parts = name.strip().split()
        if len(parts) == 0:
            continue
        last = parts[-1]
        initials = " ".join([p[0].upper() + "." for p in parts[:-1]])
        formatted = f"{last}, {initials}".strip()
        names.append(formatted)
    n = len(names)
    if n == 0:
        return ""
    if n == 1:
        return names[0]
    if 2 <= n <= 20:
        return ", ".join(names[:-1]) + ", & " + names[-1]
    # >20
    first19 = names[:19]
    last = names[-1]
    return ", ".join(first19) + ", ... " + last

def format_apa_entry(paper: Dict[str, Any]) -> str:
    """
    Build an APA 7th formatted string for a single paper record.
    Expected paper keys: title, publication_year, venue (journal_name), doi, authorship (OpenAlex authorship), id, url
    This is a best-effort formatter.
    """
    title = paper.get('title') or paper.get('display_name') or ""
    year = paper.get('publication_year') or paper.get('year') or "n.d."
    authorship = paper.get('authorships') or paper.get('authors') or []
    authors_str = format_authors_apa(authorship)
    venue = paper.get('journal', {}).get('name') if isinstance(paper.get('journal'), dict) else paper.get('venue') or paper.get('host_venue') or ""
    doi = paper.get('doi') or paper.get('ids', {}).get('doi') if isinstance(paper.get('ids'), dict) else paper.get('doi')
    url = paper.get('id') or paper.get('url') or paper.get('source_url') or ""
    # Clean up components
    if not authors_str:
        authors_str = ""
    # APA entry: Authors (Year). Title. Venue, volume(issue), pages. DOI/URL
    entry_parts = []
    if authors_str:
        entry_parts.append(f"{authors_str} ({year}).")
    else:
        entry_parts.append(f"({year}).")
    entry_parts.append(f" {title}.")
    if venue:
        entry_parts.append(f" {venue}.")
    # DOI or URL
    if doi:
        if not doi.startswith("http"):
            doi_str = f" https://doi.org/{doi}"
        else:
            doi_str = f" {doi}"
        entry_parts.append(doi_str)
    elif url:
        entry_parts.append(f" {url}")
    return "".join(entry_parts).strip()

# Preview and download
papers_list = st.session_state.get('papers_list', None)
if papers_list:
    st.header("APA Preview")
    n = len(papers_list)
    st.write(f"Total papers available from server: {n}")
    preview_n = min(max_preview, n)
    for p in papers_list[:preview_n]:
        st.markdown("- " + format_apa_entry(p))

    # Streaming download function - writes to temp file in chunks to avoid memory blowup
    def generate_apa_txt_stream(papers_iterable):
        # yields bytes
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = tmpdir + "/bibliography_apa.txt"
            with open(out_path, "w", encoding="utf-8") as f:
                for i, p in enumerate(papers_iterable, start=1):
                    entry = format_apa_entry(p)
                    f.write(f"{i}. {entry}\n")
                    # flush periodically
                    if i % 1000 == 0:
                        f.flush()
            # read file and return bytes
            with open(out_path, "rb") as fr:
                data = fr.read()
            return data

    if st.button("Generate APA .txt and download"):
        with st.spinner("Generating APA file (this may take a while for 70k entries)..."):
            try:
                data = generate_apa_txt_stream(papers_list)
                st.download_button("Download APA 7 bibliography (.txt)", data=data, file_name=f"bibliography_{project_id}_APA7.txt", mime="text/plain")
                st.success("Ready for download.")
            except Exception as e:
                st.error(f"Error building file: {e}")

else:
    st.info("No papers loaded. Click 'Fetch papers' to request the full list from the API.")
