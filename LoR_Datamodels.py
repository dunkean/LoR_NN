from dataclasses import dataclass, field
from typing import List, Tuple, Type
from enum import EnumMeta, IntEnum
import json


class DefaultEnumMeta(EnumMeta): ### implements default value as the first
    default = object()
    def __call__(cls, value=default, *args, **kwargs):
        if value is DefaultEnumMeta.default:
            return next(iter(cls))
        return super().__call__(value, *args, **kwargs)



################################################################################################################################
################################################              Database                 ############################################
################################################################################################################################

class Database:
    code_dict = {}
    # name_dict = {}

    def __init__(self):
        self.load_db()

    def load_db(self):
        with open('set1-en_us.json', encoding="utf8") as json_file:
            for data in json.load(json_file):
                # card = CardDesc.from_json(data)
                self.code_dict[data["cardCode"]] = data
                # self.name_dict[card.name] = data

    def card(self, code):
        if code in self.code_dict:
            return self.code_dict[code]
        else:
            return self.code_dict["UNK"]


DB = Database()

################################################################################################################################
################################################              CARDS                 ############################################
################################################################################################################################

class CardType(IntEnum, metaclass=DefaultEnumMeta):
    Unknown = 0
    Unit = 1
    Spell = 2
    Ability = 3
    Trap = 4

class CardRegion(IntEnum, metaclass=DefaultEnumMeta):
    Unknown = 0
    Demacia = 1
    Noxus = 2
    Ionia = 3
    ShadowIsles = 4
    Freljord = 5
    PiltoverZaun = 6
    BildgeWater = 7

class CardRarity(IntEnum, metaclass=DefaultEnumMeta):
    Unknown = 0
    Common = 1
    Rare = 2
    Epic = 3
    Champion = 4
    NoRarity = 5

class SpellSpeed(IntEnum, metaclass=DefaultEnumMeta):
    Unknown = 0
    Burst = 1
    Fast = 2
    Slow = 3
    NA = 4

class Skill(IntEnum, metaclass=DefaultEnumMeta):
    Unknown = 0
    Burst = 1
    QuickStrike = 2
    Overwhelm = 3
    Elusive = 4
    Fast = 5
    Skill = 6
    Imbue = 7
    Slow = 8
    Challenger = 9
    Regeneration = 10
    LastBreath = 11
    Lifesteal = 12
    Tough = 13
    Barrier = 14
    Fleeting = 15
    Fearsome = 16
    CantBlock = 17
    DoubleStrike = 18
    Ephemeral = 19
    SpellOverwhelm = 20
    Autoplay = 21

class SubType(IntEnum, metaclass=DefaultEnumMeta):
    Unknown = 0
    ELITE = 1
    SPIDER = 2
    PORO = 3
    TECH = 4
    YETI = 5
    ELNUK = 6

# class Effect:  
#     def trigger_effect(targets):
#         pass

@dataclass
class CardDesc:
    code: str = ""
    name: str = ""
    cardType: CardType = CardType.Unknown
    region: CardRegion = CardRegion.Unknown
    base_cost: int = -1
    base_attack: int = -1
    base_health: int = -1
    description: str = ""
    levelupDescription:str = ""
    subtypes: List[SubType] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    speed: SpellSpeed = SpellSpeed.Unknown
    rarity: CardRarity = CardRarity.Unknown
    associatedCardRefs: List[str] = field(default_factory=list)
    data: str = ""
    
    def from_json(self, code):
        data = DB.card(code)
        self.code = code
        self.name = data["name"]
        self.type = CardType[data["type"]]
        self.region = CardRegion[data["regionRef"]]
        self.base_cost = data["cost"]
        self.base_attack = data["attack"]
        self.base_health = data["health"]
        self.description = data["descriptionRaw"]
        self.levelupDescription = data["levelupDescriptionRaw"]
        self.subtypes = [SubType[d] for d in data["subtypes"]]
        self.skills = [Skill[d] for d in data["keywordRefs"]]
        self.speed = SpellSpeed.NA if data["spellSpeed"] == "" else SpellSpeed[data["spellSpeed"]]
        self.rarity = CardRarity.NoRarity if data["rarityRef"] == "None" else CardRarity[data["rarityRef"]]
        self.associatedCardRefs = data["associatedCardRefs"]
        self.data = data


@dataclass
class Card(CardDesc):
    id: str = ""
    owned: bool = False
    targets: List[Type['Card']] = field(default_factory=list)
    rect: Tuple[int,int,int,int] = (0,0,0,0)
    size: Tuple[int,int] = (0,0)
    center: Tuple[int,int] = (0,0)
    cost: int = -1
    atk: int = 0
    hp: int = 0

    def from_json(self, data, rect, size, center):
        self.id = data["CardID"]
        super().from_json(data["CardCode"])
        self.owned = data["LocalPlayer"]
        self.rect = rect
        self.size = size
        self.center = center
    
    def to_str(self):
        return self.name + "(" + str(self.atk) + "-" + str(self.hp) + ")"


