import concurrent
from mcp.server.fastmcp import FastMCP
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import logging
import mongoengine
import os

from CacheHit import CacheHit
from QueryProcessor import QueryProcessor
from APIClient import NewsAPIClient
from Chunking import chunking
from Ranking import ranking
from Evaluator import Evaluator
from CacheDB import CacheDB
from DeepSeekClient import DeepSeekClient

mcp = FastMCP("NewsDash")

load_dotenv()
try:
    mongodb_uri = os.environ["MONGO_URI"]
    logging.info(f"Connecting to MongoDB at {mongodb_uri}")
    mongoengine.connect(host=mongodb_uri)
    logging.info("MongoDB connection established")
except Exception as e:
    logging.error(f"Failed to connect to MongoDB: {e}")

embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)

deepseek_client = DeepSeekClient()
model = "deepseek-reasoner"

def format_chunks_for_llm(chunks):
    """Format chunks with metadata for LLM citation."""
    formatted_chunks = []
    
    for chunk in chunks:
        formatted_chunk = {
            "content": chunk.get("body", ""),
            "metadata": {
                "title": chunk.get("title", "Unknown Title"),
                "source": chunk.get("source", "Unknown Source"),
                "authors": chunk.get("authors", []),
                "date": chunk.get("date", "Unknown Date"),
                "url": chunk.get("url", ""),
            }
        }
        formatted_chunks.append(formatted_chunk)
    
    return formatted_chunks

@mcp.tool()
def search(query):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        can_answer_future = executor.submit(can_answer, query)
        embedding_future = executor.submit(embedding_model.encode, query)
    
    can_answer_result = can_answer_future.result()
    query_embedding = embedding_future.result()

    if not can_answer_result:
        return "The question cannot be answered."

    cached_answer, similarity = CacheHit(query_embedding)
    if cached_answer:
        logging.info(f"Cache hit with similarity {similarity}")
        return cached_answer

    query_processor = QueryProcessor(query, model)
    keywords = query_processor.query_processing()

    api_client = NewsAPIClient()

    articles = api_client.get_best_articles(keywords, count=5)

    if not articles:
        logging.warning("No articles found for the query")
        import nltk
        from nltk.corpus import stopwords
        from nltk.tokenize import word_tokenize
        try:
            nltk.data.find('corpora/stopwords')
        except nltk.downloader.DownloadError:
            nltk.download('stopwords')
        stop_words = set(stopwords.words('english'))
        word_tokens = word_tokenize(query)
        filtered_words = [w for w in word_tokens if not w.lower() in stop_words]
        
        for i in range(0, len(filtered_words), 2):
            query_chunk = ' '.join(filtered_words[i:i+2])
            articles = api_client.get_best_articles(query_chunk, count=5)
            if articles:
                logging.info(f"Found {len(articles)} articles with chunk: {query_chunk}")
                break
        
        if not articles:
            filtered_sentence = ' '.join(filtered_words)
            articles = api_client.get_best_articles(filtered_sentence, count=5)
            if not articles:
                logging.error(f"No articles found even after query refinement - {filtered_sentence}")
                return "The question cannot be answered. No relevant news articles were found."

    with concurrent.futures.ThreadPoolExecutor() as executor:
        chunking_futures = [executor.submit(chunking, article, embedding_model) for article in articles]
    
    chunks = []
    for future in concurrent.futures.as_completed(chunking_futures):
        chunks.extend(future.result())

    if not chunks:
        logging.warning("No chunks generated from articles")
        return "I couldn't process the articles found. Please try again."

    ranked_chunks = ranking(chunks, query_embedding)
    
    formatted_chunks = format_chunks_for_llm(ranked_chunks)

    prompt = f"""
    Summarize the following news article chunks to answer the user's query.
    User's Query: {query}
    Chunks: {formatted_chunks}
    
    Guidelines:
- Base your answer primarily on the provided context
- Prioritize the most relevant and recent information. The context is sorted by relevance where the most relevant information appears first.
- When using information from the context, cite the source based on the metadata provided like author, year, title, url, etc. In the text you can use author and year. But then at the end of the answer, provide a list of sources with full metadata after saying 'Sources'.
- If the context doesn't contain enough information, state this clearly
- Provide a clear, well-structured answer
    
    Answer:
    """

    response = deepseek_client.chat(
        messages=[
            {"role": "system", "content": "You are an expert summarizer. Summarize the following news article chunks to answer the user's query."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response["message"]["content"]
    answering_embedding = embedding_model.encode(answer)
    
    evaluator = Evaluator(ranked_chunks, query_embedding, embedding_model)
    score = evaluator.evaluate(answer, answering_embedding)
    logging.info(f"Evaluation score: {score}")

    if score < 0.8:
        logging.info("Answer score below threshold, initiating drafting process.")
        answer = evaluator.drafting(answer)
        score = evaluator.evaluate(answer, answering_embedding)
    
    evaluation_text = evaluator.format_evaluation_results()
    final_answer = f"{answer}\n\nEvaluation:\n{evaluation_text}"

    try:
        if score >= 0.65:
            CacheDB(
                query=query,
                answer=final_answer,
                embedding=embedding_model.encode(answer),
            ).save()
            logging.info("Successfully saved to cache")
    except Exception as e:
        logging.error(f"Failed to save to cache: {e}")
    
    return final_answer
        

@mcp.tool()
def can_answer(query):
    response = deepseek_client.chat(
        messages=[
            {"role": "system", "content": "You are an expert at determining if a question can be answered with news articles"},
            {"role": "user", "content": f"Can this question be answered with news articles? Question: {query}. Say 'true' or 'false'."}
        ]
    )
    if "true" in response["message"]["content"].lower():
        return True
    return False

if __name__ == "__main__":
    logging.info("Starting MCP server...")
    mcp.run(transport="stdio")