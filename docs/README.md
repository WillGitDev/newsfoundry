# Documentation NewsFoundry

| Document                                   | Contenu                                                                                                    |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| [architecture.md](architecture.md)         | Structure du projet, rôle de chaque fichier, commandes pour lancer l'application et les tests, déploiement |
| [choix-techniques.md](choix-techniques.md) | Les décisions prises pendant l'implémentation et leurs raisons                                             |
| [api.md](api.md)                           | Les routes de l'API backend et les erreurs qu'elles renvoient                                              |
| [prompts.md](prompts.md)                   | Les instructions données aux deux agents et l'intention de chaque consigne                                 |

## Démarrage rapide

```bash
# Backend (depuis backend/)
uv sync
uv run --env-file .env src/main.py      # http://localhost:8000

# Tests
uv run --env-file .env pytest

# Frontend (depuis frontend/)
npm install
npm run dev                              # http://localhost:3000
```

Les prérequis, les variables d'environnement et le démarrage de la base PostgreSQL sont
détaillés dans [architecture.md](architecture.md#lancer-le-projet).

## Application déployée

- **Frontend** : https://newsfoundry.vercel.app
- **Backend** : https://newsfoundry-production-f730.up.railway.app

Compte de test : `test@test.com` / `test`
