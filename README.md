# Documentation NewsFoundry

Outil de revue de presse assistée par IA pour les pigistes : discuter avec un agent informé de l'actualité du jour, affiner la recherche, puis générer une revue de presse.

| Document                                        | Contenu                                                                                                    |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [architecture.md](docs/architecture.md)         | Structure du projet, rôle de chaque fichier, commandes pour lancer l'application et les tests, déploiement |
| [choix_techniques.md](docs/choix_techniques.md) | Les décisions prises pendant l'implémentation et leurs raisons                                             |
| [api.md](docs/api.md)                           | Les routes de l'API backend et les erreurs qu'elles renvoient                                              |
| [prompts.md](docs/prompts.md)                   | Les instructions données aux deux agents et l'intention de chaque consigne                                 |
| [améliorations.md](docs/améliorations.md)       | Les pistes d'amélioration de performance, avec métriques et objectifs                                      |

## Démarrage rapide

```bash
# Backend (depuis backend/)
cp .env.example .env
uv sync
uv run --env-file .env src/main.py      # http://localhost:8000

# Tests
uv run --env-file .env pytest

# Frontend (depuis frontend/)
npm install
npm run dev                              # http://localhost:3000
```

Les prérequis, les variables d'environnement et le démarrage de la base PostgreSQL sont
détaillés dans [architecture.md](docs/architecture.md#lancer-le-projet).

## Application déployée

- **Frontend** : https://newsfoundry.vercel.app
- **Backend** : https://newsfoundry-production-f730.up.railway.app

Compte de test : `test@test.com` / `test`
