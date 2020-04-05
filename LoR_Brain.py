import json
import random

class Brain:
    cards_dict = {}

    def __init__(self):
        self.load_db()

    def load_db(self):
        with open('set1-en_us.json', encoding="utf8") as json_file:
            for p in json.load(json_file):
                self.cards_dict[p["cardCode"]] = p
    
    def complete(self, cards):
        for card in cards:
            card.update(self.cards_dict[card["CardCode"]])

    def mulligan(self, cards):
        to_mulligan = []
        self.complete(cards)
        # print(" - ".join(c["name"] for c in cards))
        for card in cards:
            if card["cost"] > 3:
                to_mulligan.append(card)
        # print(" - ".join(c["name"] for c in to_mulligan))
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
        # print(res)   
        w = W 
        invokables = []
        for i in range(n, 0, -1): 
            if res <= 0: 
                break
            if res == K[i - 1][w]: 
                continue
            else: 
                # print(i, wt[i - 1])
                invokables.append(hand[i-1])
                res = res - val[i - 1] 
                w = w - wt[i - 1] 
        return invokables

    def choose_card_to_cast(self, cards, status):
        print(cards.board)
        if len(cards.board) >= 6: ## TODO replace by cast only spells
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
            val.append(value)

        max_cards_cast = int(min( 6 - len(cards.board), len(cards.hand) ))
        invokables = self.knapSack(status.mana, wt, val, max_cards_cast, cards.hand)
        print("---Brain decision---")
        print("-".join(c["name"] for c in invokables))
        if len(invokables) == 0:
            return None
        return invokables[0]

    def choose_blockers(self, cards, status):
        blk_atk = []
        self.complete(cards.opp_pit)
        attackers = cards.opp_pit
        self.complete(cards.board)
        # random.shuffle(attackers)
        # random.shuffle(cards.board)
        for blocker in cards.board:
            for attacker in cards.opp_pit:
                if attacker["health"] <= blocker["attack"]:
                    blk_atk.append((blocker, attacker))
                    attackers.remove(attacker)
                    break
        return blk_atk

    def choose_attackers(self, cards, status):
        attackers = []
        self.complete(cards.board)
        for card in cards.board:
            attackers.append(card)
        return attackers
