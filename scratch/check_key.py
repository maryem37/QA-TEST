import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ["GROQ_API_KEY"])
r = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Réponds : ok"}],
    max_tokens=20,
)
print("clé valide, tokens utilisés :", r.usage.total_tokens)