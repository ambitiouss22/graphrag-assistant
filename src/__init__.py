import json, re
from pathlib import Path

RAW = Path("data/processed/docs.jsonl")
OUT = Path("data/processed/chunks.jsonl")

CAP = {"arxiv": 20000, "wikipedia": 16000, "readme": 16000}      # max chars kept per doc
N_DOCS = {"arxiv": 15, "wikipedia": 15, "readme": 15}            # docs kept per source
MAX_CHUNKS = 4                                                   # chunks kept per doc
CHUNK, OVERLAP = 3000, 300


def source_key(s):
    s = (s or "").lower()
    for k in CAP:
        if k[:4] in s:
            return k
    return None


def clean_readme(t):
    t = re.sub(r"```.*?```", " ", t, flags=re.S)           # code blocks
    t = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", t)            # images/badges
    t = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", t)         # links -> text
    t = re.sub(r"<[^>]+>", " ", t)                         # html tags
    return t


def clean_arxiv(t):
    t = re.sub(r"-\n(?=[a-z])", "", t)                     # hyphenation
    t = re.sub(r"(?m)^\s*\d{1,3}\s*$", "", t)              # lone page numbers
    t = re.sub(r"(?<!\n)\n(?!\n)", " ", t)                 # hard line breaks
    return t


def tidy(t):
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def split_text(t):
    chunks, start = [], 0
    while start < len(t):
        end = min(start + CHUNK, len(t))
        if end < len(t):                                   # snap to a sentence/paragraph end
            window = t[max(start, end - 500):end]
            cut = max(window.rfind(". "), window.rfind("\n"))
            if cut > 0:
                end = end - len(window) + cut + 1
        chunks.append(t[start:end].strip())
        if end >= len(t):
            break
        start = max(end - OVERLAP, start + 1)
    return [c for c in chunks if len(c) >= 200]


def main():
    kept = {k: 0 for k in CAP}
    out, n_docs = [], 0
    for line in RAW.read_text(encoding="utf-8").splitlines():
        d = json.loads(line)
        src = source_key(d.get("source"))
        if src is None or kept[src] >= N_DOCS[src]:
            continue
        text = d["text"][: CAP[src] * 2]
        if src == "readme":
            text = clean_readme(text)
        elif src == "arxiv":
            text = clean_arxiv(text)
        text = tidy(text)[: CAP[src]]
        if len(text) < 2000:
            continue
        doc_id = d.get("doc_id") or d.get("id")
        for i, c in enumerate(split_text(text)[:MAX_CHUNKS]):
            out.append({"chunk_id": f"{doc_id}#{i}", "doc_id": doc_id,
                        "source": src, "title": d.get("title", ""), "text": c})
        kept[src] += 1
        n_docs += 1
    OUT.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in out), encoding="utf-8")
    chars = sum(len(o["text"]) for o in out)
    print(f"docs kept: {kept}")
    print(f"chunks: {len(out)}  chars: {chars}  ~tokens: {chars // 4}")


if __name__ == "__main__":
    main()