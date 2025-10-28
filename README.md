# NewsDash

> **Multi-layer RAG for quick access to knowledge about current politics, science, economy, and more!**

NewsDash is an intelligent news aggregation and question-answering system that leverages state-of-the-art retrieval-augmented generation (RAG) techniques to provide accurate, cited answers to questions about current events. The system retrieves relevant news articles, processes them through semantic chunking and ranking, and generates comprehensive answers with source citations.

## 🌟 Features

- **Multi-Layer RAG Architecture**: Combines semantic search, chunking, and ranking for optimal information retrieval
- **Intelligent Query Processing**: Breaks down complex queries into multiple search terms for better article retrieval
- **Semantic Caching**: MongoDB-backed caching system with similarity-based retrieval (85% threshold)
- **Source Citation**: Automatically cites sources with metadata (author, date, title, URL)
- **Answer Quality Evaluation**: Multi-metric evaluation system including:
  - Chunk-to-query similarity
  - Chunk-to-answer similarity (grounding)
  - Query-to-answer similarity (relevance)
- **Iterative Refinement**: Automatic answer improvement when quality scores fall below threshold (0.8)
- **Model Context Protocol (MCP) Integration**: Exposes functionality via MCP server for integration with AI assistants
- **Web Interface**: Clean, modern UI for interactive queries

## 🏗️ Architecture

### Backend (Python)

#### Core Components

1. **MCPServer.py**: FastMCP server exposing two main tools:
   - `search(query)`: Main entry point for question answering
   - `can_answer(query)`: Validates if a question can be answered with news articles

2. **APIClient.py**: EventRegistry API integration for news article retrieval
   - Fetches relevant articles based on keywords
   - Supports sorting by relevance and date filtering (31-day window)

3. **QueryProcessor.py**: Intelligent query decomposition
   - Uses DeepSeek LLM to generate 3 optimized search keywords
   - Extracts relevant terms while removing noise

4. **Chunking.py**: Article segmentation
   - Splits articles into 5-sentence chunks
   - Generates embeddings for each chunk using `all-MiniLM-L6-v2`

5. **Ranking.py**: Semantic ranking system
   - Computes cosine similarity between query and chunks
   - Returns top 5 most relevant chunks

6. **CacheHit.py**: Smart caching layer
   - MongoDB-based cache with embedding similarity search
   - 85% similarity threshold for cache hits

7. **Evaluator.py**: Answer quality assessment
   - Multi-metric scoring (chunk-query, chunk-answer, query-answer)
   - Visual feedback (🟢 Excellent, 🟡 Good, 🟠 Fair, 🔴 Poor)

8. **DrafterAgent.py**: Iterative answer improvement
   - Assesses answer quality along multiple dimensions
   - Redrafts answers when grounding or relevance is insufficient

9. **DeepSeekClient.py**: LLM integration
   - Uses DeepSeek R1 via OpenRouter API
   - Handles query processing, answer generation, and refinement

10. **CacheDB.py**: MongoDB schema definition
    - Stores query, answer, embedding, and timestamp

### Frontend (Node.js + Express)

