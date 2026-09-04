# Améliorations

Ce fichier présente les pistes d'amélioration que l'on pourrait implémenter.

### Interfaces de messagerie conversationnelle en flux continu

Actuellement dans l'application le contenu généré par le LLM est affiché en une fois quand on a reçu la réponse. Le temps de réponse peut être long et atténuer l'expérience utilisateur.
On peut à la place afficher les parties de la réponse au fur et à mesure de leur disponibilité comme les chatbots les plus connus sur le marché.

```python
async with agent.run_stream(message.content, message_history=history) as result:
    async for chunk in result.stream_text(delta=True):
        yield chunk # Envoyé au front-end au fur et à mesure

    chat.messages = json.loads(to_json(result.all_messages())) #après le flux
```

- run_stream() est un gestionnaire de contexte.
- delta=True renvoie les morceaux successifs plutôt que le texte complet à chaque fois.
- result.all_messages() n'est disponible qu'après la fin du flux.

Métrique mesurée avec MLFlow (en local sur dix essais sur POST /chats/{id}/messages) : l'utilisateur attend entre 3 et 6 secondes avant de voir le moindre caractère. Le détail de la requête montre que 99,99 % de ce temps est de l'attente serveur.
Objectif : afficher le premier caractère en une seconde pour rendre l'interface plus réactive.

### Temps de réponse pour la revue

Pour la génération de revue le temps de réponse est proportionnel à la longueur de la discussion.

Pour la génération d'une revue pour une discussion courte (5 à 10 échanges) le temps de réponse varie de : 9 à 12 secondes.
Pour une discussion longue (10 à 20 échanges) le temps de réponse varie de : 15 secondes à 20 secondes.

Solutions :

Deux approches que j'ai identifiées.

1. Réduire le chat aux dix derniers messages.

```python
history = ModelMessagesTypeAdapter.validate_python(chat.messages[-10:])
```

Cette solution a un inconvénient principal c'est que l'on perd une partie de la conversation ce qui peut impacter la qualité de la revue.

2. Limiter la longueur de la revue générée.

En ajoutant une consigne qui précise de synthétiser une dizaine d'articles les plus pertinents dans le prompt de `revue_agent`.

L'objectif est de ramener le temps de génération sous les 10 secondes. Un message explicite pendant l'attente ("Génération en cours, cela peut prendre de 10 à 20 secondes") pourrait être également implémenté pour que l'utilisateur ne quitte pas le site en pensant que l'application est bloquée.
