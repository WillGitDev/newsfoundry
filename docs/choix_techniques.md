# Choix techniques

## Choix techniques imposés pour le début du projet

Le CTO à fixé la stack technique avant le début du projet. Voici ces choix et les raisons données.

| Choix imposé          | Raison donnée                                     |
| --------------------- | ------------------------------------------------- |
| Python                | Écosystème de bibliothèques IA                    |
| FastAPI               | Développement de l'API                            |
| SQLModel + PostgreSQL | ORM conçu pour bien s'intégrer à FastAPI          |
| JWT                   | Authentification                                  |
| PydanticAI            | Client LLM, s'intègre au reste de la pile backend |
| uv                    | Gestion des dépendances                           |
| Next.js               | Frontend                                          |
| World News API        | Source des actualités                             |
| Vercel + Railway      | Déploiement                                       |

## Backend

### Deux agents distincts

Deux agents ont été créés pour avoir des agents spécialisés qui sont plus performants qu'un agent généraliste.

- `agent` répond dans le chat. Il reçoit automatiquement les actualités du jour, et dispose en plus de l'outil `search_news` pour rechercher des informations supplémentaires si besoin.

- `revue_agent`à partir de la discussion et du sujet renseigné il va créer une revue.

### Sortie structurée pour la revue de presse

`revue_agent` est déclaré avec `output_type`. Ce qui permet de contraindre le modèle à répondre selon ce schéma

```python
class RevuesOutput(BaseModel):
    titre: str
    synthese_generale: str
    synthese_articles: list[ArticleSynthese]
```

Sans cela, il aurait fallu demander un format dans le prompt puis découper la réponse
avec des expressions régulières — fragile, et cassé au premier écart du modèle. Ici les
champs arrivent déjà séparés et validés, prêts à être écrits en base.

Le schéma est volontairement calqué sur les colonnes ajoutées à la table `chat`, ce qui
réduit la route `POST /chats/{id}/revue` à une simple recopie champ par champ.

### Les actualités du jour sont mises en cache une fois par jour

`get_daily_prompt()` cherche d'abord une entrée dans la table `news` à la date du jour.
Si elle existe, elle est renvoyée sans appeler World News API.
Cela limite l'appel à l'API et permet de garder le contexte de la conversation.

### Une panne d'actualités n'interrompt pas la conversation

En cas d'erreur de World News API, les fonctions ne lèvent pas d'exception : elles
renvoient une phrase en français destinée au modèle, l'invitant à prévenir l'utilisateur.

L'agent reste ainsi utilisable — il peut répondre sur ce qu'il sait déjà — et
l'utilisateur comprend pourquoi les informations manquent, au lieu de recevoir une
erreur technique. Une source d'actualités indisponible dégrade le service, elle ne
l'interrompt pas.

### Un `404` plutôt qu'un `403` sur les chats d'autrui

Répondre `403 Forbidden` confirmerait l'existence de la discussion. Le `404` rend
indiscernables « ce chat n'existe pas » et « ce chat ne vous appartient pas ».
C'est un point de sécurité couvert par deux tests.

## Frontend

### JavaScript et CSS Modules

Le projet a été initialisé en JavaScript, avec des CSS modules.

Le choix de CSS Modules est adapté au projet : chaque composant peut définir son style et permet de gérer la spécificité au niveau du fichier. Les noms de classe sont générés et uniques donc aucune collision de noms n'est possible.

### Une couche d'accès unique au backend

`libs/api.js` centralise la totalité des échanges réseau : URL de base, jeton
d'authentification, déconnexion automatique sur `401`, extraction du message d'erreur.

Le bénéfice se mesure au nombre d'endroits à modifier lors d'un changement. Le jour où
le format du jeton évolue, un seul fichier est concerné, et les six appels de
l'application en bénéficient.

### Un hook pour les lectures, un appel direct pour les écritures

La règle est décrite dans `architecture.md`. Sa justification est une contrainte de
React : un hook ne peut être appelé qu'au niveau supérieur d'un composant, jamais dans
un gestionnaire d'événement.

`useFetch` répond au besoin « charger des données dès l'affichage » — il encapsule le
`useEffect` et les trois états (`data`, `loading`, `error`) que chaque composant devrait
sinon réécrire. Une écriture déclenchée par un clic n'a pas ce besoin : le clic répond
déjà à la question « quand ? ».

Le hook accepte un chemin `null` et ne déclenche alors aucune requête. Ce cas correspond
au composant `Chat` affiché sans discussion ouverte : il n'y a rien à charger, et
`loading` passe immédiatement à `false` plutôt que de laisser un indicateur tourner
indéfiniment.

### La page de connexion n'utilise pas `apiFetch`

C'est la seule exception à la règle précédente, et elle est délibérée.

`apiFetch` réagit à un `401` en supprimant le jeton et en redirigeant vers `/`. Or un
mot de passe incorrect renvoie précisément un `401`, et `/` est déjà la page de
connexion : l'utilisateur verrait un rechargement silencieux au lieu du message
« Email ou mot de passe incorrect ».

La page de connexion appelle donc `fetch` directement et gère elle-même son cas d'erreur.

### Les réponses du modèle sont rendues en Markdown

Les LLM formatent spontanément leurs réponses en Markdown (titres, listes, gras).
Affichées telles quelles, ces réponses feraient apparaître les astérisques et les dièses
à l'écran.

`react-markdown` interprète cette syntaxe, ce qui rend les revues de presse — dont le
prompt demande explicitement des listes à puces — nettement plus lisibles.

### État partagé remonté au parent

Sur la page d'une discussion, `ChatThreadWrapper` détient l'état `title` et le
transmet à deux composants : `ChatThreadHeader` pour l'afficher, et `Chat` via une
fonction de rappel pour le mettre à jour dès que les messages sont chargés.

C'est le motif classique du « remontée d'état » : deux composants voisins ont besoin de
la même donnée, elle est donc placée dans leur premier ancêtre commun. Le rappel est
optionnel, ce qui permet de réutiliser `Chat` sur les pages qui n'affichent pas de
titre.
