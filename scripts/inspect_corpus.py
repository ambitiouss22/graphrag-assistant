import json, statistics
from collections import defaultdict

docs = [json.loads(l) for l in open("data/processed/docs.jsonl", encoding="utf-8")]
by = defaultdict(list)
for d in docs:
    by[d["source"]].append(len(d["text"]))
for s, lens in by.items():
    print(f"{s}: n={len(lens)} min={min(lens)} median={int(statistics.median(lens))} max={max(lens)}")
total = sum(len(d["text"]) for d in docs)
print("total chars:", total, "| rough tokens:", total // 4)
for d in sorted(docs, key=lambda d: -len(d["text"]))[:5]:
    print("LONGEST:", d["id"], len(d["text"]))