# API backend

Base locale : `http://localhost:8000`
Base production : `https://newsfoundry-production-f730.up.railway.app`

Une documentation interactive est générée automatiquement par FastAPI sur `/docs`.

## Authentification

Toutes les routes sauf `/` et `/login` exigent un jeton JWT dans l'en-tête :

```
Authorization: Bearer <token>
```

Le jeton est obtenu via `POST /login`. Il contient l'identifiant de l'utilisateur
(`user_id`), est signé en HS256 avec `JWT_SECRET_KEY`.

Côté frontend, `libs/api.js` ajoute cet en-tête automatiquement à chaque appel.

## Routes

### `GET /`

Route de santé. Permet de vérifier que l'API répond, notamment après un déploiement.

```json
{ "message": "👋" }
```

---

### `POST /login`

Authentifie un utilisateur et renvoie un jeton.

**Corps de la requête**

```json
{ "email": "test@test.com", "password": "test" }
```

**Réponse `200`**

```json
{ "token": "eyJhbGciOiJIUzI1NiIs..." }
```

---

### `POST /chats`

Crée une discussion vide appartenant à l'utilisateur authentifié.

**Réponse `200`**

```json
{ "id": 12, "created_at": "2026-08-30T09:14:22.310Z" }
```

---

### `GET /chats`

Liste les discussions de l'utilisateur authentifié.

**Réponse `200`**

```json
[
  { "id": 12, "created_at": "2026-08-30T09:14:22.310Z" },
  { "id": 9, "created_at": "2026-08-29T16:02:41.008Z" }
]
```

---

### `GET /chats/{chat_id}`

Renvoie l'historique d'une discussion, converti dans un format simple pour l'affichage.

**Réponse `200`**

```json
{
  "id": 12,
  "messages": [
    {
      "role": "user",
      "content": "Quelles sont les actualités du jour ?",
      "timestamp": "2026-08-30T09:15:00Z"
    },
    {
      "role": "assistant",
      "content": "Voici les principales actualités...",
      "timestamp": "2026-08-30T09:15:04Z"
    }
  ]
}
```

