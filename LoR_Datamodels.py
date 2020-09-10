from dataclasses import dataclass, field
from typing import List, Tuple, Type
from enum import EnumMeta, IntEnum
import json
from lor_deckcodes import LoRDeck, CardCodeAndCount

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
                self.code_dict[data["cardCode"]] = data
        with open('set2-en_us.json', encoding="utf8") as json_file:
            for data in json.load(json_file):
                self.code_dict[data["cardCode"]] = data
        with open('set3-en_us.json', encoding="utf8") as json_file:
            for data in json.load(json_file):
                self.code_dict[data["cardCode"]] = data

    def card(self, code):
        if code in self.code_dict:
            return self.code_dict[code]
        # else:
        #     return self.code_dict["UNK"]

    def get_deck(self, deck_code):
        deck = []
        lor_deck = LoRDeck.from_deckcode(deck_code)
        for c in list(lor_deck):
            [nb, code] = c.split(":")
            for _ in range(int(nb)):
                card_desc = CardDesc()
                card_desc.from_json(code)
                deck.append(card_desc)
        return deck

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
    Bilgewater = 7
    Targon = 8

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
    Attack = 1
    Attune = 2
    Barrier = 3
    Burst = 4
    CantBlock = 5
    Capture = 6
    Challenger = 7
    DoubleStrike = 8
    Drain = 9
    Elusive = 10
    Enlightened = 11
    Ephemeral = 12
    Fast = 13
    Fearsome = 14
    Fleeting = 15
    Frostbite = 16
    Imbue = 17
    Immobile = 18
    LastBreath = 19
    Lifesteal = 20
    Obliterate = 21
    Overwhelm = 22
    Play = 23
    QuickStrike = 24
    Recall = 25
    Regeneration = 26
    Scout = 27
    Skill = 28
    Slow = 29
    Stun = 30
    Tough = 31
    Trap = 32
    Vulnerable = 33
    Weakest = 34
    SpellOverwhelm = 35
    Autoplay = 36
    Deep = 37
    SpellShield = 38
    Fury = 39



class SubType(IntEnum, metaclass=DefaultEnumMeta):
    Unknown = 0
    ELITE = 1
    SPIDER = 2
    PORO = 3
    TECH = 4
    YETI = 5
    ELNUK = 6
    SEAMONSTER = 7

class CardState(IntEnum, metaclass=DefaultEnumMeta):
    Active = 0
    Inactive = 1
    Dead = 2
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
        if data == None: return
        self.code = code
        self.name = data["name"]
        self.type = CardType[data["type"]]
        self.region = CardRegion[data["regionRef"]]
        self.base_cost = data["cost"]
        self.base_attack = data["attack"]
        self.base_health = data["health"]
        self.description = data["descriptionRaw"]
        self.levelupDescription = data["levelupDescriptionRaw"]
        self.subtypes = [SubType[d.replace(" ","")] for d in data["subtypes"]]
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
    opp: Type['Card'] = None
    state: CardState = CardState.Inactive
    rect: Tuple[int,int,int,int] = (0,0,0,0)
    size: Tuple[int,int] = (0,0)
    center: Tuple[int,int] = (0,0)
    _cost: int = -1
    _atk: int = -1
    _hp: int = -1
    # dmg: int = 0
    detected_skills: List[Skill] = field(default_factory=list)

    def __str__(self):
        return self.name + "_" + str(self.id)
    def __repr__(self):
        return self.name + "_" + str(self.id)
    
    def __hash__(self):
        return hash(str(self))

    def __eq__(self,other):
        if other == None:
            return False
        return self.name == other.name and self.id == other.id

    def from_json(self, data, rect, size, center):
        self.id = data["CardID"]
        super().from_json(data["CardCode"])
        self.owned = data["LocalPlayer"]
        self.rect = rect
        self.size = size
        self.center = center
    
    def to_str(self):
        if self._cost == -1:
            return self.name + "(" + str(self.atk()) + ":" + str(self.hp()) + ")"
        else:
            return "(" + str(self.cost()) + ")" + self.name

    def has(self, skill):
        return skill in self.skills

    def x(self):
        return self.rect[0]

    def y(self):
        return self.rect[1]

    def width(self):
        return self.size[0]

    def height(self):
        return self.size[1]

    def atk(self):
        if self._atk == -1:
            return self.base_attack
        return self._atk
    
    def hp(self):
        if self._hp == -1:
            return self.base_health
        return self._hp

    def cost(self):
        if self._cost == -1:
            return self.base_cost
        return self._cost

    def is_valid(self):
        return True
        # return not self._atk == -1 and not self._hp == -1 # TODO CHECK THAT

################################################################################################################################
################################################              BOARD                 ############################################
################################################################################################################################
class Stage(IntEnum, metaclass=DefaultEnumMeta):
    Wait = 0
    Play = 1
    Block = 2
    Cast = 3
    Counter = 4
    Unknown = 5

class TokenType(IntEnum, metaclass=DefaultEnumMeta):
    Stateless = 0
    Attack = 1
    Round = 2
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
        self.hand.sort(key=lambda x: x.rect[0])
        self.deployed.sort(key=lambda x: x.rect[0])
        self.pit.sort(key=lambda x: x.rect[0])
        
        if len(self.hand) > 0:
            res += "HAND> " + " - ".join(( c.to_str() for c in self.hand)) + "\n"
        if len(self.deployed) > 0:
            res += "DEPLOYED> " + " - ".join(( c.to_str() for c in self.deployed)) + "\n"
        if len(self.pit) > 0:
            res += "PIT> " + " - ".join(( c.to_str() for c in self.pit)) + "\n"
        return res

    def is_valid(self):
        for card in self.hand:
            if not card.is_valid():
                return False
        for card in self.deployed:
            if not card.is_valid():
                return False
        for card in self.pit:
            if not card.is_valid():
                return False
        
        return True

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
        return str(self.hp) + "(" + str(self.mana) + "," + str(self.smana) + ")" + ":" + str(self.token)
    
    def is_valid(self):
        return not self.hp == -1 and not self.mana == -1 and not self.smana == -1 and self.army.is_valid()


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

    def is_valid(self):
        return self.player.is_valid() and self.opponent.is_valid()



class ActionType(IntEnum, metaclass=DefaultEnumMeta):
    Unknown = 0
    Cast = 1
    Block = 2
    Attack = 3
    Pass = 4











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