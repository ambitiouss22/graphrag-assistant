import json, sys
docs = [json.loads(l) for l in open("data/processed/docs.jsonl", encoding="utf-8")]
key = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
d = docs[int(key)] if key.isdigit() else next(x for x in docs if key.lower() in x["id"].lower())
print(d["id"], "|", d["title"], "|", len(d["text"]), "chars\n")
print(d["text"][:n])