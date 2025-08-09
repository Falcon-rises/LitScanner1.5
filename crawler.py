# Minimal OpenAlex-based fetcher stub. Replace with robust crawler for production.
import httpx

OPENALEX_BASE = "https://api.openalex.org/works"

async def fetch_openalex(query: str, per_page: int = 25):
    params = {"search": query, "per-page": per_page}
    async with httpx.AsyncClient() as client:
        r = await client.get(OPENALEX_BASE, params=params, timeout=30)
        r.raise_for_status()
        return r.json()
