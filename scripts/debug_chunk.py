import sys
from src.extract import client, MODEL, SYSTEM, load_chunks

cid = sys.argv[1]
c = next(c for c in load_chunks() if c["chunk_id"] == cid)
print(c["text"][:1200])
print("\n----- MODEL OUTPUT -----")
r = client.chat.completions.create(
    model=MODEL, temperature=0, response_format={"type": "json_object"},
    extra_body={"reasoning_effort": "low"},
    messages=[{"role": "system", "content": SYSTEM},
              {"role": "user", "content": c["text"]}])
print(r.choices[0].message.content)
print(r.usage)