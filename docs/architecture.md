# Architecture du projet Newsfoundry

## Vue d'ensemble

NewsFoundry est une application pour les journalistes/pigistes, qui propose des fonctionnalités IA pour les aider dans leurs recherches et la rédaction d'articles, assistée par un LLM.

Le parcours utilisateur se déroule en trois étapes :

1. L'utilisateur discute avec l'agent, déjà informé des actualités du jour.
2. Il peut lui demander des recherches sur des sujets précis.
3. À partir de la conversation, il génère une revue de presse.

## Structure des fichiers

Le projet est un monorepo. On retrouve le code backend et frontend dans des fichiers séparés.

```
P14DevIA/
├── backend/            API Python (FastAPI) — déployée sur Railway
├── frontend/           Interface Next.js — déployée sur Vercel
├── docs/               Cette documentation
└── .github/workflows/  Intégration continue (exécution des tests)
```

## Backend

```
backend/
├── Dockerfile          Image utilisée par Railway
├── pyproject.toml      Dépendances (gérées par uv)
└── src/
    ├── main.py         L'API : configuration, authentification, routes
    ├── agents.py       Les deux agents PydanticAI et leurs instructions
    ├── models.py       Modèles de base de données et schémas de requête/réponse
    ├── database.py     Connexion PostgreSQL, création des tables, utilisateur de test
    ├── world_news.py   Appels à World News API
    └── test_main.py    Tests pytest
```

### Présentation des fichiers

Dans le fichier `main.py` :

- La gestion du CORS.
- Les différentes API de l'application.

Dans le fichier `agents.py` :

- Les prompts.
- Les agents (pour la recherche et la génération de revue).

Dans le fichier `models.py` :

- Les tables qui héritent de SQLModel.
- Les schémas d'échanges.

Dans le fichier `database.py` :

- La création du moteur SQLModel.

Dans le fichier `world_news.py` :

- L'appel à `/top-news` pour la récupération des articles du jour.
- L'appel à `/search-news` pour la recherche précise sur un sujet.

## Modèle de données

| Table  | Contenu                                                                                                                                           |
| ------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `user` | Un compte : email unique et mot de passe haché avec bcrypt.                                                                                       |
| `chat` | Une discussion : son propriétaire, l'historique complet des messages au format JSON, et les champs de la revue de presse générée à partir d'elle. |
| `news` | Le résumé des actualités d'une journée, indexé par date. Sert de cache.                                                                           |

## Frontend

```
frontend/src/
├── app/            Les pages (routage par le système de fichiers)
├── components/     Les composants d'interface réutilisables
├── hooks/          useFetch — charger des données à l'affichage d'un composant
├── libs/           api.js (appels au backend) et auth.js (jeton d'authentification)
└── util/           Formatage des dates et des heures
```

### Les pages

Next.js App Router associe une URL à chaque dossier de `app/` :

| URL                  | Fichier                          | Rôle                                                    |
| -------------------- | -------------------------------- | ------------------------------------------------------- |
| `/`                  | `app/page.js`                    | Connexion                                               |
| `/HomeChat`          | `app/HomeChat/page.jsx`          | Accueil : liste des discussions et écran d'introduction |
| `/HomeChat/[chatId]` | `app/HomeChat/[chatId]/page.jsx` | Une discussion ouverte                                  |
| `/HomeChat/revues`   | `app/HomeChat/revues/page.jsx`   | Les revues de presse générées                           |

### Les composants

Chaque composant est dans un dossier portant son nom. Il contient un fichier ".jsx" qui contient le code du composant et un fichier nomDuComposant.module.css qui contient les styles CSS.

```
components/Chat/
├── index.jsx           Le composant
└── chat.module.css     Ses styles, isolés
```

| Composant           | Rôle                                                          |
| ------------------- | ------------------------------------------------------------- |
| `PastChat`          | Barre latérale : logo, liste des discussions, déconnexion     |
| `DiscussionItem`    | Une ligne de la liste des discussions                         |
| `NavChat`           | Bascule entre « Chat » et « Revue de presse »                 |
| `Chat`              | Zone centrale : le contenu affiché et le champ de saisie      |
| `ChatMessages`      | La liste des messages d'une discussion                        |
| `ChatMessageBubble` | Une bulle de message                                          |
| `ChatThreadHeader`  | En-tête d'une discussion et fenêtre de génération de revue    |
| `InfoChat`          | Écran d'accueil affiché quand aucune discussion n'est ouverte |
| `ListRevue`         | La liste des revues de presse                                 |
| `CardRevue`         | Une revue de presse                                           |
| `Loader`            | Indicateur de chargement                                      |
| `Logo`              | Le logo NewsFoundry                                           |

### Circulation des données

Les appels faits au backend sont de cette forme :

`Composant -> useFetch -> apiFetch -> API backend`

Dans le fichier `libs/api.js` on retrouve la fonction `apiFetch` qui communique avec le backend.

Dans le fichier `hooks/useFetch.js` ici le hook personnalisé contient apiFetch pour le cas de chargement de données à l'affichage d'un composant. Cette fonction renvoie la donnée, l'état de chargement et les éventuelles erreur rencontrées sous cette forme :
`{data, loading, error}`, ce qui permet de signaler le chargement en utilisant la variable loading pour le composant Loader.

## Lancer le projet

### Prérequis

Docker, Python 3.13, [uv](https://docs.astral.sh/uv/), Node.js 22.19.

### Backend

```bash
cd backend
cp .env.example .env          # première fois seulement, puis renseigner les valeurs
uv sync                       # installer les dépendances

# Démarrer PostgreSQL (première fois, ou si le conteneur n'existe plus)
docker run --name newsfoundry_db \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=newsfoundry \
  -p 5432:5432 postgres:17

# Démarrer l'API sur http://localhost:8000
uv run --env-file .env src/main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev                   # http://localhost:3000
```

### Tests

```bash
cd backend
uv run --env-file .env pytest
```

Il faut rajouter l'option `--env-file .env` pour que les tests puissent récupérer l'adresse de la base de données.

Pour n'exécuter qu'un seul test :

```bash
uv run --env-file .env pytest src/test_main.py::test_send_message_creates_chat_history
```

### Variables d'environnement

**Backend** (`backend/.env`)

| Variable             | Rôle                                                               |
| -------------------- | ------------------------------------------------------------------ |
| `DATABASE_URL`       | Chaîne de connexion PostgreSQL                                     |
| `JWT_SECRET_KEY`     | Clé de signature des jetons d'authentification (32 octets minimum) |
| `ANTHROPIC_API_KEY`  | Accès au modèle Claude                                             |
| `WORLD_NEWS_API_KEY` | Accès à World News API                                             |

**Frontend** (`frontend/.env.local`)

| Variable              | Rôle                                            |
| --------------------- | ----------------------------------------------- |
| `NEXT_PUBLIC_API_URL` | Adresse du backend, ex. `http://localhost:8000` |

## Déploiement

| Partie               | Plateforme | URL                                                |
| -------------------- | ---------- | -------------------------------------------------- |
| Frontend             | Vercel     | https://newsfoundry.vercel.app                     |
| Backend + PostgreSQL | Railway    | https://newsfoundry-production-f730.up.railway.app |

Les deux plateformes sont connectées au dépôt GitHub et redéploient automatiquement à
chaque commit sur la branche `main`.
