from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("API_KEY")

default_developer_input = """You are a game recommendation engine. Based on a list of favorite video games, suggest 5 to 10 other video games that the user is likely to enjoy. Focus on similarities in genre, gameplay mechanics, visual style, or overall experience.
Return only a valid JSON array of game titles as plain text. Do not use markdown formatting. Do not include any explanations, code blocks, or extra text — just the JSON array.
"""


def get_recommended_games(user_input:str, developer_input:str = default_developer_input):
    client = OpenAI(api_key=KEY)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "developer",
                "content": developer_input
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




