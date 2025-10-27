def chunking(article, model, sentences_per_chunk=5):
    """Set sentence chunking for articles."""
    text = article["body"]
    sentences = text.split(". ")
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk_sentences = sentences[i:i + sentences_per_chunk]
        chunk_text = ". ".join(chunk_sentences)
        
        if chunk_text and not chunk_text.endswith("."):
            chunk_text += "."
        
        chunk_dict = article.copy()
        
        chunk_dict["body"] = chunk_text
        chunk_dict["embedding"] = model.encode(chunk_text)
        chunks.append(chunk_dict)
    
    return chunks