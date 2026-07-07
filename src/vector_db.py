import chromadb
from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL, CHROMA_PATH, COLLECTION_NAME


class VectorDB:
    def __init__(self, chemin=CHROMA_PATH, ids=None, textes=None, metadatas=None):
        self.client = chromadb.PersistentClient(path=chemin)
        base_existe = COLLECTION_NAME in [c.name for c in self.client.list_collections()]

        if base_existe:
            # CAS 1 : recharge, sans reencoder
            self.collection = self.client.get_collection(COLLECTION_NAME)
            nom_modele = self.collection.metadata["embedding_model"]   # TODO 1
            self.model = SentenceTransformer(nom_modele)

        elif textes is not None:
            # CAS 2 : creation
            self.model = SentenceTransformer(EMBEDDING_MODEL)
            self.collection = self.client.create_collection(
                name=COLLECTION_NAME,
                metadata={"embedding_model": EMBEDDING_MODEL},
            )
            vecteurs = self._encode(textes)
            self.collection.add(                                       # TODO 2
                ids=ids,
                documents=textes,
                embeddings=vecteurs,
                metadatas=metadatas,
            )

        else:
            # CAS 3 : erreur
            raise ValueError(
                "Aucune base trouvee et aucun chunk fourni : impossible de demarrer."
            )

    def _encode(self, textes):
        return self.model.encode(                                     # TODO 3
            textes, normalize_embeddings=True
        ).tolist()

    def retrieve(self, question, n=3):
        vecteur_question = self._encode([question])
        return self.collection.query(                                 # TODO 4
            query_embeddings=vecteur_question,
            n_results=n,
        )