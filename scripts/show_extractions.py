import json
for l in open("data/processed/extractions.jsonl", encoding="utf-8"):
    r = json.loads(l)
    print("\n==", r["chunk_id"], "|", r["tokens"], "tokens")
    for x in r["extraction"]["relations"]:
        print(f'  {x["source"]} -[{x["relation"]}]-> {x["target"]}\n      "{x["evidence"]}"')