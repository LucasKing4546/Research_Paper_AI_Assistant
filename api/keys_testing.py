import os
import json
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import arxiv

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def load_env_file(env_path: str = ".env"):
    env_file = Path(env_path)
    if not env_file.exists():
        return

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


if load_dotenv is not None:
    load_dotenv()
else:
    load_env_file()

# ==========================================
# 1. SETUP THE ROBUST HTTP SESSION
# ==========================================
def create_retry_session():
    """
    Creates a requests Session that automatically retries on 429 (Too Many Requests)
    and 500-level server errors. Essential for Semantic Scholar and CORE.
    """
    session = requests.Session()
    
    # Configure the retry strategy
    retry_strategy = Retry(
        total=5,  # Maximum number of retries
        backoff_factor=1,  # Wait 1, 2, 4, 8 seconds between retries
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Initialize the global session
http = create_retry_session()

# ==========================================
# 2. API CONNECTOR FUNCTIONS
# ==========================================

def test_arxiv_api(query: str, max_results: int = 2):
    """
    Uses the official `arxiv` library to handle rate limits and parse the XML automatically.
    """
    print("\n--- Fetching from arXiv ---")
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=f"all:{query}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance
    )
    
    try:
        results = list(client.results(search))
        print(f"Success! Found {len(results)} papers.")
        
        # Print a clean preview of the first result
        if results:
            first_paper = results[0]
            print(f"Title: {first_paper.title}")
            print(f"Authors: {[author.name for author in first_paper.authors]}")
            print(f"Year: {first_paper.published.year}")
            print(f"Summary Snippet: {first_paper.summary[:150]}...")
            
        return results
    except Exception as e:
        print(f"arXiv Error: {e}")
        return None


def test_semantic_scholar_api(query: str, api_key: str, limit: int = 2):
    """
    Fetches JSON data from Semantic Scholar, utilizing the retry session for strict rate limits.
    """
    print("\n--- Fetching from Semantic Scholar ---")
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    if not api_key:
        print("Semantic Scholar Error: API Key is missing!")
        return None
        
    headers = {"x-api-key": api_key}
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,abstract,externalIds"
    }
    
    try:
        response = http.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status() 
        
        data = response.json()
        print(f"Success! Found {len(data.get('data', []))} papers.")
        
        # Print a clean preview
        if data.get('data'):
            print(json.dumps(data['data'][0], indent=2)[:300] + "...\n")
            
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Semantic Scholar Failed: {e}")
        return None


def test_core_api(query: str, api_key: str, limit: int = 2):
    """
    Fetches open-access papers from CORE.
    """
    print("\n--- Fetching from CORE ---")
    url = "https://api.core.ac.uk/v3/search/works"
    
    if not api_key:
        print("CORE Error: API Key is missing!")
        return None
        
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {
        "q": query,
        "limit": limit
    }
    
    try:
        response = http.get(url, headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        print(f"Success! Found {len(data.get('results', []))} papers.")
        
        # Print a clean preview
        if data.get('results'):
            print(json.dumps(data['results'][0], indent=2)[:300] + "...\n")
            
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"CORE Failed: {e}")
        return None


# ==========================================
# 3. TEST EXECUTION
# ==========================================
if __name__ == "__main__":
    # Ensure these variable names match exactly what you wrote in your .env file
    S2_API_KEY = os.getenv("S2_API_KEY")
    CORE_API_KEY = os.getenv("CORE_API_KEY")
    
    test_query = "few-shot learning in NLP"
    
    # 1. Test arXiv
    arxiv_data = test_arxiv_api(test_query)
    
    # 2. Test Semantic Scholar
    s2_data = test_semantic_scholar_api(test_query, S2_API_KEY)
    
    # 3. Test CORE
    core_data = test_core_api(test_query, CORE_API_KEY)