import requests
import torch
import json
import ir_datasets
from typing import List, Dict, Any
from transformers import AutoTokenizer, AutoModel



class IndexDocs:
    """
    Index documents in Solr.
    """
    def __init__(self, solr_url: str, core_name: str):
        self.solr_url = solr_url
        self.core_name = core_name
        self.core_url = f"{solr_url}/{core_name}"
    
    def create_core(self, config_set: str = "_default"):
        """
        Create a new Solr core.
        
        Args:
            config_set: Configuration set to use (e.g., '_default', 'sample_techproducts_configs')
        """
        url = f"{self.solr_url}/admin/cores"
        params = {
            "action": "CREATE",
            "name": self.core_name,
            "configSet": config_set
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            print(f"✓ Core '{self.core_name}' created successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"✗ Error creating core: {e}")
            if "already exists" in str(e).lower():
                print(f"  Core '{self.core_name}' already exists, continuing...")
            return None
    

    def define_schema(self, vector_dimension: int = 768):
        """
        Define the schema with text and vector fields.
        
        Args:
            vector_dimension: Dimension of the embedding vectors (e.g., 768 for BERT)
        """
        schema_url = f"{self.core_url}/schema"
        #doc_id, title, text, author, bib
        fields = [
            {
                "name": "doc_id",
                "type": "text_general",
                "indexed": True,
                "stored": True,
                "multiValued": False 

            },
            {
                "name": "title",
                "type": "text_general",
                "indexed": True,
                "stored": True,
                "multiValued": False 

            },
            {
                "name": "text",
                "type": "text_general",
                "indexed": True,
                "stored": True,
                "multiValued": False 

            },
            {
                "name": "author",
                "type": "text_general",
                "indexed": True,
                "stored": True,
                "multiValued": False 

            },
            {
                "name": "bib",
                "type": "text_general",
                "indexed": True,
                "stored": True,
                "multiValued": False 

            },
             {
                "name": "vector",
                "type": "knn_vector",
                "indexed": True,
                "stored": True,
                "multiValued": False
            }
        ]
        
        # First, add the field type for dense vectors with HNSW
        field_type = {
            "name": "knn_vector",
            "class": "solr.DenseVectorField",
            "vectorDimension": vector_dimension,
            "similarityFunction": "cosine",
            "knnAlgorithm": "hnsw",
            "hnswMaxConnections": 16,
            "hnswBeamWidth": 100
        }
        
        try:
            response = requests.post(
                schema_url,
                json={"add-field-type": field_type},
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200 or "already exists" in response.text.lower():
                print(f"✓ Field type 'vector' configured with HNSW indexing")
            else:
                print(f"✗ Failed to add field type: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Error adding field type: {e}")

        for field in fields:
            try:
                response = requests.post(
                    schema_url,
                    json={"add-field": field},
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200 or "already exists" in response.text.lower():
                    print(f"✓ Added field: {field['name']}")
                else:
                    print(f"✗ Failed to add field {field['name']}: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"✗ Error adding field {field['name']}: {e}")
    

    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index documents into Solr.
        
        Args:
            documents: List of documents
        """
        update_url = f"{self.core_url}/update/json/docs"
        
        try:
            response = requests.post(
                update_url,
                json=documents,
                params={"commit": "true"},
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            print(f"✓ Indexed {len(documents)} documents successfully")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"✗ Error indexing documents: {e}")
            return None



def embed_text(text: str, tokenizer, model) -> list:
    """Tokenize & run through BERT, then mean-pool the last hidden state."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    last_hidden = outputs.last_hidden_state        # (1, seq_len, hidden_size)
    mask = inputs.attention_mask.unsqueeze(-1)     # (1, seq_len, 1)
    masked = last_hidden * mask
    summed = masked.sum(dim=1)                     # (1, hidden_size)
    counts = mask.sum(dim=1).clamp(min=1e-9)       # avoid div zero
    mean_pooled = (summed / counts).squeeze().tolist()
    return mean_pooled


def prepare_cranfiled():
    """Load and prepare Cranfield documents."""
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model     = AutoModel.from_pretrained("bert-base-uncased")
    model.eval()

    dataset = ir_datasets.load("cranfield")
    docs = []
    for doc in dataset.docs_iter():
        docs.append({
            "doc_id": doc.doc_id,
            "title": doc.title,
            "text": doc.text,
            "author": doc.author,
            "bib": doc.bib,
            "vector": embed_text(doc.text, tokenizer, model)
        })
    return docs



if __name__ == "__main__":
    # Initialize the index creator for standalone Solr
    cran_docs = prepare_cranfiled()

    creator = IndexDocs(
        solr_url="http://localhost:8983/solr",
        core_name="cranfiled_docs"
    )
    
    # Step 1: Create core
    print("\n=== Creating Core ===")
    creator.create_core()

    # Step 2: Define schema with vector dimension (e.g., 768 for BERT embeddings)
    print("\n=== Defining Schema ===")
    creator.define_schema(vector_dimension=768)
    
    # Step 3: Index documents
    print("\n=== Indexing Documents ===")
    creator.index_documents(cran_docs)

    print("\nAll done!")