################################################################################################################################
################################################              BOARD                 ############################################
################################################################################################################################
class Stage(IntEnum, metaclass=DefaultEnumMeta):
    Wait = 0
    Play = 1
    Block = 2
    Cast = 3
    Counter = 4

class TokenType(IntEnum, metaclass=DefaultEnumMeta):
    Stateless = 0
    Attack = 1
    Attacked = 2
    Scout = 3

@dataclass
class Army:
    hand: List[Card]
    deployed: List[Card]
    pit: List[Card]
    graveyard: List[Card]

    def __init__(self):
        self.hand = []
        self.deployed = []
        self.pit = []
        self.graveyard = []

    def to_str(self):
        res = ""
        # if len(self.hand) > 0:
        #     res += "HAND> " + " - ".join(( c.to_str() for c in self.hand)) + "\n"
        if len(self.deployed) > 0:
            res += "DEPLOYED> " + " - ".join(( c.to_str() for c in self.deployed)) + "\n"
        if len(self.pit) > 0:
            res += "PIT> " + " - ".join(( c.to_str() for c in self.pit)) + "\n"
        return res


@dataclass
class Player:
    deck: List[CardDesc]
    army: Army
    hp: int = 20
    mana: int = 1
    smana: int = 0
    token: TokenType = TokenType.Stateless

    def __init__(self):
        self.deck = []
        self.army = Army()

    def to_str(self):
        return str(self.hp) + "(" + str(self.mana) + "," + str(self.smana) + ")"


@dataclass
class State:
    player: Player
    opponent: Player
    spell_arena: List[Card]
    stage: Stage

    def __init__(self):
        self.player = Player()
        self.opponent = Player()
        self.spell_arena = []
        self.stage = Stage.Wait

    def to_str(self):
        res = "*****\n"
        res += str(self.stage) + " > " + self.player.to_str() + "  -  " + self.opponent.to_str() + "\n"
        res += self.player.army.to_str()
        res += self.opponent.army.to_str()
        return res

# class State:

    
#     def __init__(self):
#         self.hand = []
#         self.opp_hand = []
#         self.board = []
#         self.pit = []
#         self.cast = []
#         self.opp_pit = []
#         self.opp_board = []

#     def card_to_string(self, c):
#         s = ""
#         if "cost" in c: s = s + "(" + str(c["cost"]) + ")"
#         s = s + c["name"] + ":"
#         if "real_atk" in c: s = s + str(c["real_atk"]) 
#         if "real_hp" in c: s = s + "|" + str(c["real_hp"])
#         if "attack" in c: s = s + "(" + str(c["attack"]) + "|"
#         if "health" in c: s = s + str(c["health"]) + ")"
#         return s

#     def to_string(self):
#         str = ""
#         if len(self.hand) > 0:
#             str += "HAND> " + " - ".join(( self.card_to_string(c)  for c in self.hand)) + "\n"
#         if len(self.board) > 0:
#             str += "BOARD> " + " - ".join((self.card_to_string(c) for c in self.board)) + "\n"
#         if len(self.pit) > 0:
#             str += "PIT> " + " - ".join((self.card_to_string(c) for c in self.pit)) + "\n"
#         if len(self.cast) > 0:
#             str += "CAST> " + " - ".join((self.card_to_string(c) for c in self.cast)) + "\n"
#         if len(self.opp_pit) > 0:
#             str += "OPP_PIT> " + " - ".join((self.card_to_string(c) for c in self.opp_pit)) + "\n"
#         if len(self.opp_board) > 0:
#             str += "OPP_BOARD> " + " - ".join((self.card_to_string(c) for c in self.opp_board)) + "\n"
#         return str

# class Status:
#     hp = 0
#     mana = 0
#     smana = 0
#     opp_hp = 0
#     opp_mana = 0
#     opp_smana = 0
#     atk_token = False
#     opp_atk_token = False

#     def __init__(self):
#         self.hp = -1
#         self.mana = -1
#         self.smana = -1
#         self.opp_hp = -1
#         self.opp_mana = -1
#         self.opp_smana = -1
#         self.atk_token = False
#         self.opp_atk_token = False
        
#     def to_string(self):
#         return "hp:%s, mana:%s, smama:%s, token:%s | hp:%s, mana:%s, smana:%s, token:%s" %\
#                 (self.hp, self.mana, self.smana, "X" if self.atk_token == True else "-", \
#                 self.opp_hp, self.opp_mana, self.opp_smana, "X" if self.opp_atk_token == True else "-")


# db = Database()
# for name, card in db.name_dict.items():
#     print(name, card.cost, card.rarity, card.cardType, ">", " ".join([db.code_dict[s].name for s in card.associatedCardRefs]))
# print(len(db.code_dict.keys()))