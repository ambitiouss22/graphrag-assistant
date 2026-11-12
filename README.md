# GraphRAG Knowledge Assistant

Hybrid graph + vector retrieval over a multi-source corpus (arXiv papers, Wikipedia,
GitHub READMEs), with LLM-based entity extraction and entity resolution into Neo4j.

## Design
1. Ingest: collect and clean documents from three sources
2. Chunk: section-aware chunking
3. Extract: LLM-based entity and relation extraction into a typed schema
4. Resolve: merge duplicate entities (embedding similarity + LLM adjudication)
5. Store: Neo4j for the graph, Qdrant for chunk embeddings
6. Retrieve: combine graph traversal with vector search
7. Evaluate: compare vector-only, graph-only and hybrid retrieval on multi-hop questions

The graph schema is in docs/schema.md.

## Repository contents
- scripts/fetch_corpus.py: builds the corpus (arXiv, Wikipedia, GitHub READMEs)
- scripts/inspect_corpus.py, scripts/peek.py: corpus statistics and inspection
- scripts/check_services.py: verifies Neo4j, Qdrant and embedding model connections
- docs/schema.md: entity types, relation types and graph structure

## Setup
1. Python 3.12, then `python -m venv .venv` and activate it
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your values
4. `python scripts/check_services.py` to verify the connections
5. `python scripts/fetch_corpus.py` to download the corpus
