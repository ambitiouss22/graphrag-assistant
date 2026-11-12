# Graph schema (v1)

## Entity types
Model, Method, Dataset, Benchmark, Organization, Tool

## Relation types
USES, EVALUATED_ON, IMPROVES_ON, DEVELOPED_BY, PART_OF, COMPARED_WITH

## Graph structure
(:Document {id, title, source})-[:HAS_CHUNK]->(:Chunk {id, text})
(:Chunk)-[:MENTIONS]->(:Entity {id, name, type, aliases})
(:Entity)-[:RELATES {type, evidence_chunk_id}]->(:Entity)

Every relation keeps its evidence chunk, for the source-graph view and faithfulness checks.

## What counts as a duplicate
Same real-world thing under different names = SAME ("GPT-4", "GPT4", "OpenAI GPT-4").
Different versions or related products = DIFFERENT ("GPT-4" vs "GPT-4o", "LangChain" vs "LangGraph").
Labelling rule for the 100 hand-labelled pairs: label each pair SAME or DIFFERENT, with about half
being hard negatives (similar names, different things).