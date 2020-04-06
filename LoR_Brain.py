import json
import random
import logging

class Brain:
    cards_dict = {}

    def __init__(self):
        self.load_db()

    def load_db(self):
        with open('set1-en_us.json', encoding="utf8") as json_file:
            for p in json.load(json_file):
                self.cards_dict[p["cardCode"]] = p
    
    def complete(self, cards):
        logging.info("Adding db info to cards")
        for card in cards:
            card.update(self.cards_dict[card["CardCode"]])

    def mulligan(self, cards):
        logging.info("Computing mulligan")
        to_mulligan = []
        self.complete(cards)
        for card in cards:
            if card["cost"] > 3:
                to_mulligan.append(card)
        logging.info("---Brain mulligan decision---")
        logging.info("-".join(c["name"] for c in to_mulligan))
        return to_mulligan



    def knapSack(self, W, wt, val, n, hand): 
        K = [[0 for w in range(W + 1)]  for i in range(n + 1)]

        for i in range(n + 1): 
            for w in range(W + 1): 
                if i == 0 or w == 0: 
                    K[i][w] = 0
                elif wt[i - 1] <= w: 
                    K[i][w] = max(val[i - 1]  
                    + K[i - 1][w - wt[i - 1]], 
                                K[i - 1][w]) 
                else: 
                    K[i][w] = K[i - 1][w] 
    
        # stores the result of Knapsack 
        res = K[n][W] 
        # #print(res)   
        w = W 
        invokables = []
        for i in range(n, 0, -1): 
            if res <= 0: 
                break
            if res == K[i - 1][w]: 
                continue
            else: 
                # #print(i, wt[i - 1])
                invokables.append(hand[i-1])
                res = res - val[i - 1] 
                w = w - wt[i - 1] 
        return invokables

    def choose_card_to_cast(self, cards, status):
        logging.info("Brain is computing cast")
        #print(cards.board)
        if len(cards.board) >= 6: ## TODO replace by cast only spells
            logging.info("Board is full")
            return None

        self.complete(cards.hand)
        wt = []
        val = []
        for card in cards.hand:
            wt.append(card["cost"])
            value = card["cost"]
            if card["rarity"] == "Common": value = value * 8
            elif card["rarity"] == "Rare": value = value * 9
            elif card["rarity"] == "Epic": value = value * 10
            elif card["rarity"] == "Champion": value = value * 13

            if card["type"] == "Unit": value = value * 5
            else: value = value * 4
            val.append(value)

        max_cards_cast = int(min( 6 - len(cards.board), len(cards.hand) ))
        invokables = self.knapSack(status.mana, wt, val, max_cards_cast, cards.hand)
        logging.info("---Brain cast decision---")
        logging.info("-".join(c["name"] for c in invokables))
        if len(invokables) == 0:
            return None
        return invokables[0]

    def choose_blockers(self, cards, status):
        logging.info("Brain is computing blockers")
        blk_atk = []
        self.complete(cards.opp_pit)
        attackers = cards.opp_pit
        self.complete(cards.board)
        random.shuffle(attackers)
        random.shuffle(cards.board)
        for blocker in cards.board:
            for attacker in cards.opp_pit:
                if attacker["health"] <= blocker["attack"] and (len(cards.board) > 2 or status.hp <= 10 or blocker["health"] > attacker["attack"]):
                    blk_atk.append((blocker, attacker))
                    attackers.remove(attacker)
                    break
        logging.info("---Brain block decision---")
        logging.info("-".join(c[0]["name"] + "|" + c[1]["name"] for c in blk_atk))
        return blk_atk

    def choose_attackers(self, cards, status):
        logging.info("Brain is computing attackers")
        attackers = []
        self.complete(cards.opp_board)
        self.complete(cards.board)
        random.shuffle(cards.opp_board)
        random.shuffle(cards.board)
        for attacker in cards.board:
            beaten = False
            for blocker in cards.opp_board:
                if attacker["health"] <= blocker["attack"] and attacker["attack"] < blocker["health"]:
                    beaten = True

            if beaten == False:
                attackers.append(attacker)
        logging.info("---Brain attack decision---")
        logging.info("-".join(c["name"] for c in attackers))
        
        return attackers
