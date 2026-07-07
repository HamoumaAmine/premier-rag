import os
from groq import Groq
from dotenv import load_dotenv
from src.config import LLM_MODEL
from src.vector_db import VectorDB
from src.moderation import Moderateur

load_dotenv()


class RAG:
    def __init__(self, prompt_path="prompts/rag_systeme.txt"):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.moderateur = Moderateur()
        self.db = VectorDB()   # recharge la base existante (cas 1)
        with open(prompt_path, encoding="utf-8") as f:
            self.prompt_template = f.read()

    def answer_question(self, question):
        # ETAPE 1 : moderation AVANT tout (decision de securite)
        verdict = self.moderateur.moderate(question)
        if verdict["is_prompt_injection"]:
            return "Requete refusee : tentative de detournement detectee."

        # ETAPE 2 : recuperer les 3 chunks les plus proches
        res = self.db.retrieve(question, n=3)
        chunks = res["documents"][0]

        # ETAPE 3 : remplir le prompt a trous
        chunks_texte = "\n".join(chunks)
        prompt_systeme = self.prompt_template.replace("{{Chunks}}", chunks_texte)

        # ETAPE 4 : appeler le LLM principal (texte libre, PAS de JSON ici)
        reponse = self.client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": prompt_systeme},
                {"role": "user", "content": question},
            ],
        )
        return reponse.choices[0].message.content