
import time
# import utils as Utils
# import copy
import LoR_Handler, LoR_Brain, LoR_Queries

# def print_state(state):
#     # if len(state["mulligan"]) > 0:
#     #     print("MULLIGAN >", " - ".join(c["name"] for c in state["mulligan"]))
#     #     # return

#     lines = ["hand", "board", "pit","opp_hand","opp_board","opp_pit"]
#     print("*********", state["stage"], "*********", state["btn"])
#     print("HP:", state["hp"],"Mana:", state["mana"], "SpellMana:", state["smana"], "@@" if state["atk_token"] == True else "", 
#     " -- vs -- ","HP:", state["opp_hp"],"Mana:", state["opp_mana"], "SpellMana:", state["opp_smana"], "@@" if state["opp_atk_token"] == True else "")
#     for line in lines:
#         if len(state[line]) > 0: 
#             print(line, ">>>", " - ".join((c["name"] + " " + ( c["atk"] if "atk" in c else str(c["attack"])) + "|" + ( c["hp"] if "hp" in c else str(c["health"]) ) ) for c in state[line]))
#     cast = sorted(state["cast"], key=lambda x: x["TopLeftX"])
    
#     if len(state["cast"]) > 0: 
#         print(" >> ".join(("<ME>" if x["LocalPlayer"] == True else "<OPP>") + x["name"] for x in cast))


# def in_game_automata(LoR):
#     state = LoR.get_state()
#     if state == None:
#         time.sleep(0.5)
#         return
#     print_state(state)
#     stage = state["stage"]
#     if stage == "MULLIGAN":
#         # print("CHOOSE CARDS TO CHANGE")
#         ### replace spells
#         LoR.next()
#     elif stage == "END_ROUND": #no more mana, or passed before, most probably attack token "END ROUND"
#         # print("END ROUND OR ATTACK")
#         invokable = get_invocations(state)
#         if invokable != None:
#             LoR.cast(invokable)
#         elif state["atk_token"] == True:
#             for card in state["board"]:
#                 LoR.attack(card)
#             LoR.next()
#         else:
#             LoR.next()
#     elif stage == "VALIDATE_ATTACK": #creatures are in the pit ready to attack //"ATTACK"
#         # print("CAN VALIDATE OR ADD NEW CREATURES")
#         LoR.next()
#     elif stage == "PLAY":
#         # print("I HAVE TO PLAY") #you have mana, you can act //"PASS"
#         invokable = get_invocations(state)
#         if invokable != None:
#             LoR.cast(invokable)
#         elif state["atk_token"] == True:
#             for card in state["board"]:
#                 LoR.attack(card)
#             LoR.next()
#         else:
#             LoR.next()
#     elif stage == "CHOOSE_BLOCKERS":  #opp is attacking //"SKIP BLOCK"
#         # print("I HAVE TO BLOCK")
#         blk_atk = get_block(state)
#         for t in blk_atk:
#             LoR.block(t[0],t[1])
#         LoR.next()
#     elif stage == "VALIDATE_BLOCK":  #opp is attacking put monsters & validate or skip //"SKIP BLOCK"
#         # print("READY TO TAKE ATTACK")
#         LoR.next()
#     # elif stage == "SELECT": #a block or a spell is ready to cast choose target //"SELECT TARGET"
#         # print("I HAVE TO SELECT A TARGET") 
#         # LoR.next()
#     elif stage == "VALIDATE_LAST_OPP_ACTION": #an opp action can be interrupted//"OK" or "PLAY"
#         # print("I HAVE TO SELECT A COUNTER ACTION")
#         LoR.next()
#     elif stage == "VALIDATE_CAST": #you have cast a spell//"OK" or "PLAY"
#         # print("CAST IS READY, VALIDATE")
#         LoR.next()
#     elif stage == "VALIDATE_OPP_CAST": #an opp spell can be interrupted//"OK" or "PLAY"
#         # print("I HAVE TO SELECT A COUNTER SPELL") 
#         LoR.next()
#     elif stage == "OPPONENT": #either you or your opponent is playin / casting //"Opponent's Turn"
#         time.sleep(0.1)
#     else:
#         time.sleep(0.1)
#     time.sleep(0.5)

brain = LoR_Brain.Brain()

def play(LoR, last_game_id):
    print("game in progress...", end="\r")
    game_id, won = LoR_Queries.get_last_game()
    while game_id == last_game_id:
        btn = LoR.ocr_btn_txt()
        cards = LoR.get_board_cards()

        print("***", btn, "***")
        if "round" in btn or "pass" in btn: #"END_ROUND" #PASS
            print("Need to play")
            status = LoR.get_status()
            card = brain.choose_card_to_cast(cards, status)
            if card == None:
                LoR.click_next()
            else:
                LoR.cast(card)
                
        elif "skip" in btn: # SKIP BLOCK
            print("Need to block")
            status = LoR.get_status()
            blockers = brain.choose_blockers(cards, status)
            LoR.block(blockers)
            LoR.click_next()

        elif "select" in btn:
            print("Need to select target")

        elif "attack" in btn or "block" in btn: ## should not happens coz its a validation #BLOCK #ATTACK
            print("Need to validate block or attack")
            LoR.click_next()

        elif "ok" in btn and len(cards.cast) > 0 and cards.cast[0]["LocalPlayer"] == True: ## own cast validation Should not happen
            print("Need to validate cast")
            LoR.click_next()

        elif "ok" in btn and (len(cards.cast) == 0 or cards.cast[0]["LocalPlayer"] == True):
            print("Need to validate invocation")
            LoR.click_next()

        elif "turn" in btn or "onent" in btn:
            print("Opponent is playing")

        elif "summon" in btn:
            print("Summoning in progress")
            
        else:
            print("Don't know what to do")
        
        time.sleep(3)
        #check if game finished
        game_id, won = LoR_Queries.get_last_game()
    return game_id, won



def mulligan(LoR):
    cards = LoR_Queries.get_my_cards()
    to_mulligan = brain.mulligan(cards)
    LoR.click_mulligan(to_mulligan)
    LoR.click_next()

def launch_match(LoR, mode):
    print("Launching match vs", mode)
    if mode == "bot":
        LoR.wait_for_image(["Play", "vsAI"])
    elif mode == "challenger":
        LoR.wait_for_image(["Friends", "Spare", "Challenge"])
    elif mode == "challenged":
        LoR.wait_for_image(["Accept"])


def loop(mode = "bot"):
    LoR = LoR_Handler.launch()
    print("Game hooked.")
    # print("Choosing next opponent >", mode)
    
    game_already_started = False
    if LoR_Queries.is_game_in_progress == False:
        launch_match(LoR, mode)
        LoR.wait_for_selection_menu()
        LoR.wait_for_image(["Versus", "Ready"])
    else:
        game_already_started = True
    
    # GAME SESSION
    game_session = True
    last_game_id, _ = LoR_Queries.get_last_game()
    game_count = 1
    LoR.update_geometry() ## TODO REMOVE
    while game_session == True:
        if game_already_started == False:
            LoR.wait_for_game_to_start() ## DEBUG
            mulligan(LoR)
        game_id, won = play(LoR, last_game_id)

        # # clean and restart
        LoR.game_ended()
        last_game_id = game_id
        print("Game ", game_count, "finished >", "Victory" if won == True else "Defeat")
        game_count = game_count + 1
        time.sleep(4)
        LoR.wait_for_image(["Continue", "Ready"])


loop()

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