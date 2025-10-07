
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any, Union
import json


@dataclass
class Edismax:
    """Extended DisMax query parameters"""
    qf: Optional[str] = None  # Query fields with boosts: "title^5 description^1"
    mm: Optional[str] = None  # Minimum match: "2<75%"
    pf: Optional[str] = None  # Phrase fields: "title^10"
    ps: Optional[int] = None  # Phrase slop
    pf2: Optional[str] = None  # Bigram phrase fields
    ps2: Optional[int] = None  # Bigram phrase slop
    pf3: Optional[str] = None  # Trigram phrase fields
    ps3: Optional[int] = None  # Trigram phrase slop
    tie: Optional[float] = None  # Tie breaker: 0.0 to 1.0
    bq: Optional[Union[str, List[str]]] = None  # Boost query
    bf: Optional[str] = None  # Boost function
    boost: Optional[str] = None  # Multiplicative boost
    qs: Optional[int] = None  # Query phrase slop
    q_op: Optional[str] = field(default=None, metadata={'json_key': 'q.op'})  # AND or OR
    stopwords: Optional[bool] = None
    lowercaseOperators: Optional[bool] = None
    sow: Optional[bool] = None  # Split on whitespace

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict, removing None values and handling q.op"""
        result = {}
        for k, v in asdict(self).items():
            if v is not None:
                # Handle q.op special case
                if k == 'q_op':
                    result['q.op'] = v
                else:
                    result[k] = v
        return result


@dataclass
class VectorQuery:
    """K-Nearest Neighbors vector search"""
    field: str  # Vector field name
    vector: List[float]  # Query vector
    topK: int = 10  # Number of nearest neighbors
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TextQuery:
    """Text search query using edismax"""
    query: str
    qf: Optional[str] = None  # Query fields
    mm: Optional[str] = None  # Minimum match
    boost: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = {'query': self.query}
        if self.qf:
            result['qf'] = self.qf
        if self.mm:
            result['mm'] = self.mm
        if self.boost:
            result['boost'] = self.boost
        return result

@dataclass
class RerankConfig:
    """Reranking configuration"""
    query: str
    reRankDocs: int = 100
    reRankWeight: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'query': f"{{!rerank reRankQuery=$rq reRankDocs={self.reRankDocs} reRankWeight={self.reRankWeight}}}",
            'params': {'rq': self.query}
        }


@dataclass
class SolrQuery:
    """Complete Solr query builder"""
    # Base query
    query: str = "*:*"
    
    # Filters
    filters: List[str] = field(default_factory=list)
    
    # Text search
    text_query: Optional[str] = None
    edismax_params: Optional[Edismax] = None
    
    # Vector search
    vector_query: Optional[VectorQuery] = None
    
    # Pagination
    limit: int = 10
    offset: int = 0
    
    # Fields to return
    fields: List[str] = field(default_factory=lambda: ["*", "score"])
    
    # Reranking
    rerank: Optional[RerankConfig] = None
    
    # Sort
    sort: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Solr JSON query format"""
        query_dict = {"query": self.query}
        
        # Add filters
        if self.filters:
            query_dict["filter"] = self.filters
        
        # Add pagination
        query_dict["limit"] = self.limit
        query_dict["offset"] = self.offset
        
        # Add fields
        query_dict["fields"] = self.fields
        
        # Add sort
        if self.sort:
            query_dict["sort"] = self.sort
        
        # Add params for edismax
        if self.edismax_params:
            params = self.edismax_params.to_dict()
            if params:
                params["defType"] = "edismax"
                query_dict["params"] = params
        
        # Add text and vector queries
        queries = {}
        
        if self.text_query:
            text_params = {"query": self.text_query}
            if self.edismax_params:
                edismax_dict = self.edismax_params.to_dict()
                if edismax_dict:
                    text_params.update(edismax_dict)
            queries["text_query"] = {"edismax": text_params}
        
        if self.vector_query:
            queries["vector_query"] = {"knn": self.vector_query.to_dict()}
        
        if queries:
            query_dict["queries"] = queries
        
        
        # Add reranking
        if self.rerank:
            query_dict["rerank"] = self.rerank.to_dict()
        
        return query_dict
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)

