# Simple sentence-transformers based embeddings for local testing
from sentence_transformers import SentenceTransformer
import numpy as np

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def embed_texts(texts):
    model = get_model()
    embs = model.encode(texts, show_progress_bar=False)
    return np.asarray(embs)
