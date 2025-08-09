import os
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', '')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
GROBID_URL = os.getenv('GROBID_URL', 'http://localhost:8070')
VECTOR_INDEX = os.getenv('VECTOR_INDEX', 'lit_index')
