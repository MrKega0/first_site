from openai import AsyncOpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("API_KEY")


recommended_games_input = """You are a game recommendation engine. Based on a list of favorite video games, suggest 5 to 10 other video games that the user is likely to enjoy. Focus on similarities in genre, gameplay mechanics, visual style, or overall experience.
Return only a valid JSON array of game titles as plain text. Do not use markdown formatting. Do not include any explanations, code blocks, or extra text — just the JSON array.
"""
description_game_input = """You are a game description assistant for a video game database. Given the title of a video game, return a short, engaging description of the game in Russian. The description should be suitable for a general audience and focus on the game's genre, gameplay, setting, and atmosphere.
Do not include release date, developer name, platform information, or system requirements. Just describe the game.
Output only the Russian description as plain text. Do not include translations, titles, notes, or any extra formatting.
"""
game_genre_input = """You are a video game categorization assistant. Given the title of a video game, return only the main genre of that game in Russian. The genre should be a common, general term such as: платформер, метроидвания, рогалик, экшен, стратегия, головоломка, визуальная новелла, шутер, симулятор, песочница, RPG, и т.п.
Output only the genre name in Russian, as plain text. Do not include explanations, translations, or extra formatting.
"""

async def get_recommended_games(user_input: str) -> list[str]:
    client = AsyncOpenAI(api_key=KEY)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": recommended_games_input},
            {"role": "user", "content": user_input}
        ]
    )
    try:
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("❌ Ошибка парсинга JSON:", e)
        return []

async def get_game_description(game_title: str) -> str:
    client = AsyncOpenAI(api_key=KEY)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": description_game_input},
            {"role": "user", "content": game_title}
        ]
    )
    return response.choices[0].message.content.strip()

async def get_game_genre(game_title: str) -> str:
    client = AsyncOpenAI(api_key=KEY)
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": game_genre_input},
            {"role": "user", "content": game_title}
        ]
    )
    return response.choices[0].message.content.strip()