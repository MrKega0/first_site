from openai import AsyncOpenAI
import os
import json
from dotenv import load_dotenv
import asyncio

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
combined_prompt = """
You are a game recommendation engine. Given a comma-separated list of the user's favorite video game titles, suggest 5–10 additional games they are likely to enjoy.  
For each recommendation, output an object with the following keys:
  • name        – the game’s title  
  • genre       – the main genre in Russian (e.g. Симулятор, RPG, Стратегия)  
  • description – a short, engaging description in Russian, focusing on the game’s genre, gameplay, setting, and atmosphere  

Return ONLY a raw JSON array of these objects. Do NOT include any explanations, markdown, or extra text.
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

async def get_full_recommendations_for(new_names: list[str]) -> list[dict]:
    client = AsyncOpenAI(api_key=KEY)
    prompt = (
        "For each game in the following JSON array of new titles, "
        "return an array of objects with keys name, genre and description."
        "Do not use markdown formatting. Do not include any explanations, code blocks, or extra text — just the JSON array."
        "The description should be in Russian. Respond with raw JSON only:\n"
        + json.dumps(new_names)
    )
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content": prompt}
        ]
    )
    try:
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print("❌ Ошибка парсинга JSON:", e)
        return []

async def test():
    return await get_full_recommendations_for(['hearts of iron 4','Victoria 3'])

if __name__ == "__main__":
     print(asyncio.run(test()))