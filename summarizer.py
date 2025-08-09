# Very small map-reduce style summarizer stub
from embeddings import embed_texts


def extractive_sample(texts, topk=3):
    # rudimentary: return first sentences
    out = []
    for t in texts:
        s = t.split('.')[:topk]
        out.append('.'.join(s).strip() + '.')
    return '\n'.join(out)


def compose_summary(cluster_summaries):
    return '\n\n'.join(cluster_summaries)
