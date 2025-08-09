# Minimal in-memory vector index for scaffolding. Use Pinecone/Weaviate in prod.
from sklearn.neighbors import NearestNeighbors
import numpy as np

_index = None
_vectors = None
_metadata = []


def init_index(vectors):
    global _index, _vectors
    _vectors = np.array(vectors)
    _index = NearestNeighbors(n_neighbors=10, algorithm='auto').fit(_vectors)


def query(vec, topk=10):
    if _index is None:
        return []
    dist, idx = _index.kneighbors([vec], n_neighbors=topk)
    return [(i, float(d)) for i, d in zip(idx[0], dist[0])]


def add(vectors, metas):
    global _vectors, _metadata, _index
    if _vectors is None:
        _vectors = np.array(vectors)
        _metadata = metas
    else:
        _vectors = np.concatenate([_vectors, np.array(vectors)], axis=0)
        _metadata.extend(metas)
    _index = NearestNeighbors(n_neighbors=10, algorithm='auto').fit(_vectors)
