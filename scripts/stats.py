import json, collections

ents, rels = collections.Counter(), collections.Counter()
n = zero = nrel = 0
for l in open("data/processed/extractions.jsonl", encoding="utf-8"):
    r = json.loads(l)
    e = r["extraction"]
    n += 1
    nrel += len(e["relations"])
    zero += len(e["relations"]) == 0
    for x in e["entities"]:
        ents[(x["name"].lower(), x["type"])] += 1
    for x in e["relations"]:
        rels[x["relation"]] += 1
print("chunks:", n, "| relations:", nrel, "| chunks with no relation:", zero)
print("distinct entities:", len(ents))
print("relation types:", dict(rels))
print("most-mentioned entities:", [(k[0], v) for k, v in ents.most_common(15)])