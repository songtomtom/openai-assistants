import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
organization = os.getenv("OPENAI_ORG_ID")
client = OpenAI(organization=organization, api_key=api_key)

# print(client.beta.assistants.list(limit=3, order="desc"))
assistants = client.beta.assistants.list(limit=3, order="desc")

for assistant in assistants:
    print(f"id: {assistant.id}, name: {assistant.name}")
