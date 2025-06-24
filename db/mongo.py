from typing import Tuple

from pymongo import MongoClient
from config import MONGO_URI

client = None
db = None
youtube_channels_collection = None
discord_servers_collection = None
card_collection = None
user_collection = None
game_collection = None

def connect_db():
    global client, youtube_channels_collection, discord_servers_collection, card_collection, user_collection, \
        game_collection
    client = MongoClient(MONGO_URI)
    db = client["youtube_bot"]
    print(f"db connected: {db.name}")

    # separate collections
    youtube_channels_collection = db["youtube_channels"]
    discord_servers_collection = db["discord_servers"]
    card_collection = db["card"]
    user_collection = db["user"]
    game_collection = db["game"]


def register_server(server_id: int, owner_id: int):
    existing = get_server_by_server_id(server_id)
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
    existing = get_server_by_server_id(server_id)
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

def insert_user(discord_user_id: int, pack: Tuple[str, str]):
    existing = get_user_by_user_discord_id(discord_user_id)
    if existing:
        return False  # already registered

    user_collection.insert_one({
        "discord_id": discord_user_id
        , "cards": []
        , "deck": []
        , "pack": [{"type": pack[0], "class": pack[1]}]
        , "log": ["registered"]
    })
    return True

def get_user_by_user_discord_id(user_discord_id):
    existing = user_collection.find_one({"discord_id": user_discord_id})
    if not existing:
        return False
    return existing

def add_pack_user_by_user_discord_id(user_discord_id: int, pack: Tuple[str, str]) :
    user_collection.update_one(
        {"discord_id": user_discord_id},
        {"$push": {"pack": {"type": pack[0], "class": pack[1], "log": f"{pack} added"}}}
    )

def update_user_game_by_user_discord_id(discord_id, game_id):
    user_collection.update_one({"discord_id": discord_id}, {"$set": {"game": game_id}})

def delete_pack_user_by_user_discord_id(discord_user_id: int, pack: Tuple[str, str]) :
    user = user_collection.find_one({"discord_id": discord_user_id})
    for index, pack_db in enumerate(user["pack"]):
        if pack_db["type"] == pack[0] and pack_db["class"] == pack[1]:
            new_pack = user["pack"][:index] + user["pack"][index + 1:]
            user_collection.update_one(
                {"discord_id": discord_user_id},
                {"$set": {"pack": new_pack}}
            )
            user_collection.update_one(
                {"discord_id": discord_user_id},
                {"$push": {f"{pack} deleted by unpacking"}}
            )

def get_card_by_id(card_id):
    existing = card_collection.find_one({"_id": card_id})
    if not existing:
        return False
    return existing

def get_card_by_title(card_title):
    existing = card_collection.find_one({"title": card_title})
    if not existing:
        return False
    return existing

def get_cards_by_class(class_name):
    return card_collection.find({"class": class_name})

def get_cards_by_class_member(class_name, member):
    return card_collection.find({"class": class_name, "member": member})

def add_card_to_user_by_discord_id(user_discord_id, card_id):
    quantity = get_card_quantity_by_user_discord_id_card_id(user_discord_id, card_id) + 1

    result = user_collection.update_one(
        {"discord_id": user_discord_id, "cards.card_id": card_id},
        {"$set": {"cards.$.quantity": quantity}}
    )

    if result.matched_count == 0:
        # Card doesn't exist, add it
        user_collection.update_one(
            {"discord_id": user_discord_id},
            {"$push": {"cards": {"card_id": card_id, "quantity": quantity}}}
        )

    user_collection.update_one(
        {"discord_id": user_discord_id},
        {"$push": {"log": f"card id {card_id} added to user"}}
    )

def get_user_deck_by_user_discord_id(discord_id):
    user = user_collection.find_one({"discord_id": discord_id})
    if not user:
        return False

    deck_cards_id = user["deck"]
    deck_cards = []
    for card_id in deck_cards_id:
        card = get_card_by_id(card_id)
        deck_cards.append(card)

    return deck_cards

def get_user_deck_cards_id_by_user_discord_id(discord_id):
    user = user_collection.find_one({"discord_id": discord_id})
    if not user:
        return False

    deck_cards_id = user["deck"]
    return deck_cards_id

def add_card_to_user_deck_by_discord_id(user_discord_id, card_id):
    user_collection.update_one(
        {"discord_id": user_discord_id},
        {"$push": {"deck": card_id}}
    )

def drop_user_deck_by_user_discord_id(user_discord_id):
    user_collection.update_one(
        {"discord_id": user_discord_id},
        {"$set": {"deck": []}}
    )

def get_cards_quantities_by_user_discord_id(user_id):
    user = user_collection.find_one({"discord_id": user_id})
    if not user:
        return False

    cards_id_quantity = user["cards"]
    return cards_id_quantity

def get_cards_by_user_discord_id(user_id):
    user = user_collection.find_one({"discord_id": user_id})
    if not user:
        return False

    cards_id_quantity = user["cards"]
    cards = []
    for card_id_quantity in cards_id_quantity:
        card = get_card_by_id(card_id_quantity["card_id"])
        cards.append(card)
    return cards

