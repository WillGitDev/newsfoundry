# Les prompts et leurs raisons

Les instructions des deux agents sont regroupées dans `backend/src/agents.py`, sous
forme de constantes nommées (`INSTRUCTIONS_CHAT`, `INSTRUCTIONS_REVUE`) plutôt qu'écrites
directement dans les appels `Agent(...)`. Un prompt est du contenu que l'on relit et que
l'on ajuste souvent : le sortir du code le rend lisible et modifiable sans risquer de
casser la construction de l'agent.

---

## L'agent de chat

```python
INSTRUCTIONS_CHAT = (
    "Tu es un assistant de journaliste ou de pigistes pour un public français. "
    "Tu dois aider les pigistes à gagner du temps et aussi à améliorer la qualité "
    "de leurs articles. Sois factuel et professionnel, il faut un contenu "
    "journalistique. Demande à l'utilisateur quel style et quelle forme adopter "
    "pour ses articles. Pour les revues de presse il faut s'appuyer sur des faits, "
    "c'est un point important si tu ne peux pas répondre à la question il faut le "
    "dire que tu ne sais pas"
)
```

### Ce que chaque consigne cherche à obtenir

| Consigne                                                           | Intention                                                                                                                                                                                                                                   |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| « assistant de journaliste ou de pigistes »                        | Donner un rôle. Un modèle à qui l'on assigne un métier adopte le vocabulaire et les réflexes de ce métier — ici, citer ses sources et distinguer les faits des commentaires.                                                                |
| « pour un public français »                                        | Fixer la langue de réponse et le cadre de référence. Sans cela, le modèle bascule facilement vers l'anglais ou vers des références nord-américaines.                                                                                        |
| « gagner du temps » et « améliorer la qualité »                    | Rappeler l'objectif produit énoncé dans le brief. Les réponses restent orientées vers un usage professionnel plutôt que vers de la conversation généraliste.                                                                                |
| « Sois factuel et professionnel »                                  | Écarter le ton promotionnel ou familier que les modèles adoptent par défaut.                                                                                                                                                                |
| « Demande à l'utilisateur quel style et quelle forme adopter »     | Rendre l'agent actif. Plutôt que de produire un texte au hasard, il interroge le pigiste sur son format — brève, analyse, revue — ce qui correspond à l'étape « affiner la recherche » du parcours utilisateur.                             |
| « s'appuyer sur des faits »                                        | Contrer la tendance des modèles à combler les lacunes par de la plausibilité. Un article de presse construit sur une invention est inutilisable.                                                                                            |
| « si tu ne peux pas répondre… il faut le dire que tu ne sais pas » | **Autoriser explicitement l'aveu d'ignorance.** C'est la consigne la plus importante du prompt : sans elle, un modèle préfère produire une réponse fausse plutôt qu'aucune réponse. Elle est indispensable dans un contexte journalistique. |

### Les actualités du jour

Ce mécanisme répond à la "cutt of date" du modèle : Claude ne connaît rien de ce qui
s'est passé après son entraînement. Sans injection, il répondrait avec assurance sur une
actualité vieille de plusieurs mois, ou refuserait de répondre.

Deux décisions accompagnent cette injection :

- Seuls le titre et le résumé de chaque article sont transmis, jamais le contenu
  complet. Le prompt reste court, ce qui réduit le coût, la latence, et le risque que le
  modèle se perde dans un contexte trop long.
- Le texte est persisté en base pour la journée (table `news`). Sans cela, le
  contexte changerait d'un jour à l'autre et une discussion entamée la veille deviendrait
  incohérente.

### L'outil de recherche

La description d'un outil est elle-même un prompt : c'est sur elle que le modèle décide
d'appeler l'outil ou non.

```python
@agent.tool_plain
async def search_news(query: str) -> str:
    """Recherche des articles d'actualité sur un sujet précis.
    À utiliser quand l'utilisateur veut plus d'informations sur un thème donné."""
```

