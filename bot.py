
import time
# import utils as Utils
# import copy
import LoR_Handler

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

# def knapSack(W, wt, val, n, hand): 
#     K = [[0 for w in range(W + 1)] 
#             for i in range(n + 1)] 

#     for i in range(n + 1): 
#         for w in range(W + 1): 
#             if i == 0 or w == 0: 
#                 K[i][w] = 0
#             elif wt[i - 1] <= w: 
#                 K[i][w] = max(val[i - 1]  
#                   + K[i - 1][w - wt[i - 1]], 
#                                K[i - 1][w]) 
#             else: 
#                 K[i][w] = K[i - 1][w] 
  
#     # stores the result of Knapsack 
#     res = K[n][W] 
#     # print(res)   
#     w = W 
#     invokables = []
#     for i in range(n, 0, -1): 
#         if res <= 0: 
#             break
#         if res == K[i - 1][w]: 
#             continue
#         else: 
#             # print(i, wt[i - 1])
#             invokables.append(hand[i-1])
#             res = res - val[i - 1] 
#             w = w - wt[i - 1] 
#     return invokables

# def get_invocations(state):
#     if len(state["board"]) >= 6:
#         return None
#     mana = int(state["mana"])
#     wt = []
#     val = []
#     for card in state["hand"]:
#         wt.append(card["cost"])
#         value = card["cost"]
#         if card["rarity"] == "Common": value = value * 8
#         elif card["rarity"] == "Rare": value = value * 9
#         elif card["rarity"] == "Epic": value = value * 10
#         elif card["rarity"] == "Champion": value = value * 13
#         val.append(value)
#     # print(wt, val)
#     invokables = knapSack(mana, wt, val, len(state["hand"]), state["hand"])
#     # print( "INVOCATION > ", mana, ":", " - ".join(c["name"] for c in invokables))

#     if len(invokables) == 0:
#         return None
#     return invokables[0]

# def get_block(state):
#     blk_atk = []
#     attackers = state["opp_pit"]
#     for blocker in state["board"]:
#         for attacker in attackers:
#             if attacker["health"] <= blocker["attack"]:
#                 blk_atk.append((blocker, attacker))
#                 attackers.remove(attacker)
#                 break
#     return blk_atk

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

# def mulligan(LoR):
#     Utils.wait_for_btn("ok")
#     ## choose card to mulligan
#     #cards = Brain.mulligan(state)
#     #Utils.click_change(cards)
#     LoR.next()

# def play(LoR, last_game_id):
#     print("game in progress...", end="\r")
#     game_id, won = LoR.get_last_game()
#     while game_id == last_game_id: #game not finished
#         state = LoR.get_state()
    
#         #check if game finished
#         game_id, won = LoR.get_last_game()
#     return game_id, won


def launch_match(LoR, mode):
    print("Launching match vs", mode)
    # try:
    if mode == "bot":
        LoR.wait_and_click(["Play", "vsAI"], 5, 8)
    elif mode == "challenger":
        LoR.wait_and_click(["Friends", "Spare", "Challenge"], 2, 2)
    elif mode == "challenged":
        LoR.wait_and_click(["Accept"], 2, 2)
    pass
    # except:
        # print("launch failed")
        # return False
    return True

def rematch(LoR, mode):
    LoR.exit()
    loop(mode)

def loop(mode = "bot"):
    LoR = LoR_Handler.launch()
    print("Game hooked. Choosing next opponent >", mode)

    if launch_match(LoR, mode) == False:
        print("killing and restart")
        # rematch(LoR, mode)
        return

    LoR.wait_for_selection_menu()

    LoR.wait_and_click(["Versus", "Ready"])
    
    ## GAME SESSION
    # game_session = True
    # last_game_id, _ = LoR.get_last_game()
    # game_count = 1
    # while game_session == True:
    #     mulligan(LoR)
    #     game_id, won = play(LoR, last_game_id)
    #     # clean and restart
    #     last_game_id = game_id
    #     print("Game ", game_count, "finished >", "Victory" if won == True else "Defeat")
    #     game_count = game_count + 1
    #     LoR.clean()
    #     time.sleep(4)
    #     LoR.wait_and_click(["Continue", "Ready"])


loop()


# loop(bot = True)
# LoR = Utils.LoR()
# print("LoR connected")
# state = LoR.get_state()
# print_state(state)
# time.sleep(2)
# state = LoR.get_state()
# print_state(state)
# in_game_automata(LoR)

# launch()
# LoR = Utils.LoR()
# LoR.capture(None, "vsAI")
# LoR.capture((0,0,750,750))
# LoR.capture((0,0,250,250), "capture")


## OUT OF GAME
# http://127.0.0.1:21337/positional-rectangles ## screen + board state  
# {"PlayerName":null,"OpponentName":null,"GameState":"Menus","Screen":{"ScreenWidth":1920,"ScreenHeight":1080},"Rectangles":[]}

### IN GAME
# http://127.0.0.1:21337/static-decklist ## activated decklist
# {"DeckCode":"CEAQUAIAAEDAYFA5EISCOLJPAECACAADCUNDMAICAEAAONA","CardsInDeck":{"01DE001":3,"01DE006":3,"01DE012":3,"01DE020":3,"01DE029":3,"01DE034":3,"01DE036":3,"01DE039":3,"01DE045":3,"01DE047":3,"01DE003":2,"01DE021":2,"01DE026":2,"01DE054":2,"01DE007":1,"01DE052":1}}

# http://127.0.0.1:21337/game-result   ## GameID = nb of games of the session
# {"GameID":4,"LocalPlayerWon":true}