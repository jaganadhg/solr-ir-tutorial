import requests 
from typing import List, Dict, Optional, Any, Union

from solrir.utils.qtypes import SolrQuery



class SolrClient:
    def __init__(self, solr_url: str, core: str, timeout: int = 10):
        self.solr_url = solr_url
        self.core = core
        self.timeout = timeout 
        self.base_url = f"{self.solr_url}/solr/{self.core}/query"
    
    def search(self, query: SolrQuery) -> Dict[str, Any]:
        """Send a search request to Solr and return the response"""
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(self.base_url,
                                     json=query.to_dict(),
                                     headers=headers,
                                     timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error during Solr request: {e}")
            raise


