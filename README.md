# Mon premier RAG — M2 MD5

RAG minimal mais complet : ChromaDB + sentence-transformers + Groq + agent modérateur.

Base de connaissances : un corpus de 200 phrases absurdes (« Le chat bleu de Bob s'appelle Henri »…), faits introuvables sur Internet, pour prouver que les bonnes réponses viennent du *retrieval* et non de la mémoire du LLM.

## Architecture

Trois briques, chacune dans son fichier :

- `src/vector_db.py` — **VectorDB** : crée ou recharge une base ChromaDB persistée, encode les chunks, retrouve les plus proches d'une question.
- `src/moderation.py` — **Moderateur** : demande à un modèle de sécurité si la question est une injection, renvoie un JSON.
- `src/rag.py` — **RAG** : orchestre modération → retrieval → prompt → appel LLM.

Configuration :

- `src/config.py` — noms des modèles et chemins, centralisés à un seul endroit.
- `prompts/` — les prompts système en fichiers texte (retravaillables sans toucher au code).

## Installation

```
python -m venv venv
source venv/Scripts/activate      # Windows Git Bash
pip install -r requirements.txt
```

Créer un fichier `.env` à la racine (voir `.env.example`) avec votre clé Groq :

```
GROQ_API_KEY=gsk_votre_cle
```

## Utilisation

```
python -m src.main         # construit/recharge la base et teste le retrieval
python -m src.test_rag     # teste le pipeline RAG complet
```

## Modèles utilisés

- **Embedding** : `distiluse-base-multilingual-cased-v2` — multilingue (corpus en français), léger, suffisant pour ce corpus.
- **Génération** : `llama-3.3-70b-versatile` (Groq).
- **Modération** : `openai/gpt-oss-safeguard-20b` (Groq). Le modèle guard initialement prévu ayant été décommissionné, un seul changement de ligne dans `config.py` a suffi — c'est tout l'intérêt de centraliser les noms de modèles.

## Réponses aux questions du TP

**1. Pourquoi normaliser les embeddings ?**
La recherche repose sur la similarité cosinus, qui compare la *direction* des vecteurs (le sens), pas leur longueur. Normaliser met tous les vecteurs à la même norme, pour que la comparaison porte uniquement sur le sens et non sur la magnitude — sinon une phrase longue pourrait peser plus lourd juste par sa taille.

**2. Le nom du modèle dans les métadonnées de la collection : quel bug évité ?**
À la création, on enregistre le nom du modèle d'embedding dans les métadonnées de la collection. Au rechargement, on relit ce nom pour charger *ce* modèle-là, et pas celui (peut-être différent) de la config du jour. Sans cette astuce : si on créait la base avec le modèle A puis qu'on la rechargeait des mois plus tard avec une config pointant vers le modèle B, les questions seraient encodées avec B tandis que le corpus l'a été avec A. Les vecteurs seraient incompatibles, le retrieval renverrait n'importe quoi — un bug silencieux, sans message d'erreur, très difficile à diagnostiquer.

**3. Pourquoi un modérateur dédié plutôt qu'une consigne dans le prompt du RAG ?**
Un modèle de sécurité séparé est spécialisé et découplé. S'appuyer sur une simple ligne « refuse les injections » dans le prompt du RAG est fragile : ce prompt est lui-même la cible du détournement. Séparer la décision de sécurité de la génération la rend plus robuste, et permet de refuser *avant* d'appeler le LLM principal.

**4. Les consignes du prompt système du RAG (reformulées) :**
- *Répondre uniquement depuis la base* → empêche le LLM d'utiliser ses connaissances générales et d'halluciner.
- *Tous les chunks ne sont pas utiles* → le retrieval ramène parfois du bruit ; le modèle est autorisé à écarter le hors-sujet.
- *Dire « je ne sais pas » hors périmètre* → prévient l'invention de réponses (test « capitale du Japon »).
- *Signaler les contradictions* → gère le cas « le chat est vert ? » où un chunk dément l'affirmation.

## La mise à l'épreuve (partie 6)

| Test | Comportement observé |
|------|----------------------|
| Question dans le corpus (couleur du chat de Bob) | Répond « Henri, bleu » et mentionne Casimir (noir), ancré dans les chunks |
| Hors corpus (capitale du Japon) | Dit qu'il ne sait pas, ne répond pas « Tokyo » de mémoire |
| Affirmation fausse (le chat est vert ?) | Signale la contradiction et corrige : « a toujours été bleu » |
| Injection (oublie ton contexte…) | Refusée par le modérateur, le LLM principal n'est jamais appelé |

**Qui intercepte l'injection, et quand ?** Le modérateur, en **étape 1** du pipeline, avant le retrieval et avant le LLM. L'ordre des opérations est une décision de sécurité.

## Vérification de la base

`python -m src.check_db` inspecte la base : nombre de chunks (200), modèle enregistré dans les métadonnées de la collection, et un extrait des entrées stockées.

## Workflow Git

Branches `main` (stable) / `dev` (intégration) / `feature/*` (une par brique).
Commits atomiques préfixés (`feat:`, `chore:`, `merge:`). `.env` et `chroma/` ignorés via `.gitignore`.