from util import cosine_similarity
import numpy as np

def ranking(chunks, query_embedding):
    """Rank chunks based on similarity to the query embedding."""
    ranked_chunks = []
    for chunk in chunks:
        chunk_embedding = np.array(chunk["embedding"])
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        ranked_chunks.append((similarity, chunk))
    
    ranked_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in ranked_chunks[:5]]