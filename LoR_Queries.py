import requests

def board():
    url = "http://127.0.0.1:21337/positional-rectangles"
    try:
        data = requests.get(url = url).json()
        return data
    except:
        return None
    return None

def get_game_result():
    url = "http://127.0.0.1:21337/game-result"
    data = requests.get(url = url).json()
    return data

def get_last_game():
    result = get_game_result()
    return result["GameID"], result["LocalPlayerWon"]

def cards():
    r = board()
    if r != None:
        return r["Rectangles"]  
    else: 
        return None

def get_card_pos(card):
    for c in cards():
        if c["CardID"] == card["CardID"]:
            return (c["TopLeftX"], c["TopLeftY"])
    return (card["TopLeftX"], card["TopLeftY"])

def get_playable_cards():
    board_cards = cards()
    playable_cards = []
    if cards != None:
        for card in board_cards:
            if card["CardCode"] != "face":
                playable_cards.append(card)
    return playable_cards

def get_my_cards():
    board_cards = cards()
    my_cards = []
    if cards != None:
        for card in board_cards:
            if card["CardCode"] != "face" and card["LocalPlayer"] == True:
                my_cards.append(card)
    return my_cards

def is_game_in_progress():
    if len(cards()) > 0:
        return True
    return False