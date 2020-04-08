import json
import random
import logging
import itertools

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
        if status.mana < 0: ## TODO replace by cast only spells
            logging.error("Mana not recognized, cannot cast (-99)")
            return None
        if status.mana == 0: ## TODO replace by cast only spells
            logging.info("No mana to cast")
            return None

        self.complete(cards.hand)
        wt = []
        val = []
        for card in cards.hand:
            cost = card["cost"]
            if card["type"] == "Spell":
                cost = max(0, cost - status.smana)
            wt.append(cost)

            value = card["cost"]
            if card["rarity"] == "Common": value = value * 8
            elif card["rarity"] == "Rare": value = value * 9
            elif card["rarity"] == "Epic": value = value * 11
            elif card["rarity"] == "Champion": value = value * 13

            if card["type"] == "Unit": value = value * 5
            else: value = value * 3
            val.append(value)

        max_cards_cast = int(min( 6 - len(cards.board), len(cards.hand) ))
        invokables = []
        try:
            invokables = self.knapSack  (status.mana, wt, val, max_cards_cast, cards.hand)
            pass
        except:
            logging.error("Crash of knapsack", status.mana, wt, val, max_cards_cast, cards.hand)
            print("Crash of knapsack", status.mana, wt, val, max_cards_cast, cards.hand)
            pass

        if len(invokables) == 0:
            logging.info("--No invokables chosen---")
            return None
        else:
            logging.info("---Brain cast decision---")
            logging.info("-".join(c["name"] for c in invokables))

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
                if self.hp(attacker) <= self.atk(blocker) and (len(cards.board) > 2 or status.hp <= 10 or self.hp(blocker) > self.atk(attacker)):
                # if attacker["health"] <= blocker["attack"] and (len(cards.board) > 2 or status.hp <= 10 or blocker["health"] > attacker["attack"]):
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
                if self.hp(attacker) <= self.atk(blocker) and self.atk(attacker) < self.hp(blocker):
                    beaten = True

            if beaten == False:
                attackers.append(attacker)
        logging.info("---Brain attack decision---")
        logging.info("-".join(c["name"] for c in attackers))
        
        return attackers

    def hp(self, card):
        if "real_hp" in card and card["real_hp"] != -99:
            return card["real_hp"]
        elif "health" in card:
            return card["health"]
        else:
            return -1
    
    def atk(self, card):
        if "real_atk" in card and card["real_atk"] != -99:
            return card["real_atk"]
        elif "attack" in card:
            return card["attack"]
        else:
            return -1

    def cost(self, card):
        if "real_cost" in card:
            return card["real_cost"]
        elif "cost" in card:
            return card["cost"]
        else:
            return -1

# "Challenger",

# > effects: "Drain", "Rally","Support","Capture",
# > status: "Silenced","Frostbite","Barrier","Stun"
# > conditions: "Last Breath","Enlightened","Allegiance",

    def simulate_duel(self, atkr, blkr):

        if self.has(atkr,"Double Attack"):
            hp, opp_hp, a_hp, b_hp = self.simulate_duel(atkr, blkr)
        else:
            hp = 0
            if duel[1] != None:
                blkr = (self.atk(duel[1]), self.hp(duel[1]))
            hp = 0
            opp_hp = 0

        a_atk = self.atk(atkr)
        a_hp = self.hp(atkr)
        if blkr == None:
            hp -= a_atk
            if self.has(atkr,"Lifesteal"): opp_hp += a_atk
            if self.has(atkr,"Double Attack"): hp -= a_atk
        else:
            blk = self.atk(blkr)
            bhp = self.hp(blkr)

            ## atk turn
            bhp -= atk
            if self.has(atkr,"Quick Attack") and bhp <= 0:
                pass
            else:
                ahp -= blk



            pass


# > atk props: 
# "Can't Block",
# "Fearsome",
# "Ephemeral",
# "Elusive",
# 
# "Lifesteal",
# "Tough",
# "Quick Attack",
# "Overwhelm",
# "Double Attack"
#  "Regeneration"


    def has(self, card, property):
        if property in card["keywords"]:
            return True
        return False

    def simulate_fight(self, duels): ## duel should be sorted by TopLeftX
        ### discard unrealistic situation #Elusive / Fearsome / Can't Block
        for duel in duels:
            if duel[1] == None:
                continue
            if self.has(duel[0], "Elusive") and not self.has(duel[1], "Elusive"):
                return False
            if self.has(duel[1], "Can't Block"):
                return False
            if self.has(duel[0], "Fearsome") and self.atk(duel[1]) < 3:
                return False

        # apply_global_effects()
        # apply_local_effects()
        for duel in duels:
            hp, opp_hp, atkr, blkr = self.simulate_duel(duel)
        pass

    def generate_blk_permutations(self, atkrs, board):
        board.extend(["N" for i in range(len(atkrs)+1)])
        perm = list(itertools.permutations(board, len(atkrs)))
        perm = list(dict.fromkeys(perm))
        return perm

    def generate_atk_permutations(self, board, blkrs):
        attackers_configs = []
        for i in range(len(board) + 1):
            comb = list(itertools.combinations(board,i))
            attackers_configs.append(comb)
            print("--- ATTACKERS COMBINATIONS --- of size >", i, "generated", len(comb))    
        
        blockers_configs = []
        blkrs.extend(["N" for i in range(len(board) + 1)])
        for i in range(len(board) + 1):
            perm = list(itertools.permutations(blkrs,i))
            perm = list(dict.fromkeys(perm))
            blockers_configs.append(perm)
            print("--- BLOCKERS PERMUTATIONS --- of size >", i, "generated", len(perm))

        combinations = []
        for i in range(len(board) + 1):
            for atkrs in attackers_configs[i]:
                for blkrs in blockers_configs[i]:
                    combinations.append((atkrs, blkrs))
        
        print("Total of possible fights", len(combinations))
        return combinations