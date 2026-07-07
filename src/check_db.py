from src.vector_db import VectorDB

db = VectorDB()   # recharge la base existante (cas 1)

# 1. Combien de chunks sont indexes ?
print("Nombre de chunks :", db.collection.count())

# 2. Le modele stocke dans les metadonnees de la collection
print("Modele enregistre :", db.collection.metadata)

# 3. Regarder quelques entrees brutes (texte + metadonnees)
extrait = db.collection.get(limit=3, include=["documents", "metadatas"])
for doc, meta in zip(extrait["documents"], extrait["metadatas"]):
    print("-", doc, "|", meta)