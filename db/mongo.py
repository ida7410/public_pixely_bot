from typing import Tuple

from pymongo import MongoClient
from config import MONGO_URI

client = None
db = None
youtube_channels_collection = None
discord_servers_collection = None
card_collection = None
user_collection = None

def connect_db():
    global client, youtube_channels_collection, discord_servers_collection, card_collection, user_collection
    client = MongoClient(MONGO_URI)
    db = client["youtube_bot"]
    print(f"db connected: {db.name}")

    # separate collections
    youtube_channels_collection = db["youtube_channels"]
    discord_servers_collection = db["discord_servers"]
    card_collection = db["card"]
    user_collection = db["user"]


def register_server(server_id: int, owner_id: int):
    existing = get_user_by_user_id(server_id)
    if existing:
        return False  # already registered

    discord_servers_collection.insert_one({
        "server_id": server_id
        , "owner_id": owner_id
        , "target_rule_message_id": ""
        , "target_role_message_id": ""
        , "target_youtube_message_id": ""
        , "registered": True
    })
    return True


def update_server(server_id: int, owner_id: int, type_of: str
                    , target_message_id: int = ""):
    existing = get_user_by_user_id(server_id)
    if not existing:
        return False  # server doesn't exist

    discord_servers_collection.update_one(
        filter={
            "server_id": server_id
            , "owner_id": owner_id
        }
        ,update={
            "$set": {f"target_{type_of}_message_id": target_message_id}
        }
    )
    return True

def get_server_by_server_id(server_id: int):
    existing = discord_servers_collection.find_one({"server_id": server_id})
    if not existing:
        return False
    return existing

def update_channel_data(channel_id: int, last_id, type_of: str) :
    youtube_channels_collection.update_one(
        filter={"channel_id": channel_id}
        , update={"$set": {type_of: last_id}}
    )

def insert_card(member: str, classes: str, title: str, desc: str, line: str):
    card_collection.insert_one({
        "member": member,
        "class": classes,
        "title": title,
        "desc": desc,
        "line": line
    })
    return True

def register_user(user_id: int, pack: Tuple[str, str]):
    existing = get_user_by_user_id(user_id)
    if existing:
        return False  # already registered

    user_collection.insert_one({
        "user_id": user_id
        , "cards_id": []
        , "deck": []
        , "pack": [{"type": pack[0], "class": pack[1]}]
        , "registered": True
    })
    return True

def get_user_by_user_id(user_id: int):
    existing = user_collection.find_one({"user_id": user_id})
    if not existing:
        return False
    return existing

def add_pack_user(user_id: int, pack: Tuple[str, str]) :
    user_collection.update_one(
        {"user_id": user_id},
        {"$push": {"pack": {"type": pack[0], "class": pack[1]}}}
    )

def delete_pack_user(user_id: int, pack: Tuple[str, str]) :
    user = user_collection.find_one({"user_id": user_id})
    for index, pack_db in enumerate(user["pack"]):
        if pack_db["type"] == pack[0] and pack_db["class"] == pack[1]:
            new_pack = user["pack"][:index] + user["pack"][index + 1:]
            user_collection.update_one(
                {"user_id": user_id},
                {"$set": {"pack": new_pack}}
            )

def get_card_by_id(card_id):
    existing = card_collection.find_one({"_id": card_id})
    if not existing:
        return False
    return existing

def get_card_by_card_id_type_name_class_name(card_id, type_name, class_name):
    existing = card_collection.find_one({
        "card_id": card_id,
        "type": type_name,
        "class": class_name
    })
    if not existing:
        return False
    return existing

def add_card_to_user(user_id, card_id):
    user_collection.update_one(
        {"user_id": user_id},
        {"$push": {"cards_id": card_id}}
    )

def get_cards_by_user_id(user_id):
    user = user_collection.find_one({"user_id": user_id})
    if not user:
        return False

    cards_id = user["cards_id"]
    cards = []
    for card_id in cards_id:
        card = get_card_by_id(card_id)
        cards.append(card)
    return cards