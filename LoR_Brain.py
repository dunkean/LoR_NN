import json
import random
import logging
import itertools

from ortools.algorithms import pywrapknapsack_solver

from dataclasses import dataclass, field
from typing import List, Tuple, Type

from LoR_Datamodels import Card, State, ActionType, CardType, Database


@dataclass
class Action:
    type: ActionType
    cards: List[Card] = field(default_factory=list)
    targets: List[Card] = field(default_factory=list)

class Brain:
    # cards_dict = {}
    solver = None

    def __init__(self):
        self.solver = pywrapknapsack_solver.KnapsackSolver(
            pywrapknapsack_solver.KnapsackSolver
                .KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'Cast solver')
        # self.load_db()

    # def load_db(self):
    #     with open('set1-en_us.json', encoding="utf8") as json_file:
    #         for p in json.load(json_file):
    #             self.cards_dict[p["cardCode"]] = p
    
    # def complete(self, cards):
    #     logging.info("Adding db info to cards")
    #     for card in cards:
    #         card.update(self.cards_dict[card["CardCode"]])

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


    def get_next_actions(state):     
        if state.stage == Stage.Block:
            blkrs, atkrs = choose_attackers(state)
            return Action(ActionType.Block, blkrs, atkrs)
        
        elif state.stage == Stage.Counter:
            return Action(ActionType.Pass) ##No counter spell for the moment

        elif state.stage == Stage.Play:
            ### @TODO add choice to attack b4 cast 
            cards = knapsack_cast(state)

            if len(cards) == 0:
                if state.player.token == TokenType.Attack:
                    atkrs, blkrs = choose_attackers(state)
                    return Action(ActionType.Attack, atkrs, blkrs)
                else:
                    return Action(ActionType.Pass)
            else:
                targets = choose_targets(state, cards[0])
                return Action(ActionType.Cast, cards[0], targets)
        else:
            return Action(ActionType.Pass)


    
    def knapsack_cast(self, state):
        cards = state.player.army.hand
        values = []
        weights = []
        weights.append([])
        weights.append([])
        for card in cards:
            values.append(self.estimate_card(card))
            weights[0].append(card.cost if card.type == CardType.Unit else card.cost - state.player.smana)
            weights[1].append(1 if card.type == CardType.Unit else 0)

        capacities = [ state.player.mana, 6 - len(state.player.army.deployed) ] ## mana, board space, smana
        self.solver.Init(values, weights, capacities)

        solver.Solve()
        for i in range(len(values)):
            if solver.BestSolutionContains(i):
                print(cards.to_str())


      

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
        nb_spells = 0
        for card in cards.hand:
            cost = card["cost"]
            if card["type"] == "Spell":
                cost = max(0, cost - status.smana)
                nb_spells += 1
            

            value = card["cost"]
            if card["rarity"] == "Common": value = value * 8
            elif card["rarity"] == "Rare": value = value * 9
            elif card["rarity"] == "Epic": value = value * 12
            elif card["rarity"] == "Champion": value = value * 14

            if card["type"] == "Unit": value = value * 5
            else: value = value * 2

            if len(cards.board) < 6 or card["type"] == "Spell":
                wt.append(cost)
                val.append(value)

        max_cards_cast = int(max(nb_spells, min( 6 - len(cards.board), len(cards.hand) )))
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



    def score_state(self, state):
        return -1

    def choose_next_action(self, state, btn):
        if btn == "skip block":
            attackers = state.opp_pit
            permutations = LoR_algo.generate_blk_permutations(state)
            best_score = float('-inf')
            for blockers in permutations:
                new_state = LoR_simulator.solve_fight(state)


            #evaluate best block
            




    # def choose_card_to_cast(self, cards, status):
    #     logging.info("Brain is computing cast")
    #     #print(cards.board)
    #     if len(cards.board) >= 6: ## TODO replace by cast only spells
    #         logging.info("Board is full")
    #         return None
    #     if status.mana < 0: ## TODO replace by cast only spells
    #         logging.error("Mana not recognized, cannot cast (-99)")
    #         return None
    #     if status.mana == 0: ## TODO replace by cast only spells
    #         logging.info("No mana to cast")
    #         return None

    #     self.complete(cards.hand)
    #     wt = []
    #     val = []
    #     nb_spells = 0
    #     for card in cards.hand:
    #         cost = card["cost"]
    #         if card["type"] == "Spell":
    #             cost = max(0, cost - status.smana)
    #             nb_spells += 1
            

    #         value = card["cost"]
    #         if card["rarity"] == "Common": value = value * 8
    #         elif card["rarity"] == "Rare": value = value * 9
    #         elif card["rarity"] == "Epic": value = value * 12
    #         elif card["rarity"] == "Champion": value = value * 14

    #         if card["type"] == "Unit": value = value * 5
    #         else: value = value * 2

    #         if len(cards.board) < 6 or card["type"] == "Spell":
    #             wt.append(cost)
    #             val.append(value)

    #     max_cards_cast = int(max(nb_spells, min( 6 - len(cards.board), len(cards.hand) )))
    #     invokables = []
    #     try:
    #         invokables = self.knapSack  (status.mana, wt, val, max_cards_cast, cards.hand)
    #         pass
    #     except:
    #         logging.error("Crash of knapsack", status.mana, wt, val, max_cards_cast, cards.hand)
    #         print("Crash of knapsack", status.mana, wt, val, max_cards_cast, cards.hand)
    #         pass

    #     if len(invokables) == 0:
    #         logging.info("--No invokables chosen---")
    #         return None
    #     else:
    #         logging.info("---Brain cast decision---")
    #         logging.info("-".join(c["name"] for c in invokables))

    #     return invokables[0]

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

            if beaten == False or (len(cards.board) > 3 and attacker["rarity"] != "Rare"):
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

    # def simulate_fight(self, duels): ## duel should be sorted by TopLeftX
    #     ### discard unrealistic situation #Elusive / Fearsome / Can't Block
    #     for duel in duels:
    #         if duel[1] == None:
    #             continue
    #         if self.has(duel[0], "Elusive") and not self.has(duel[1], "Elusive"):
    #             return False
    #         if self.has(duel[1], "Can't Block"):
    #             return False
    #         if self.has(duel[0], "Fearsome") and self.atk(duel[1]) < 3:
    #             return False

    #     # apply_global_effects()
    #     # apply_local_effects()
    #     for duel in duels:
    #         hp, opp_hp, atkr, blkr = self.simulate_duel(duel)
    #     pass

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




# db = Database()
# deck = db.get_deck('CEBQCAQDAQBQCBBHGQ3AMAIDBQHRIHRFFABQCAQDAMBACAYCF4BACBABCEAA')
# # for card in deck:
# #     print(card.name)
# solver = pywrapknapsack_solver.KnapsackSolver(
#             pywrapknapsack_solver.KnapsackSolver
#                 .KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'Cast solver')
# smana = 0
# mana = 3
# deployed = 3

# cards = random.choices(deck, k=7)
# values = []
# weights = []
# weights.append([])
# weights.append([])
# for card in cards:
#     values.append(card.base_health + card.base_attack if card.type == CardType.Unit else 1)
#     weights[0].append(card.base_cost if card.type == CardType.Unit else card.base_cost - smana)
#     weights[1].append(1 if card.type == CardType.Unit else 0)

# print("-".join([c.name for c in cards]))
# print(values)
# print(weights)

# capacities = [ mana, 6 - deployed ] ## mana, board space, smana
# solver.Init(values, weights, capacities)

# solver.Solve()
# for i in range(len(values)):
#     if solver.BestSolutionContains(i):
#         print(cards[i].name + "(" + str(cards[i].base_cost) + ")")
       
