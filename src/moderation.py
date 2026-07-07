import os
import json
from groq import Groq
from dotenv import load_dotenv
from src.config import MODERATION_MODEL

load_dotenv()


class Moderateur:
    def __init__(self, prompt_path="prompts/moderateur.txt"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        with open(prompt_path, encoding="utf-8") as f:
            self.system_prompt = f.read()

    def moderate(self, question):
        reponse = self.client.chat.completions.create(
            model=MODERATION_MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": question},
            ],
            response_format={"type": "json_object"},
        )
        contenu = reponse.choices[0].message.content
        resultat = json.loads(contenu)
        return resultat