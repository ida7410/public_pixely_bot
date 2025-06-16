from db.mongo import insert_card, connect_db

connect_db()
with open("./card.txt", "r", encoding="utf-8") as cards_file:
    for card_line in cards_file:
        card_split = card_line.split("-")
        print(card_split)
        class_name = card_split[0]
        member = card_split[1]
        title = card_split[2]
        desc = card_split[3].replace('\\n', "\n")
        line = card_split[4].replace('\n', '')
        try:
            insert_card(member, class_name, title, desc, line)
            print(f"카드가 등록되었습니다!\nmember: {member} | class: {class_name}\n# \" {title} \"\n{desc}\n\n{line}")
        except Exception as e:
            print(e)