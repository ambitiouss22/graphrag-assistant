import json, random

rels = [json.loads(l) for l in open("data/processed/relations_clean.jsonl", encoding="utf-8")]
random.seed(11)
for i, x in enumerate(random.sample(rels, min(30, len(rels))), 1):
    print(f'{i}. {x["source"]} -[{x["relation"]}]-> {x["target"]}   ({x["chunk_id"]})')
    print(f'     "{x["evidence"]}"')