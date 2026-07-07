from src.corpus import load_corpus
from src.vector_db import VectorDB


def construire_base():
    ids, textes, metadatas = load_corpus()
    db = VectorDB(ids=ids, textes=textes, metadatas=metadatas)
    print(f"Base prete : {len(ids)} chunks indexes.")
    return db


def tester_retrieval(db):
    questions = [
        "Quelle est la couleur du chat de Bob ?",
        "Comment s'appelle le chien d'Alice ?",
        "Que collectionne Bob ?",
        "Que mange le chat Casimir ?",
        "Combien d'habitants a Villebrume-les-Cuilleres ?",
    ]
    for q in questions:
        res = db.retrieve(q, n=3)
        print("\nQ :", q)
        for doc in res["documents"][0]:
            print("   -", doc)


if __name__ == "__main__":
    db = construire_base()
    tester_retrieval(db)