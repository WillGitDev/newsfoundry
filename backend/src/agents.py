from pydantic_ai import Agent
from world_news import get_daily_prompt, get_search_news
from models import RevuesOutput
MODEL = "anthropic:claude-haiku-4-5-20251001"

INSTRUCTIONS_CHAT = (
    "Tu es un assistant de journaliste ou de pigistes pour un public français. Tu dois aider les pigistes à gagner du temps et aussi à améliorer la "
    "qualité de leurs articles. Sois factuel et professionnel, il faut un contenu journalistique. Demande à l'utilisateur quel style et quelle forme "
    "adopter pour ses articles. Pour les revues de presse il faut s'appuyer sur des faits, c'est un point important si tu ne peux pas répondre à la question "
    "il faut le dire que tu ne sais pas"
)

INSTRUCTIONS_REVUE = (
    "Tu es un assistant de journaliste ou de pigistes pour un public français. Tu dois faire une revue en t'appuyant sur toute la discussion " 
    "de tous les articles et une synthèse pour chaque article. Pour la synthèse générale, commence par une ligne \"REVUE DE PRESSE [SUJET] - jour Mois annnée\" ," 
    "Pour le jour mois année met le jour en chiffre, le mois en lettre avec la première lettre en majuscule et l'année en chiffre (exemple: 30 Septembre 2025)" 
    "Utilise la date exacte qui te sera donnée dans le message, ne l'invente jamais. Pour la mise en forme du reste du contenue mes listes à puces et des saut de ligne entre chaque liste à puces"
)

agent = Agent(MODEL, instructions=INSTRUCTIONS_CHAT)

revue_agent = Agent(MODEL, instructions=INSTRUCTIONS_REVUE, output_type=RevuesOutput)

@agent.system_prompt
async def add_daily_news() -> str:
    content = await get_daily_prompt()
    return f"Voici les actualités du jour, à utiliser comme source d'information à jour :\n{content}"

@agent.tool_plain
async def search_news(query: str) -> str:
    """Recherche des articles d'actualité sur un sujet précis. 
    À utiliser quand l'utilisateur veut plus d'informations sur un thème donné."""
    search = await get_search_news(query)
    return f"Voici les résultats de la recherche :\n{search}"