La docstring comporte deux phrases distinctes : la première dit ce que fait l'outil,
la seconde quand l'utiliser. La seconde est celle qui compte : sans condition
d'usage explicite, un modèle appelle un outil disponible trop souvent, ou l'ignore.

Le format d'échange est volontairement simple — une chaîne de caractères en entrée, du
texte en sortie — plutôt que la réponse brute de World News API, qui est un objet JSON
complexe. Le brief le recommande explicitement : des entrées et sorties simples
facilitent l'usage de l'outil par l'agent.

---

## L'agent de revue de presse

```python
INSTRUCTIONS_REVUE = (
    "Tu es un assistant de journaliste ou de pigistes pour un public français. "
    "Tu dois faire une revue en t'appuyant sur toute la discussion de tous les "
    "articles et une synthèse pour chaque article. Pour la synthèse générale, "
    'commence par une ligne "REVUE DE PRESSE [SUJET] - jour Mois année", '
    "Pour le jour mois année met le jour en chiffre, le mois en lettre avec la "
    "première lettre en majuscule et l'année en chiffre (exemple: 30 Septembre 2025) "
    "Utilise la date exacte qui te sera donnée dans le message, ne l'invente jamais. "
    "Pour la mise en forme du reste du contenu, mets des listes à puces et des sauts "
    "de ligne entre chaque liste à puces"
)
```

### Ce que chaque consigne cherche à obtenir

| Consigne                                                                               | Intention                                                                                                                                                                              |
| -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Même rôle que l'agent de chat                                                          | Conserver le registre journalistique et la langue.                                                                                                                                     |
| « en t'appuyant sur toute la discussion »                                              | Rappeler que la matière première est l'historique complet, transmis via `message_history`, et pas seulement le sujet demandé.                                                          |
| « une synthèse pour chaque article »                                                   | Obtenir le champ `synthese_articles` attendu par le schéma de sortie.                                                                                                                  |
| Format d'en-tête imposé                                                                | Produire un rendu homogène d'une revue à l'autre, reconnaissable au premier coup d'œil.                                                                                                |
| Format de date détaillé, avec exemple                                                  | Un exemple concret vaut mieux qu'une description abstraite. « 30 Septembre 2025 » lève toute ambiguïté entre les formats français, anglais et numériques.                              |
| **« Utilise la date exacte qui te sera donnée dans le message, ne l'invente jamais »** | Consigne critique. Un modèle ne connaît pas la date du jour et en inventera une s'il en a besoin. La date réelle est calculée par le backend et transmise dans le message utilisateur. |
| Listes à puces et sauts de ligne                                                       | Le rendu final passe par `react-markdown`. Un texte structuré en listes est nettement plus lisible qu'un bloc de prose dans une carte de revue.                                        |

### Le message envoyé à l'agent

Contrairement au chat, où le message vient de l'utilisateur, la génération de revue
construit son message côté serveur :

```python
revue_date = datetime.now(timezone.utc)
result = await revue_agent.run(
    f"Le sujet choisi par l'utilisateur pour la revue : {revue_request.sujet}"
    f"La date du jour est : {revue_date.strftime('%d %B %Y')}.",
    message_history=history,
)
```

Deux informations seulement y figurent : le **sujet** saisi dans la fenêtre de
génération, et la **date du jour** calculée par le serveur. Cette même date est ensuite
enregistrée dans `revue_generated_at`, ce qui garantit que la date affichée dans le texte
et la date stockée en base sont identiques.

### La sortie structurée

`revue_agent` est déclaré avec `output_type=RevuesOutput`. PydanticAI transmet ce schéma
au modèle et valide la réponse. C'est une forme de contrainte plus fiable qu'une
consigne de format dans le prompt : le découpage en `titre`, `synthese_generale` et
`synthese_articles` est garanti par la bibliothèque, pas espéré du modèle.
