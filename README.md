# GraphRAG Knowledge Assistant

Hybrid graph + vector retrieval over a multi-source corpus (arXiv papers, Wikipedia,
GitHub READMEs), with LLM-based entity extraction and entity resolution into Neo4j.

**Status: in progress.** Last updated: 12 Nov 2026.

## Progress
- [x] Environment, Neo4j AuraDB + local Qdrant, embeddings (BAAI/bge-small-en-v1.5)
- [x] Corpus collection script (95 documents: 40 arXiv, 30 Wikipedia, 25 READMEs)
- [x] Graph schema v1 (see docs/schema.md)
- [ ] Text cleaning and chunking
- [ ] LLM entity/relation extraction
- [ ] Entity resolution
- [ ] Hybrid retrieval (graph traversal + vector search)
- [ ] Evaluation: vector-only vs graph-only vs hybrid on multi-hop questions
- [ ] Web UI with source-graph view and feedback buttons
- [ ] Public demo

## Results
Not available yet. Numbers will be added here only after they are measured.

## Demo
Coming soon.

## Setup
1. Python 3.12, then `python -m venv .venv` and activate it
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your values
4. `python scripts/check_services.py` to verify the connections
5. `python scripts/fetch_corpus.py` to download the corpus

## Project log
Daily decisions and problems are recorded in docs/log.md.