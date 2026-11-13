import json, re, collections

IN = "data/processed/extractions.jsonl"
OUT = "data/processed/relations_clean.jsonl"


def norm(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


why, kept, total = collections.Counter(), [], 0
for line in open(IN, encoding="utf-8"):
    r = json.loads(line)
    ents = {norm(e["name"]): e["type"] for e in r["extraction"]["entities"]}
    for x in r["extraction"]["relations"]:
        total += 1
        s, t, ev = norm(x["source"]), norm(x["target"]), norm(x["evidence"])
        if not s or not t or s == t:
            why["empty or self-relation"] += 1
        elif s not in ents or t not in ents:
            why["endpoint not in entity list"] += 1
        elif t not in ev:
            why["target not named in the quote"] += 1
        elif x["relation"] == "DEVELOPED_BY" and ents[t] != "Organization":
            why["DEVELOPED_BY target is not an Organization"] += 1
        elif x["relation"] == "EVALUATED_ON" and ents[t] not in ("Dataset", "Benchmark"):
            why["EVALUATED_ON target is not a Dataset/Benchmark"] += 1
        else:
            kept.append({**x, "chunk_id": r["chunk_id"], "doc_id": r["doc_id"],
                         "source_type": ents[s], "target_type": ents[t]})

with open(OUT, "w", encoding="utf-8") as f:
    for k in kept:
        f.write(json.dumps(k, ensure_ascii=False) + "\n")
print(f"relations: {total} -> kept {len(kept)}")
for k, v in why.most_common():
    print(f"  dropped {v}: {k}")