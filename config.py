import json
import os

from discord import Color

TOKEN = os.getenv("BOT_TOKEN")
MONGO_URI = os.getenv("MONGO_URI")

# Load all cogs
extensions = [
    "cogs.reaction_roles"
    , "cogs.personal_color"
    , "cogs.private_channel"
    , "cogs.youtube_tracker"
    , "cogs.server_setting"
    , "cogs.server_joined"
    , "insert_card"
    , "cogs.user_register"
    , "cogs.user_card_pack"
    , "cogs.user_card_deck"
    , "cogs.create_game"
    , "cogs.card_deck"
    , "cogs.game_hp"
]

with open("./PIXELY_EMOJI.json", "r", encoding="utf-8") as f:
    TARGET_EMOJI_PIXELY = json.load(f)
TARGET_EMOJI_EX = {
    '🥦': '팀샐', '🍊': '패스', '🎙️': '시스', '💡': '그외'
}

with open("lang.json", "r", encoding="utf-8") as f:
    lang = json.load(f)

with open("lang_en.json", "r", encoding="utf-8") as f:
    lang_en = json.load(f)

with open("lang_ko.json", "r", encoding="utf-8") as f:
    lang_ko = json.load(f)

def get_message(key, local="en", **kwargs):
    template = lang.get(key, {}).get(local, "").get("response", "")
    return template.format(**kwargs)

def get_color(member):
    if member == "rather":
        color = Color.red()
    elif member == "duckgae":
        color = Color.orange()
    elif member == "heptagram":
        color = Color.yellow()
    elif member == "dino":
        color = Color.green()
    elif member == "sleepground":
        color = Color.blue()
    elif member == "suhyen":
        color = Color.purple()
    else:
        color = Color.light_grey()
    return color