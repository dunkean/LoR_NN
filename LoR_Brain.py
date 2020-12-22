import json
import random
import logging
import itertools
import copy

from ortools.algorithms import pywrapknapsack_solver

from dataclasses import dataclass, field
from typing import List, Tuple, Type

from LoR_Datamodels import Card, State, ActionType, CardType, Database, Stage, CardRarity, TokenType, Skill, CardState
import LoR_Simulator as simulator

Skill_Bonus = {
    Skill.Attack: 0,
    Skill.Attune: 0.5,
    Skill.Barrier: 1,
    Skill.Burst: 0,
    Skill.CantBlock: -2,
    Skill.Capture: 0,
    Skill.Challenger: 2,
    Skill.DoubleStrike: 2.5,
    Skill.Drain: 1.2,
    Skill.Elusive: 2,
    Skill.Enlightened: 0,
    Skill.Ephemeral: -1.5,
    Skill.Fast: 0,
    Skill.Fearsome: 2,
    Skill.Fleeting: 0,
    Skill.Frostbite: 0,
    Skill.Imbue: 0,
    Skill.Immobile: 0,
    Skill.LastBreath: 0,
    Skill.Lifesteal: 2,
    Skill.Obliterate: 0,
    Skill.Overwhelm: 2,
    Skill.Play: 0,
    Skill.QuickStrike: 2,
    Skill.Recall: 0,
    Skill.Regeneration: 1.5,
    Skill.Scout: 1.5,
    Skill.Skill: 0,
    Skill.Slow: 0,
    Skill.Stun: 0,
    Skill.Tough: 1.5,
    Skill.Trap: 0,
    Skill.Vulnerable: 0,
    Skill.Weakest: 0,
    Skill.SpellOverwhelm: 0,
    Skill.Autoplay: 0,
    Skill.Deep: 0.5,
    Skill.SpellShield: 0.3,
    Skill.Fury: 1,
    Skill.Augment: 0.5
}

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
        # self.simulator = Simulator()

        # self.load_db()

    # def __del__(self):
    #     del self.solver

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
        for card in cards:
            # print(card.name, card.cost(), card.base_cost)
            if card.cost() > 3:
                to_mulligan.append(card)
        logging.info("---Brain mulligan decision---")
        logging.info("-".join(c.name for c in to_mulligan))
        return to_mulligan

    def evaluate_card(self, card):
        if card.state == CardState.Dead:
            # print("EVALUATION", card.name, card.atk(), card.hp(), 0)
            return -1
        # print("EVALUATION", card.name, card.atk(), card.hp(), card.hp() + card.atk())
        score = card.hp() + card.atk() * 1.2
        score += ( card.cost() / 2 )
        for s in card.skills:
            score += Skill_Bonus[s]

        if card.rarity == CardRarity.Champion:
            score = 10 + score * 2
        elif card.rarity == CardRarity.Epic:
            score = score * 1.2
        

        # print(card.name, score)
        return score
        # return card.rarity * card.cost() + card.hp() + card.atk()

    def ease(self, p):
        p = p/20
        if (p < 0.5):
            return 2 * p * p
        return 20 * ( (-2 * p * p) + (4 * p) - 1 )

    def evaluate_board(self, state):
        # player_score = state.player.hp * 3
        # opp_score = state.opponent.hp * 3
        player_score = (state.player.hp-30) if state.player.hp <= 0 else self.ease(state.player.hp)
        player_score = player_score * 1.9
        opp_score = (state.opponent.hp-30) if state.opponent.hp <= 0 else self.ease(state.opponent.hp)
        opp_score = opp_score * 1.9

        for c in state.player.army.deployed:
            if c != None: player_score += self.evaluate_card(c)
        for c in state.player.army.pit:
            if c != None: player_score += self.evaluate_card(c)
        for c in state.opponent.army.deployed:
            if c != None: opp_score += self.evaluate_card(c)
        for c in state.opponent.army.pit:
            if c != None: opp_score += self.evaluate_card(c)

        # print(player_score, " vs ", opp_score)
        return player_score - opp_score

    def knapsack_cast(self, state):
        cards = state.player.army.hand
        values = []
        weights = []
        weights.append([])
        weights.append([])
        for card in cards:
            values.append(self.evaluate_card(card))
            weights[0].append(card.cost() if card.type == CardType.Unit else card.cost() - state.player.smana)
            weights[1].append(1 if card.type == CardType.Unit else 0)

        # print(cards, values, weights)
        capacities = [ max(0,state.player.mana), 6 - len(state.player.army.deployed) ] ## mana, board space, smana
        # print(state.player.mana)
        self.solver.Init(values, weights, capacities)
        # print("Initialized")
        self.solver.Solve()
        best_value = 0
        best_card = None
        for i in range(len(values)):
            if self.solver.BestSolutionContains(i):
                if values[i] > best_value:
                    best_value = values[i]
                    best_card = cards[i]
                # print(cards.to_str())
                # return cards[i] ## return random chosen card
        #return card to cast (based on eval or random or full evaluation of effect)
        return best_card
        

    def blk_permutations(self, state):
        atkrs = [atkr for atkr in state.opponent.army.pit if atkr.opp == None]
        nb_atkrs = len(atkrs)
        blkrs = [blkr for blkr in state.player.army.deployed if not blkr.has(Skill.CantBlock)]
        blkrs.extend([None for i in range(nb_atkrs)])
        # print("Attackers:", atkrs)
        # print("Blockers:", blkrs)
        perm = list(itertools.permutations(blkrs, nb_atkrs))
        perm = list(dict.fromkeys(perm))
        return perm, atkrs


    def atk_permutations(self, state):
        attackers_configs = []
        deployed = state.player.army.deployed
        for i in range(len(deployed) + 1):
            comb = list(itertools.combinations(deployed,i))
            attackers_configs.append(comb)
            # print("--- ATTACKERS COMBINATIONS --- of size >", i, "generated", len(comb))    
        
        blockers_configs = []
        blockers = state.opponent.army.deployed
        nb_missing_blockers = len(deployed) - len(blockers)
        blockers.extend([None for i in range(nb_missing_blockers)])
        # print(blockers)
        # print(deployed)
        for i in range(len(deployed) + 1):
            perm = list(itertools.permutations(blockers,i))
            perm = list(dict.fromkeys(perm))
            blockers_configs.append(perm)
            # print("--- BLOCKERS PERMUTATIONS --- of size >", i, "generated", len(perm))

        atkrs_combi = []
        blkrs_combi = []
        for i in range(len(deployed) + 1):
            for atkrs in attackers_configs[i]:
                atkrs_combi.append(atkrs)
                tmp = []
                for blkrs in blockers_configs[i]:
                    tmp.append(blkrs)
                blkrs_combi.append(tmp)
                    # combinations.append((atkrs, blkrs))
        
        # print("Total of possible fights", len(combinations))
        return atkrs_combi, blkrs_combi



    def choose_attackers(self, state):
        sim_state = copy.deepcopy(state)

        atkrs_list, blkrs_perm = self.atk_permutations(sim_state)
        scores = []
        best_block_index = []
        initial_score = self.evaluate_board(state)
        # print("----------------- COMPUTING ATTACK ------------------")
        # print("Initial score:", initial_score)
        # print("Player:", state.player.army.to_str())
        # print("Opponent:", state.opponent.army.to_str())
        for i in range(len(atkrs_list)) :
            blkrs_list = blkrs_perm[i]
            atkrs = atkrs_list[i]
            # print("*** Attackers > ", atkrs)
            local_scores = []
            for blkrs in blkrs_list:
                blkrs = list(blkrs)
                for i in range(len(atkrs)):
                    if blkrs[i] != None:
                        if atkrs[i].has(Skill.Elusive) and blkrs[i] != None and not blkrs[i].has(Skill.Elusive):
                            blkrs[i] = None
                        elif atkrs[i].has(Skill.Fearsome) and blkrs[i] != None and blkrs[i].atk() < 3:
                            blkrs[i] = None
                        else:
                            blkrs[i].opp = atkrs[i]
                    atkrs[i].opp = blkrs[i]
                
                sim_state.player.army.pit = atkrs
                sim_state.player.army.deployed = [c for c in state.player.army.deployed if not c in list(atkrs)]
                sim_state.opponent.army.pit = blkrs
                sim_state.opponent.army.deployed = [c for c in state.opponent.army.deployed if not c in list(blkrs)]
                new_state = simulator.simulate_fight(sim_state)
                new_score = self.evaluate_board(new_state)
                # print("***--> ", blkrs, " >>> ", new_score)
                local_scores.append(new_score)
            scores.append(min(local_scores))
            best_block_index.append(local_scores.index(max(local_scores)))

        best_atk_index = scores.index(max(scores))
        atkrs = list(atkrs_list[best_atk_index])
        blkrs = list(blkrs_list[best_block_index[best_atk_index]])
        # print("Attackers", atkrs)
        # print("Blockers", blkrs)
        for i in range(len(atkrs)):
            if atkrs[i].has(Skill.Challenger) or ( blkrs[i] != None and blkrs[i].has(Skill.Vulnerable)):
                atkrs[i].opp = blkrs[i]
            else:
                atkrs[i].opp = None

        # print("++++ CHOSEN ++++", atkrs, " >>> ", max(scores))
        del sim_state
        return atkrs


    def choose_blockers(self, state):
        sim_state = copy.deepcopy(state)
        blkrs_list, atkrs = self.blk_permutations(sim_state)
        scores = []
        initial_score = self.evaluate_board(state)
        # print("initial_score", initial_score)
        # print("----------------- COMPUTING BLOCK ------------------")
        # print("Initial score:", initial_score)
        # print("*** Attackers > ", atkrs)
        for j in range(len(blkrs_list)):
            blkrs = list(blkrs_list[j])
            for i in range(len(blkrs)):
                if atkrs[i].has(Skill.Elusive) and blkrs[i] != None and not blkrs[i].has(Skill.Elusive):
                   blkrs[i] = None
                elif atkrs[i].has(Skill.Fearsome) and blkrs[i] != None and blkrs[i].atk() < 3:
                    blkrs[i] = None

                if blkrs[i] != None:
                    blkrs[i].opp = atkrs[i]
                atkrs[i].opp = blkrs[i]
            blkrs_list[j] = blkrs
            sim_state.player.army.pit = state.player.army.pit + blkrs
            sim_state.player.army.deployed = [c for c in state.player.army.deployed if not c in blkrs]
            new_state = simulator.simulate_fight(sim_state)
            new_score = self.evaluate_board(new_state)
            # print("new_score", new_score)
            # print("***--> ", blkrs, " >>> ", new_score)
            scores.append(new_score)

        best_blk_index = scores.index(max(scores))

        blkrs = blkrs_list[best_blk_index]
        for i in range(len(blkrs)):
            if blkrs[i] != None: 
                blkrs[i].opp = atkrs[i]
            atkrs[i].opp = blkrs[i]
        
        # print("++++ CHOSEN ++++", blkrs, " >>> ", max(scores))
        del sim_state
        return blkrs




    def get_next_action(self, state):     
        if state.stage == Stage.Block:
            blkrs = self.choose_blockers(state)
            return Action(ActionType.Block, blkrs)
        
        elif state.stage == Stage.Counter:
            return Action(ActionType.Pass) ##No counter spell for the moment

        elif state.stage == Stage.Play:
            ### @TODO add choice to attack b4 cast 
            card = self.knapsack_cast(state)
            # print("KNAPSACK", card)
            if card == None:
                if state.player.token == TokenType.Attack and len(state.player.army.deployed) > 0:
                    atkrs = self.choose_attackers(state)
                    return Action(ActionType.Attack, atkrs)
                else:
                    return Action(ActionType.Pass)
            else:
                # targets = choose_targets(state, [card])
                targets = []
                return Action(ActionType.Cast, [card], targets)
        else:
            return Action(ActionType.Pass)


    


      

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



    # def score_state(self, state):
    #     return -1

    # def choose_next_action(self, state, btn):
    #     if btn == "skip block":
    #         attackers = state.opp_pit
    #         permutations = LoR_algo.generate_blk_permutations(state)
    #         best_score = float('-inf')
    #         for blockers in permutations:
    #             new_state = LoR_simulator.solve_fight(state)


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

    # def choose_blockers(self, cards):
    #     logging.info("Brain is computing blockers")
    #     blk_atk = []
    #     self.complete(cards.opp_pit)
    #     attackers = cards.opp_pit
    #     self.complete(cards.board)
    #     random.shuffle(attackers)
    #     random.shuffle(cards.board)
    #     for blocker in cards.board:
    #         for attacker in cards.opp_pit:
    #             if self.hp(attacker) <= self.atk(blocker) and (len(cards.board) > 2 or status.hp <= 10 or self.hp(blocker) > self.atk(attacker)):
    #             # if attacker["health"] <= blocker["attack"] and (len(cards.board) > 2 or status.hp <= 10 or blocker["health"] > attacker["attack"]):
    #                 blk_atk.append((blocker, attacker))
    #                 attackers.remove(attacker)
    #                 break
    #     logging.info("---Brain block decision---")
    #     logging.info("-".join(c[0]["name"] + "|" + c[1]["name"] for c in blk_atk))
    #     return blk_atk

    # def choose_attackers(self, cards):
    #     logging.info("Brain is computing attackers")
    #     attackers = []
    #     self.complete(cards.opp_board)
    #     self.complete(cards.board)
    #     random.shuffle(cards.opp_board)
    #     random.shuffle(cards.board)
    #     for attacker in cards.board:
    #         beaten = False
    #         for blocker in cards.opp_board:
    #             if self.hp(attacker) <= self.atk(blocker) and self.atk(attacker) < self.hp(blocker):
    #                 beaten = True

    #         if beaten == False or (len(cards.board) > 3 and attacker["rarity"] != "Rare"):
    #             attackers.append(attacker)
    #     logging.info("---Brain attack decision---")
    #     logging.info("-".join(c["name"] for c in attackers))
        
    #     return attackers

    # def hp(self, card):
    #     if "real_hp" in card and card["real_hp"] != -99:
    #         return card["real_hp"]
    #     elif "health" in card:
    #         return card["health"]
    #     else:
    #         return -1
    
    # def atk(self, card):
    #     if "real_atk" in card and card["real_atk"] != -99:
    #         return card["real_atk"]
    #     elif "attack" in card:
    #         return card["attack"]
    #     else:
    #         return -1

    # def cost(self, card):
    #     if "real_cost" in card:
    #         return card["real_cost"]
    #     elif "cost" in card:
    #         return card["cost"]
    #     else:
    #         return -1



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

    # def generate_blk_permutations(self, atkrs, board):
    #     board.extend(["N" for i in range(len(atkrs)+1)])
    #     perm = list(itertools.permutations(board, len(atkrs)))
    #     perm = list(dict.fromkeys(perm))
    #     return perm

    # def generate_atk_permutations(self, board, blkrs):
    #     attackers_configs = []
    #     for i in range(len(board) + 1):
    #         comb = list(itertools.combinations(board,i))
    #         attackers_configs.append(comb)
    #         print("--- ATTACKERS COMBINATIONS --- of size >", i, "generated", len(comb))    
        
    #     blockers_configs = []
    #     blkrs.extend(["N" for i in range(len(board) + 1)])
    #     for i in range(len(board) + 1):
    #         perm = list(itertools.permutations(blkrs,i))
    #         perm = list(dict.fromkeys(perm))
    #         blockers_configs.append(perm)
    #         print("--- BLOCKERS PERMUTATIONS --- of size >", i, "generated", len(perm))

    #     combinations = []
    #     for i in range(len(board) + 1):
    #         for atkrs in attackers_configs[i]:
    #             for blkrs in blockers_configs[i]:
    #                 combinations.append((atkrs, blkrs))
        
    #     print("Total of possible fights", len(combinations))
    #     return combinations




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
       
