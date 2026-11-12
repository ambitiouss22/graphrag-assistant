import json, re, pathlib, requests, arxiv, pymupdf
from collections import Counter

OUT = pathlib.Path("data/processed")
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "graphrag-assistant/0.1 (student project; avneedadhich38@gmail.com)"}
docs = []

def clean(text, cut_refs=False):
    if cut_refs:
        idx = max(text.rfind("\nReferences\n"), text.rfind("\nREFERENCES\n"))
        if idx > len(text) * 0.5:
            text = text[:idx]
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def add(doc_id, source, title, text, cut_refs=False):
    text = clean(text, cut_refs)
    if len(text) < 500:
        print("  too short, skipped:", doc_id)
        return
    docs.append({"id": doc_id, "source": source, "title": title, "text": text})

# 1) arXiv: 40 papers (text extracted in memory, no PDFs saved)
queries = ["LLM agent long-term memory", "knowledge graph retrieval augmented generation",
           "GraphRAG", "agentic RAG", "LLM-as-a-judge evaluation"]
client = arxiv.Client(page_size=10, delay_seconds=3, num_retries=3)
seen = set()
for q in queries:
    for r in client.results(arxiv.Search(query=q, max_results=12)):
        if len(seen) >= 40:
            break
        aid = r.get_short_id()
        if aid in seen:
            continue
        try:
            resp = requests.get(r.pdf_url, headers=HEADERS, timeout=60)
            resp.raise_for_status()
            with pymupdf.open(stream=resp.content, filetype="pdf") as pdf:
                text = "\n".join(page.get_text() for page in pdf)
        except Exception as e:
            print("  skip", aid, e)
            continue
        seen.add(aid)
        add(f"arxiv:{aid}", "arxiv", r.title, text, cut_refs=True)
        print("arxiv", len(seen), r.title[:60])

# 2) Wikipedia: missing titles are skipped
titles = ["Retrieval-augmented generation", "Knowledge graph", "Large language model",
  "Vector database", "Entity linking", "Record linkage", "Semantic search", "Neo4j",
  "Prompt engineering", "Hallucination (artificial intelligence)", "Graph database",
  "Word embedding", "Named-entity recognition", "Information extraction",
  "Ontology (information science)", "Nearest neighbor search", "BERT (language model)",
  "GPT-4", "Reinforcement learning from human feedback", "Question answering",
  "Semantic Web", "Resource Description Framework", "Transformer (deep learning architecture)",
  "Natural language processing", "Cosine similarity", "Knowledge representation and reasoning",
  "Chatbot", "Recommender system", "Cypher (query language)", "SPARQL"]
for t in titles:
    try:
        r = requests.get("https://en.wikipedia.org/w/api.php", headers=HEADERS, timeout=30,
            params={"action": "query", "prop": "extracts", "explaintext": 1,
                    "redirects": 1, "titles": t, "format": "json"})
        page = next(iter(r.json()["query"]["pages"].values()))
        if page.get("extract"):
            add(f"wiki:{t}", "wikipedia", t, page["extract"])
            print("wiki", t)
    except Exception as e:
        print("  skip", t, e)

# 3) GitHub READMEs
repos = ["langchain-ai/langgraph", "langchain-ai/langchain", "run-llama/llama_index",
  "microsoft/autogen", "crewAIInc/crewAI", "mem0ai/mem0", "letta-ai/letta",
  "microsoft/graphrag", "neo4j/neo4j-graphrag-python", "qdrant/qdrant",
  "explodinggradients/ragas", "chroma-core/chroma", "milvus-io/milvus",
  "weaviate/weaviate", "deepset-ai/haystack", "huggingface/transformers",
  "UKPLab/sentence-transformers", "vllm-project/vllm", "ollama/ollama",
  "tiangolo/fastapi", "streamlit/streamlit", "neo4j/neo4j-python-driver",
  "infiniflow/ragflow", "HKUDS/LightRAG", "getzep/graphiti", "langfuse/langfuse"]
for repo in repos:
    for branch in ("main", "master"):
        try:
            r = requests.get(f"https://raw.githubusercontent.com/{repo}/{branch}/README.md",
                             headers=HEADERS, timeout=30)
        except Exception as e:
            print("  skip", repo, e)
            break
        if r.ok:
            add(f"readme:{repo}", "readme", repo, r.text)
            print("readme", repo)
            break

with open(OUT / "docs.jsonl", "w", encoding="utf-8") as f:
    for d in docs:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")
print("\nTOTAL:", len(docs), dict(Counter(d["source"] for d in docs)))