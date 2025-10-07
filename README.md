# Modern Information Retrieval with Solr (Bonus GenAI and RAG)

This tutorial repository guides you through setting up and using Apache Solr for modern
information retrieval use cases, including traditional keyword search, vector search, and
hybrid search. You will learn how to:

- Launch a Solr instance with Docker and custom configuration sets.
- Define Solr schemas supporting text analysis and dense vector fields.
- Create and manage a Solr collection optimized for GenAI and retrieval-augmented generation (RAG).
- Index sample data and execute search queries using Python scripts.

### Prerequisites:

- Docker & Docker Compose installed on your machine.
- Python 3.x and required dependencies

## Smoke Test

A quick verification of basic Solr operations is provided in the `0-smoketest` directory. See [0-smoketest/README.md](0-smoketest/README.md) for setup and usage details.

## Indexing Cranfield Documents into Solr
A script to index Cranfield documents with BERT embeddings into Solr is provided in the `1-indexdocs` directory. See [1-indexdocs/README.md](1-indexdocs/README.md) for setup and usage details.


