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

def insert_card(member: str, title: str, line: str, desc: str):
    card_collection.insert_one({
        "member": member,
        "title": title,
        "line": line,
        "desc": desc
    })
    return True

def register_user(user_id: int):
    existing = get_user_by_user_id(user_id)
    if existing:
        return False  # already registered

    user_collection.insert_one({
        "user_id": user_id
        , "registered": True
    })
    return True

def get_user_by_user_id(user_id: int):
    existing = user_collection.find_one({"user_id": user_id})
    if not existing:
        return False
    return existing