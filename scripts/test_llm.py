import os, json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.environ["LLM_BASE_URL"], api_key=os.environ["LLM_API_KEY"])
r = client.chat.completions.create(
    model=os.environ["LLM_MODEL"], temperature=0,
    response_format={"type": "json_object"},
    messages=[{"role": "user",
               "content": 'Return a JSON object with one key "entities" listing two LLM names.'}])
print(r.choices[0].message.content)
print("tokens used:", r.usage.total_tokens)
json.loads(r.choices[0].message.content)
print("valid JSON")