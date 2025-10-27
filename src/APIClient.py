import os
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

# Tested!
class NewsAPIClient:
    def __init__(self):
        self.api_key = os.getenv('API_KEY')
        if not self.api_key:
            raise ValueError("API_KEY not found in environment variables")
        self.base_url = "https://eventregistry.org/api/v1"
        self.search_endpoint = f"{self.base_url}/article/getArticles"
    
    def search_articles(
        self, 
        query: str,
        count: int = 2,
        sort_by: str = "rel",
        lang: Optional[str] = "eng"
    ) -> List[Dict]:
        # Build query using EventRegistry complex query structure
        payload = {
            "action": "getArticles",
            "keyword": query,
            "articlesPage": 1,
            "articlesCount": min(count, 100),
            "articlesSortBy": sort_by,
            "articlesSortByAsc": False,
            "articlesArticleBodyLen": -1,
            "resultType": "articles",
            "dataType": ["news"],
            "apiKey": self.api_key,
            "forceMaxDataTimeWindow": 31
        }
        
        if lang:
            payload["lang"] = lang
        
        try:
            response = requests.post(
                self.search_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            response.raise_for_status()
            
            data = response.json()
            
            if "articles" in data and "results" in data["articles"]:
                articles = data["articles"]["results"]
                return articles
            else:
                return []
                
        except requests.exceptions.RequestException as e:
            # print(f"Error fetching articles: {e}")
            raise
    
    def get_best_articles(self, query: str, count: int = 2) -> List[Dict]:
        return self.search_articles(
            query=query,
            count=count,
            sort_by="rel"
        )