def get_card_quantity_by_user_discord_id_card_id(user_id, card_id):
    user = user_collection.find_one({"discord_id": user_id})
    if not user:
        return False

    cards = user["cards"]

    for card in cards:
        if card_id == card["card_id"]:
            card_quantity = card["quantity"]
            return card_quantity

    return 0

def get_games_by_user_discord_id(user_discord_id):
    games = list(game_collection.find({
        "$or": [
            {"player1.discord_id": user_discord_id},
            {"player2.discord_id": user_discord_id},
        ]
    }))
    if not games:
        return False
    return games

def get_game_by_id(game_id):
    game = game_collection.find_one({"_id": game_id})
    return game

def get_game_by_id_finished(game_id, finished):
    game = game_collection.find_one({"_id": game_id, "finished": finished})
    return game

def get_game_player_deck_by_game_id_user_discord_id(game_id, player_discord_id):
    game = get_game_by_id(game_id)
    player_num = get_game_player_num_by_game_id_player_discord_id(game_id, player_discord_id)

    deck = game[f"player{player_num}"]["deck"]
    return deck

def get_game_player_deck_by_game_id_player_num(game_id, player_num):
    game = get_game_by_id(game_id)
    deck = game[f"player{player_num}"]["deck"]
    return deck

def get_game_player_hand_by_game_id_user_discord_id(game_id, player_discord_id):
    game = get_game_by_id(game_id)
    player_num = get_game_player_num_by_game_id_player_discord_id(game_id, player_discord_id)

    hand = game[f"player{player_num}"]["hand"]
    return hand

def insert_game(thread_id, player1_discord_id, player1_deck, player2_discord_id, player2_deck, hp):
    result = game_collection.insert_one({
        "thread_id": thread_id,
        "player1": {
            "discord_id": player1_discord_id,
            "hp": hp,
            "deck": player1_deck,
            "hand": []
        },
        "player2": {
            "discord_id": player2_discord_id,
            "hp": hp,
            "deck": player2_deck,
            "hand": []
        },
        "original_hp": hp,
        "finished": False,
        "log": ["game started"]
    })
    if result:
        return result.inserted_id
    else:
        return False

def update_game_log_by_game_id(game_id, log: str):
    game_collection.update_one(
        {"_id": game_id},
        {"$push": {"log": log}}
    )

def update_game_finished_by_game_id(game_id, log: str = "game is over"):
    game_collection.update_one(
        {"_id": game_id},
        {"$set": {"finished": True}}
    )

    update_game_log(game_id, log)

def update_game_hp_by_game_id_player_num(game_id, player_num, hp: int, log: str = None):
    game = get_game_by_id(game_id)
    original_hp = game[f"player{player_num}"]["hp"]
    new_hp = original_hp + hp
    game_collection.update_one(
        {"_id": game_id},
        {
            "$set": {f"player{player_num}.hp": new_hp},
            "$push": {"log": log}
        }
    )

    update_game_log(game_id, log)

def update_game_player_deck_by_game_id_user_discord_id(game_id, player_discord_id, deck, log: str = None):
    player_num = get_game_player_num_by_game_id_player_discord_id(game_id, player_discord_id)

    game_collection.update_one(
        {
            "_id": game_id,
            f"player{player_num}.discord_id": player_discord_id
        },
        {
            "$set": {f"player{player_num}.deck": deck},
            "$push": {"log": log}
        }
    )

    update_game_log(game_id, log)

def update_game_player_deck_by_game_id_player_num(game_id, player_num, deck, log: str = None):
    game_collection.update_one(
        {"_id": game_id},
        {
            "$set": {f"player{player_num}.deck": deck},
            "$push": {"log": log}
        }
    )

    update_game_log(game_id, log)

def update_game_player_hand_by_game_id_player_num(game_id, player_num, card_id, log: str = None):
    game_collection.update_one(
        {"_id": game_id},
        {"$push": {f"player{player_num}.hand": card_id}}
    )
    update_game_log(game_id, log)

def update_game_drop_card_in_player_deck_hand_by_game_id_player_discord_id(game_id, player_discord_id, card_id, log: str = None):
    game = get_game_by_id(game_id)
    player_num = get_game_player_num_by_game_id_player_discord_id(game_id, player_discord_id)

    deck_cards_id = game[f"player{player_num}"]["deck"]
    index = deck_cards_id.index(card_id)
    new_deck = deck_cards_id[:index]
    new_deck.extend(deck_cards_id[index + 1:])

    log += get_card_by_id(card_id)["title"]
    update_game_player_deck_by_game_id_player_num(game_id, player_num, new_deck, log)
    update_game_player_hand_by_game_id_player_num(game_id, player_num, card_id)

    card = get_card_by_id(card_id)
    return card

def is_target_card_id_in_deck(target_card_id, deck):
    for card in deck:
        if card["_id"] == target_card_id:
            return True

    return False

def get_game_player_num_by_game_id_player_discord_id(game_id, player_discord_id):
    game = get_game_by_id(game_id)
    player_num = 0
    if game["player1"]["discord_id"] == player_discord_id:
        player_num = 1
    if game["player2"]["discord_id"] == player_discord_id:
        player_num = 2

    return player_num

def update_game_log(game_id, log: str = None):
    if log is not None:
        game_collection.update_one(
            {"_id": game_id},
            {
                "$push": {"log": log}
            }
        )