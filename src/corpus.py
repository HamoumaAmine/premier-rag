import csv
from src.config import CSV_PATH


def load_corpus(path=CSV_PATH):
    """Lit le CSV et renvoie (ids, textes, metadatas).
    - ids       : liste des identifiants (colonne 'id')
    - textes    : liste des phrases a encoder (colonne 'text')
    - metadatas : liste de dicts {'source': ..., 'categorie': ...}
    """
    ids = []
    textes = []
    metadatas = []

    with open(path, encoding="utf-8") as f:
        lecteur = csv.DictReader(f)
        for ligne in lecteur:
            ids.append(ligne["id"])
            textes.append(ligne["text"])
            metadatas.append({
                "source": ligne["source"],
                "categorie": ligne["categorie"],
            })

    return ids, textes, metadatas