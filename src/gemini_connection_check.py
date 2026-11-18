import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is not configured.")

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Respond with exactly: Gemini connection successful.",
)

print(response.text)


# # print(response.content)
# if isinstance(response.content, list):
#     print(response.content[0]["text"])
# else:
#     print(response.content)