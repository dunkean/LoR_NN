from LoR_Datamodels import Card, CardDesc, State, ActionType, CardType, Database, Stage, CardRarity, TokenType, Skill, CardState, Player
import copy
from dataclasses import dataclass, field
from typing import List, Tuple, Type

from lor_deckcodes import LoRDeck, CardCodeAndCount
import random
from LoR_Brain import Brain

@dataclass
class Game:
    state: State
    round: int = 0
    player1: Brain = None
    player2: Brain = None
    players: List[Type['Player']] = field(default_factory=list)
    brains: List[Type['Brain']] = field(default_factory=list)
   

    def __init__(self, code1, code2):
        self.player1 = Brain()
        self.player2 = Brain()
        self.state = State()

        self.state.player.deck = self.generate_deck(code1)
        random.shuffle(self.state.player.deck)
        self.state.opponent.deck =self.generate_deck(code2)
        random.shuffle(self.state.opponent.deck)
        
        self.players = [self.state.player, self.state.opponent]
        self.brains = [self.player1, self.player2]
        
        self.start()
        
    def generate_deck(self, code):
        deck_list = LoRDeck.from_deckcode(code)
        deck = []
        for cnc in deck_list.cards:
            for i in range(cnc.count):
                cd = CardDesc()
                cd.from_json(cnc.card_code)
                deck.append(cd)
        return deck
    
    def start(self):
        ## Mulligan
        for player in self.players:
            draw = [player.deck.pop() for _ in range(4)]
            for c in draw:
                print(c.name)
            print("*******")


    def play_card(self, card, targets):
        # update state
        # return choice if needed
        pass
    
    def choose_card(self, card):
        pass

    def execute_board(self):
        pass


game = Game('CECQCAYGCEAQEBADAIAQIAJUAMBAMGRLFYBQGBAFBUMQGAICAYTACAYECIBACBBHFUBACAQGFIAQGBAE','CECQCBAAAIAQEAABAIAQEIBLAIBQABQOAMAQACI2FUBAEAIAEUZQGAICCMSTCAQBAMBBIAQBAA2DK')

# def execute_state(state):


#### COMBAT TRIGGERS
# WHEN - attack, strike, support, strike_nexus





############ TESTING (olv version) ###################

# def random_unit(lvl = 9, nb_skills = 2):
#     skills = random.choices(short_sk, k=random.randint(0,nb_skills))
#     atk = random.randint(1,lvl)
#     hp = random.randint(1,lvl)
#     return Unit(atk, hp, skills, uuid.uuid1())


# ## test fight
# atkrs = []
# blkrs = []
# for i in range(5):
#     atkrs.append(random_unit(6,0))

# for j in range(3):
#     blkrs.append(random_unit(4,0))
        
# print(round(evaluate_board(atkrs, True),2), "****** VS ********", round(evaluate_board(blkrs, True),2))
# # get_best_block(atkrs, blkrs)
# get_best_attack(atkrs, blkrs)



# # import json
# # json_file = open('set1-en_us.json', encoding="utf8")
# # dict = {}
# # for p in json.load(json_file):
# #     if p["type"] == "Spell":
# #         dict[p["descriptionRaw"]] = None

# # print(list(dict))

# # file = open("log_simu.txt","w") 
# # file.write("\n".join(c for c in list(dict)))
# # file.close()