- **server.js**: Express server with MCP client integration
- **MCPClientManager.js**: Manages MCP client connection to Python server
- **public/index.html**: Modern web interface with:
  - Dark/light theme toggle
  - Real-time query processing
  - Source citation display

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 14.x or higher
- **MongoDB**: Running instance (local or cloud)
- **API Keys**:
  - EventRegistry API key ([Get one here](https://eventregistry.org/))
  - OpenRouter API key for DeepSeek R1 ([Get one here](https://openrouter.ai/))

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/CODERTG2/NewsDash.git
cd NewsDash
```

### 2. Python Environment Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Required Python packages:**
```
mcp
fastmcp
sentence-transformers
mongoengine
python-dotenv
requests
scikit-learn
numpy
nltk
```

### 3. Node.js Setup

```bash
npm install
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017/newsdash
# Or use MongoDB Atlas:
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/newsdash

# EventRegistry API Key
API_KEY=your_eventregistry_api_key_here

# OpenRouter API Key (for DeepSeek R1)
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 5. Download NLTK Data (First Run)

The system will automatically download required NLTK data on first run, but you can pre-download:

```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

## 🎯 Usage

### Option 1: MCP Server (Direct)

Run the MCP server directly for integration with AI assistants:

```bash
mcp dev src/MCPServer.py
```

### Option 2: Web Interface

1. Start the Express server (which automatically starts the MCP server):

```bash
npm start
```

2. Open your browser to `http://localhost:3000`

3. Enter your question in the interface and get answers with citations!

### Example Queries

- "What are the latest developments in AI regulation?"
- "Who won the Nobel Prize in Physics in 2024?"
- "What is the current status of climate change negotiations?"
- "What are the recent breakthroughs in quantum computing?"

## 🔄 System Flow

```mermaid
graph TD
    A[User Query] --> B{Cache Hit?}
    B -->|Yes| C[Return Cached Answer]
    B -->|No| D[Query Processing]
    D --> E[Generate Keywords]
    E --> F[Fetch Articles via EventRegistry]
    F --> G[Chunk Articles]
    G --> H[Generate Embeddings]
    H --> I[Rank Chunks]
    I --> J[Generate Answer with DeepSeek]
    J --> K{Score >= 0.8?}
    K -->|No| L[Refine Answer]
    K -->|Yes| M[Format with Citations]
    L --> M
    M --> N[Cache Result]
    N --> O[Return Answer]
```

## 📊 Performance Optimization

- **Concurrent Processing**: Parallel execution for chunking and embedding generation
- **Smart Caching**: 85% similarity threshold reduces API calls
- **Query Refinement**: Automatic fallback to filtered queries if no articles found
- **Top-K Retrieval**: Only processes top 5 most relevant chunks

## 🛠️ Configuration

### Adjustable Parameters

**In MCPServer.py:**
- `similarity_threshold` (default: 0.85): Cache hit threshold
- `count` (default: 5): Number of articles to retrieve
- `sentences_per_chunk` (default: 5): Chunk size in Chunking.py
- `top_k` (default: 5): Number of chunks to rank in Ranking.py

**In DeepSeekClient.py:**
- `temperature` (default: 0.7): LLM creativity parameter

## 📝 API Endpoints

### Express Server

- `GET /`: Web interface
- `POST /api/mcp`: MCP tool invocation
  ```json
  {
    "name": "search",
    "arguments": {
      "query": "Your question here"
    }
  }
  ```

### MCP Tools

- `search(query: str)`: Main Q&A function
- `can_answer(query: str)`: Validates question answerability

## 🧪 Testing

```bash
# Test the MCP server
python -c "from src.MCPServer import search; print(search('What is the latest news on AI?'))"
```

## 📦 Project Structure

```
NewsDash/
├── src/
│   ├── MCPServer.py          # FastMCP server with search & can_answer tools
│   ├── APIClient.py          # EventRegistry API client
│   ├── QueryProcessor.py     # Query decomposition & keyword extraction
│   ├── Chunking.py           # Article chunking with embeddings
│   ├── Ranking.py            # Semantic similarity ranking
│   ├── CacheHit.py           # Cache retrieval logic
│   ├── CacheDB.py            # MongoDB schema
│   ├── Evaluator.py          # Answer quality evaluation
│   ├── DrafterAgent.py       # Answer refinement agent
│   ├── DeepSeekClient.py     # DeepSeek LLM client
│   └── util.py               # Cosine similarity utility
├── public/
│   └── index.html            # Web interface
├── server.js                 # Express server
├── MCPClientManager.js       # MCP client manager
├── package.json              # Node.js dependencies
├── .env                      # Environment variables (create this)
└── README.md                 # This file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **EventRegistry**: For comprehensive news article API
- **DeepSeek**: For powerful reasoning capabilities
- **Sentence Transformers**: For semantic embeddings
- **Model Context Protocol**: For standardized AI integration
- **MongoDB**: For flexible document storage

## 📧 Contact

**Tanmay Shubh Garg**
- GitHub: [@CODERTG2](https://github.com/CODERTG2)
- Repository: [NewsDash](https://github.com/CODERTG2/NewsDash)

## 🔮 Future Enhancements

- [ ] Multi-language support
- [ ] Real-time news streaming
- [ ] User authentication and personalized feeds
- [ ] Advanced analytics dashboard
- [ ] Export answers as PDF/Markdown
- [ ] Integration with more news sources
- [ ] Fine-tuned embedding models
- [ ] GraphQL API
- [ ] Mobile application

---

**Made with ❤️ by the NewsDash Team**
