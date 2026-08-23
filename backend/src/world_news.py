import os
import httpx
from datetime import date
from sqlmodel import Session
from database import engine
from models import News

async def fetch_top_news():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.worldnewsapi.com/top-news",
                params={"source-country": "fr", "language": "fr"},
                headers={"x-api-key": os.getenv("WORLD_NEWS_API_KEY", "")},
            )
        except httpx.RequestError as e:
            print(f"Erreur réseau de World news API : {e}")
            return "Impossible de contacter le service d'actualiés. Précise cela à l'utilisateur au début de ta réponse."
        # Les erreurs dans les logs serveur et pour l'IA lors de sa réponse. 
        if response.status_code == 402:
            print("Erreur World News API : quota quotidien dépassé")
            return "Les actualités du jour n'ont pas pu être chargées (quota quotidien de l'API dépassé). Précise cela à l'utilisateur au début de ta réponse."
        if response.status_code == 429:
            print("Erreur World News API : trop de requêtes")
            return "Les actualités du jour n'ont pas pu être chargées (trop de requêtes envoyées à l'API). Précise cela à l'utilisateur au début de ta réponse."
        if response.status_code != 200:
            print(f"Erreur World News API : code {response.status_code}")
            return f"Les actualités du jour n'ont pas pu être chargées (erreur technique, code {response.status_code}). Précise cela à l'utilisateur au début de ta réponse."
        
        data = response.json()
        
        articles = []
        for cluster in data["top_news"]:
            article = cluster["news"][0]
            summary = article.get('summary', '')
            if not summary:
                summary = article.get('text', '')[:150]
            articles.append(f"- {article.get("title", 'Titre indisponible')}: {summary}")

        result =  "\n".join(articles)
        print(f"Actualités récupérées : {result}")
        return result
    
async def get_daily_prompt():
    today = date.today()
    with Session(engine) as session:
        news = session.get(News, today)
        if news: return news.content

        content = await fetch_top_news()
        news = News(date=today, content=content)
        session.add(news)
        session.commit()
        return content

async def get_search_news(query):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://api.worldnewsapi.com/search-news",
                params={"text": query, "language": "fr", "number": 5},
                headers={"x-api-key": os.getenv("WORLD_NEWS_API_KEY", "")},
            )
        except httpx.RequestError as e:
            print(f"Erreur réseau de World news API : {e}")
            return "Impossible de contacter le service d'actualités. Précise cela à l'utilisateur au début de ta réponse."
        if response.status_code == 402:
            print("Erreur World News API : quota quotidien dépassé")
            return "La recherche n'a pas aboutis (quota quotidien de l'API dépassé). Précise cela à l'utilisateur au début de ta réponse."
        if response.status_code == 429:
            print("Erreur World News API : trop de requêtes")
            return "La recherche n'a pas aboutis (trop de requêtes envoyées à l'API). Précise cela à l'utilisateur au début de ta réponse."
        if response.status_code != 200:
            print(f"Erreur World News API : code {response.status_code}")
            return f"La recherche n'a pas aboutis (erreur technique, code {response.status_code}). Précise cela à l'utilisateur au début de ta réponse."

        data = response.json()
        search_article = []
        for article in data["news"]:
            summary = article.get("summary", "")

            if not summary:
                summary = article.get('text', '')[:150]

            search_article.append(f"- {article.get("title", "Titre indisponible")} : {summary}")

        result = "\n".join(search_article)
        print("------------------------------------------------------------")
        print(f"La recherche fais par l'agent : {result}")
        print("------------------------------------------------------------")
        return result
        