L'historique est stocké en base au format interne de PydanticAI, qui décrit chaque
message comme une liste de fragments typés (`user-prompt`, `text`, appels d'outils…).
La fonction `simplify_messages` l'aplatit avant l'envoi, afin que le frontend n'ait pas
à connaître ce format.

---

### `POST /chats/{chat_id}/messages`

Ajoute un message de l'utilisateur à une discussion et renvoie la réponse de l'agent.
L'historique complet de la discussion est mis à jour en base.

**Corps de la requête**

```json
{ "content": "Recherche des articles sur les incendies en Gironde" }
```

**Réponse `200`**

```json
{ "response": "Voici ce que j'ai trouvé sur ce sujet..." }
```

Cette route peut déclencher un ou plusieurs appels d'outil : si l'agent estime avoir
besoin d'articles supplémentaires, il appelle lui-même `search_news`, qui interroge
World News API. Ces appels sont invisibles pour l'appelant, mais allongent le temps de
réponse.

---

### `POST /chats/{chat_id}/revue`

Génère une revue de presse à partir de l'intégralité de la discussion, sur un sujet
choisi par l'utilisateur. Le résultat est enregistré sur la discussion.

**Corps de la requête**

```json
{ "sujet": "incendies" }
```

**Réponse `200`**

```json
{
  "titre": "Incendies en France",
  "synthese_generale": "REVUE DE PRESSE INCENDIES - 30 Août 2026\n\n...",
  "synthese_articles": [
    { "titre": "Le bilan des feux de l'été", "synthese": "..." }
  ],
  "revue_generated_at": "2026-08-30T10:59:12.442Z"
}
```

---

### `GET /revues`

Liste les revues de presse de l'utilisateur, c'est-à-dire ses discussions pour
lesquelles une revue a été générée.

**Réponse `200`**

```json
[
  {
    "id": 12,
    "titre": "Incendies en France",
    "synthese_generale": "...",
    "synthese_articles": [{ "titre": "...", "synthese": "..." }],
    "revue_generated_at": "2026-08-30T10:59:12.442Z"
  }
]
```

## Erreurs

Toutes les erreurs suivent le format de FastAPI : un objet JSON contenant une clé
`detail` avec un message en français, destiné à être affiché tel quel à l'utilisateur.

```json
{ "detail": "Chat introuvable" }
```

Côté frontend, `apiFetch` extrait ce `detail` et le transmet aux composants, qui
l'affichent dans une notification (`react-hot-toast`).

### Tableau des erreurs

| Code  | `detail`                             | Cause                                                                                          | Routes concernées                                                        |
| ----- | ------------------------------------ | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| `401` | `Email ou mot de passe incorrect`    | Identifiants invalides                                                                         | `POST /login`                                                            |
| `401` | `Token invalide`                     | Jeton absent, malformé ou signé avec une autre clé                                             | toutes les routes protégées                                              |
| `404` | `Chat introuvable`                   | La discussion n'existe pas **ou** appartient à un autre utilisateur                            | `GET /chats/{id}`, `POST /chats/{id}/messages`, `POST /chats/{id}/revue` |
| `422` | _(généré par FastAPI)_               | Corps de requête invalide, par exemple un champ manquant                                       | toutes les routes avec un corps                                          |
| `429` | `Crédit épuisé, réessayez plus tard` | Quota Anthropic dépassé                                                                        | `POST /chats/{id}/messages`, `POST /chats/{id}/revue`                    |
| `500` | `Erreur du service d'IA`             | Erreur du fournisseur LLM autre qu'un quota (clé invalide, modèle inexistant, requête refusée) | `POST /chats/{id}/messages`, `POST /chats/{id}/revue`                    |
| `504` | `Le service d'IA n'a pas répondu`    | Impossible de joindre le fournisseur LLM (réseau, délai dépassé)                               | `POST /chats/{id}/messages`, `POST /chats/{id}/revue`                    |

### Deux points d'attention

**Le `404` sur un chat appartenant à quelqu'un d'autre est délibéré.** Un `403
Forbidden` serait plus descriptif, mais il confirmerait à l'attaquant que la discussion
existe. Répondre `404` rend indiscernables les deux cas « ce chat n'existe pas » et « ce
chat ne vous appartient pas ». Ce comportement est couvert par les tests
`test_user_cannot_access_another_users_chat` et
`test_user_cannot_modify_another_users_chat`.

Les messages d'erreur LLM restent volontairement génériques. Le détail technique
(nom du modèle, corps de la réponse du fournisseur) est conservé dans les journaux du
serveur mais n'est jamais transmis au navigateur : il n'aiderait pas l'utilisateur et
renseignerait un attaquant sur l'infrastructure.

## Erreurs de World News API

Les appels à World News API ne remontent jamais d'erreur HTTP au frontend. Quand
l'API d'actualités échoue, `world_news.py` renvoie à la place une phrase destinée au
modèle, qui la relaie à l'utilisateur dans sa réponse :

| Situation                       | Message transmis à l'agent                                                                                |
| ------------------------------- | --------------------------------------------------------------------------------------------------------- |
| API injoignable                 | « Impossible de contacter le service d'actualités. Précise cela à l'utilisateur au début de ta réponse. » |
| `402` — quota quotidien dépassé | « Les actualités du jour n'ont pas pu être chargées (quota quotidien de l'API dépassé)… »                 |
| `429` — trop de requêtes        | « Les actualités du jour n'ont pas pu être chargées (trop de requêtes envoyées à l'API)… »                |
| Autre code HTTP                 | « … (erreur technique, code N)… »                                                                         |

Ce choix est expliqué dans `choix-techniques.md` : une panne de la source d'actualités
ne doit pas empêcher la conversation de se poursuivre.
