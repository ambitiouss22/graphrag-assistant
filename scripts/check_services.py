import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI

load_dotenv()

driver = GraphDatabase.driver(os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]))
driver.verify_connectivity()
print("Neo4j OK")

client = QdrantClient(path=os.environ["QDRANT_PATH"])
print("Qdrant OK, collections:", client.get_collections())
client.close()

emb = SentenceTransformer("BAAI/bge-small-en-v1.5")
print("Embedding dim:", emb.encode("hello").shape)   # expect (384,)

# LLM check: skipped until you add a real key
if os.environ.get("LLM_API_KEY", "").startswith("put_"):
    print("LLM: skipped (no key yet)")
else:
    llm = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
    r = llm.chat.completions.create(model=os.environ["LLM_MODEL"],
        messages=[{"role": "user", "content": "Reply with the word OK."}])
    print("LLM:", r.choices[0].message.content)