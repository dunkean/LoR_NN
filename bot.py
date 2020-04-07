import time
import LoR_Handler, LoR_Brain, LoR_Queries
import random
import logging
import sys

brain = LoR_Brain.Brain()

def play(LoR, last_game_id):
    logging.info("Starting ingame loop")
    game_id, won = LoR_Queries.get_last_game()
    last_btn = ""
    last_btn_repeat = 0
    last_invoked_card_id = None
    while game_id == last_game_id:
        btn = LoR.ocr_btn_txt()
        cards = LoR.get_board_cards()
       
        if last_btn == btn and not ("turn" in btn or "onent" in btn or "pone" in btn):
            last_btn_repeat = last_btn_repeat + 1
        else:
            last_btn_repeat = 0
            last_btn = btn

        if last_btn_repeat > 10:
            logging.warning("btn value is the same for 10 times: %s, click next", last_btn)
            LoR.click_next()
            continue

        #print("***", btn, "***")
        if "round" in btn or "pass" in btn: #"END_ROUND" #PASS
            logging.info("Player's turn")
            time.sleep(0.5)
            status = LoR.get_status()
            print(status.to_string())
            logging.info("Status: %s", status.to_string())

            card = brain.choose_card_to_cast(cards, status)
            if card == None or card["CardID"] == last_invoked_card_id:
                logging.info("No card to cast")
                last_invoked_card_id = None
                if status.atk_token == True:
                    attackers = brain.choose_attackers(cards, status)
                    for attacker in attackers:
                        logging.info("Attack with %s", attacker["name"])
                        LoR.drag_to_center(attacker)
                        time.sleep(0.5)
                LoR.click_next()
            else:
                logging.info("Casting > %s", card["name"])
                LoR.drag_to_center(card)
                last_invoked_card_id = card["CardID"]
                time.sleep(1)
                    
        elif "skip" in btn: # SKIP BLOCK
            logging.info("Blocking action")
            status = LoR.get_status()
            print(status.to_string())
            logging.info("Status: %s", status.to_string())

            blocks = brain.choose_blockers(cards, status)
            for block in blocks:
                logging.info("Blocking %s with %s", block[0]["name"], block[1]["name"])
                LoR.drag_to_block(block)
                time.sleep(0.5)
            LoR.click_next()

        elif "select" in btn:
            logging.info("pass - but need to select target")
            pass

        elif "attack" in btn or "block" in btn: ## should not happens coz its a validation #BLOCK #ATTACK
            logging.info("validate block or attack")
            LoR.click_next()

        elif "ok" in btn and len(cards.cast) > 0 and cards.cast[0]["LocalPlayer"] == True: ## own cast validation Should not happen
            logging.info("validate cast")
            LoR.click_next()

        elif "ok" in btn and (len(cards.cast) == 0 or cards.cast[0]["LocalPlayer"] == True):
            logging.info("validate invocation")
            LoR.click_next()

        elif "turn" in btn or "onent" in btn or "pone" in btn:
            logging.info("opponent turn")

        elif "summon" in btn:
            logging.info("summoning in progress")
        else:
            logging.info("waiting to have more info")
        
        time.sleep(2)
        #check if game finished
        game_id, won = LoR_Queries.get_last_game()
        if "round" not in btn and "pass" not in btn:
            last_invoked_card_id = None

    return game_id, won



def mulligan(LoR):
    logging.info("Mulligan...")
    cards = LoR_Queries.get_my_cards()
    to_mulligan = brain.mulligan(cards)
    LoR.click_mulligan(to_mulligan)
    LoR.click_next()

def launch_match(LoR, mode):
    logging.info("Launching match vs %s", mode)
    if mode == "bot":
        LoR.wait_for_image(["Play", "vsAI"])
    elif mode == "challenger":
        LoR.wait_for_image(["Friends", "Spare", "Challenge"])
    elif mode == "challenged":
        LoR.wait_for_image(["Accept"])



# def game_session():



def loop(mode = "bot"):
    logging.info("Starting bot.")
    LoR = LoR_Handler.launch()
    logging.info("Game hooked.")
    
    if LoR_Queries.is_game_in_progress() == False:
        logging.info("No game in progress.")
        launch_match(LoR, mode)
        LoR.wait_for_selection_menu()
        LoR.wait_for_image(["Versus", "Ready"])
    else:
        logging.info("Game already started.")
    
    # GAME SESSION
    game_session = True
    last_game_id, _ = LoR_Queries.get_last_game()
    game_count = 1
    
    while game_session == True:
        LoR.wait_for_game_to_start()

        ## play
        if LoR.detect("Mulligan") != None:
            logging.info("Mulligan detected")
            mulligan(LoR)
        game_id, won = play(LoR, last_game_id)

        ## restart
        last_game_id = game_id
        print("Game ", game_count, "finished >", "Victory" if won == True else "Defeat")
        game_count = game_count + 1
        time.sleep(25)
        LoR.wait_for_image(["Continue", "Ready"])


if sys.argv[1] == "capture":
    LoR_Handler.raw_capture()
else:
    loop(sys.argv[1])

# def rematch(LoR, mode):
#     LoR.exit()
#     loop(mode)


## OUT OF GAME
# http://127.0.0.1:21337/positional-rectangles ## screen + board state  
# {"PlayerName":null,"OpponentName":null,"GameState":"Menus","Screen":{"ScreenWidth":1920,"ScreenHeight":1080},"Rectangles":[]}

### IN GAME
# http://127.0.0.1:21337/static-decklist ## activated decklist
# {"DeckCode":"CEAQUAIAAEDAYFA5EISCOLJPAECACAADCUNDMAICAEAAONA","CardsInDeck":{"01DE001":3,"01DE006":3,"01DE012":3,"01DE020":3,"01DE029":3,"01DE034":3,"01DE036":3,"01DE039":3,"01DE045":3,"01DE047":3,"01DE003":2,"01DE021":2,"01DE026":2,"01DE054":2,"01DE007":1,"01DE052":1}}

# http://127.0.0.1:21337/game-result   ## GameID = nb of games of the session
# {"GameID":4,"LocalPlayerWon":true}