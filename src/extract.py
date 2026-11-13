import os, re, json, sys, time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from src.models import Extraction

load_dotenv()
client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
MODEL = os.environ["LLM_MODEL"]
CHUNKS = Path("data/processed/chunks.jsonl")
OUT = Path("data/processed/extractions.jsonl")
PAUSE = 15  # seconds between calls, keeps us under 8K tokens/minute

SYSTEM = """You extract a knowledge graph from text about AI/ML.
Return ONLY a JSON object: {"entities":[{"name":str,"type":str}],"relations":[{"source":str,"relation":str,"target":str,"evidence":str}]}
Entity types: Model (a named trained model), Method (algorithm, technique, architecture, attack or defense), Tool (software, library, framework, product), Dataset, Benchmark, Organization (company, lab, university).
Relation types and when to use them:
- USES: A is built on, depends on, or applies B.
- EVALUATED_ON: model/method A is tested on dataset/benchmark B.
- IMPROVES_ON: method/model A is stated to outperform, extend or fix an earlier method/model B.
- DEVELOPED_BY: A was created by organization B.
- PART_OF: A is explicitly described as a component or sub-module of B. Never use it for "works with", "integrates with" or "built on".
- COMPARED_WITH: A and B are explicitly compared.
Rules:
- Relations: only include ones the text explicitly states. No outside knowledge. When unsure, skip the relation.
- Entities: always list every specific named method, model, dataset, benchmark, tool or organization the text mentions (for example a paper's own proposed method like "MRMMIA", or named baselines), even when no relation is found.
- evidence = ONE contiguous exact quote copied from the text (max 25 words) that states the relation. No "..." and never stitch separate parts together.
- Use the short name as written in the text (e.g. "GPT-4", not "the GPT-4 model"). Different versions are different entities.
- source and target of every relation must also appear in entities.
- Skip generic concepts such as "LLM", "AI", "agent". Only named systems, methods, datasets, organizations.
- Maximum 12 relations. If nothing fits, return empty lists."""


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def verify(ext, text):
    """Keep relations whose evidence words appear verbatim in the chunk; return the rest as rejected."""
    t = norm(text)
    kept, rejected = [], []
    for r in ext.relations:
        e = norm(r.evidence)
        (kept if e and e in t else rejected).append(r)
    ext.relations = kept
    return ext, rejected


def extract(text, retries=3):
    for attempt in range(1, retries + 1):
        try:
            r = client.chat.completions.create(
                model=MODEL, temperature=0,
                response_format={"type": "json_object"},
                extra_body={"reasoning_effort": "low"},
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": text}])
            ext = Extraction.model_validate_json(r.choices[0].message.content)
            return ext, r.usage.total_tokens
        except RateLimitError as e:
            msg = str(e)
            print("rate limited:", msg[:200])
            if "per day" in msg.lower() or "tpd" in msg.lower():
                print("DAILY LIMIT REACHED. Stop now. Switch model in .env or retry tomorrow.")
                sys.exit(0)
            time.sleep(30 * attempt)
        except Exception as e:
            print("retry", attempt, type(e).__name__, str(e)[:150])
            time.sleep(3)
    return None, 0


def load_chunks():
    return [json.loads(l) for l in CHUNKS.read_text(encoding="utf-8").splitlines()]


def pick_test(chunks):
    picked, count = [], {"arxiv": 3, "wikipedia": 2, "readme": 2}
    for c in chunks:
        if c["chunk_id"].endswith("#1") and count.get(c["source"], 0) > 0:
            picked.append(c)
            count[c["source"]] -= 1
    return picked


def run(chunks):
    done = set()
    if OUT.exists():
        done = {json.loads(l)["chunk_id"] for l in OUT.read_text(encoding="utf-8").splitlines() if l}
    total = 0
    for i, c in enumerate(chunks, 1):
        if c["chunk_id"] in done:
            continue
        ext, tokens = extract(c["text"])
        if ext is None:
            print("FAILED:", c["chunk_id"])
            continue
        ext, rejected = verify(ext, c["text"])
        total += tokens
        rec = {"chunk_id": c["chunk_id"], "doc_id": c["doc_id"], "model": MODEL,
               "tokens": tokens, "extraction": ext.model_dump(),
               "rejected": [r.model_dump() for r in rejected]}
        with OUT.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"[{i}/{len(chunks)}] {c['chunk_id']}: {len(ext.entities)} entities, "
            f"{len(ext.relations)} relations (dropped {len(rejected)}), {tokens} tokens (session total {total})")
        time.sleep(PAUSE)

def redo(chunks, cid):
    c = next(c for c in chunks if c["chunk_id"] == cid)
    ext, _ = extract(c["text"])
    ext, rejected = verify(ext, c["text"])
    print("KEPT:")
    for r in ext.relations:
        print(f"  {r.source} -[{r.relation}]-> {r.target} | {r.evidence}")
    print("REJECTED:")
    for r in rejected:
        print(f"  {r.source} -[{r.relation}]-> {r.target} | {r.evidence}")

def rerun(chunks, ids):
    recs = {}
    for l in OUT.read_text(encoding="utf-8").splitlines():
        if l:
            r = json.loads(l)
            recs[r["chunk_id"]] = r
    by_id = {c["chunk_id"]: c for c in chunks}
    for cid in ids:
        c = by_id[cid]
        ext, tokens = extract(c["text"])
        if ext is None:
            print("FAILED:", cid)
            continue
        ext, rejected = verify(ext, c["text"])
        recs[cid] = {"chunk_id": cid, "doc_id": c["doc_id"], "model": MODEL, "tokens": tokens,
                     "extraction": ext.model_dump(), "rejected": [r.model_dump() for r in rejected]}
        OUT.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in recs.values()) + "\n",
                       encoding="utf-8")
        print(f"{cid}: {len(ext.relations)} relations (rejected {len(rejected)}), {tokens} tokens")
        time.sleep(PAUSE)

if __name__ == "__main__":
    chunks = load_chunks()
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    if mode == "redo":
        redo(chunks, sys.argv[2])
    elif mode == "rerun":
        rerun(chunks, [l.strip() for l in open(sys.argv[2], encoding="utf-8") if l.strip()])
    else:
        run(pick_test(chunks) if mode == "test" else chunks)