from openai import OpenAI
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

def get_recommended_games(user_input:str)->json:
    client = OpenAI(api_key=KEY)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "developer",
                "content": recommended_games_input
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
    )


    response_text = response.output_text

    if response_text:
        try:
            game_list = json.loads(response_text)
            print("✅ Parsed JSON:", game_list)
            return game_list
        except json.JSONDecodeError as e:
            print("❌ JSON parsing failed:", e)
    else:
        print("❌ No content returned in response.output_text")


def get_game_description(game:str)->str:
    client = OpenAI(api_key=KEY)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "developer",
                "content": description_game_input
            },
            {
                "role": "user",
                "content": game
            }
        ]
    )
    return response.output_text