# LitHybrid Flat Scaffold

This repository contains a flat-file scaffold for a LitScanner-style hybrid summarization system. Files are intentionally stored without folders for easy copy-paste into a single GitHub directory as requested.

**Not production ready.** Use as a starting point. Important components are stubbed and must be replaced with robust implementations (crawler, parser, vector DB, LLM integration, auth).

## How to run (backend)

1. Create a virtualenv and install requirements: `pip install -r requirements.txt`
2. Start Redis (or set REDIS_URL in .env)
3. Run the FastAPI app: `uvicorn main:app --reload --port 8000`

## How to run (frontend)

1. `npm install`
2. `npm run dev`


## Files included
- Backend: main.py, tasks.py, crawler.py, parser.py, embeddings.py, vectordb.py, summarizer.py, worker.py, config.py, requirements.txt, Dockerfile.backend
- Frontend: index.jsx, package.json, next.config.js, api_client.js, styles.css, Dockerfile.frontend
- Misc: .gitignore, env.example, Procfile, README.md, LICENSE
