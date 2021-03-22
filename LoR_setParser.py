# "associatedCardRefs": [],
# "regionRef": "Bilgewater",
# "attack": 5,
# "cost": 5,
# "health": 6,
# "description": "<link=vocab.RoundStart><style=Vocab>Round Start</style></link>: Create a <link=keyword.Fleeting><sprite name=Fleeting><style=Keyword>Fleeting</style></link> <link=card.create><style=AssociatedCard>Sleep with the Fishes</style></link> in hand.",
# "name": "Jack, the Winner",
# "cardCode": "03BW006",
# "keywordRefs": [],
# "spellSpeedRef": "",
# "rarityRef": "Epic",
# "subtype": "",
# "subtypes": [],
# "supertype": "",
# "type": "Unit"


import json
from html.parser import HTMLParser

card = {}
keyword = {}
vocab = {}
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if "link=" in tag:
            tag = tag.replace("link=","")
            if "card" in tag:
                card[tag.replace("card.","")] = None
            elif "keyword" in tag:
                keyword[tag.replace("keyword.","")] = None
            elif "vocab" in tag:
                vocab[tag.replace("vocab.","")] = None
        # print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        pass

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        pass


cards = {}

with open('set1-en_us.json', encoding="utf8") as json_file:
    for data in json.load(json_file):
        cards[data["cardCode"]] = data
with open('set2-en_us.json', encoding="utf8") as json_file:
    for data in json.load(json_file):
        cards[data["cardCode"]] = data
with open('set3-en_us.json', encoding="utf8") as json_file:
    for data in json.load(json_file):
        cards[data["cardCode"]] = data


parser = MyHTMLParser()
triggers_actions = ["Give", "Grant", "Deal", "Draw", "When I'm summoned", "Kill", "When you summon", "To play me", "When I survive", "Heal", \
                    "Reduce my cost", "Reduce the cost", "When allies attack", "When you draw"]
for key in cards.keys():
    c = cards[key]
    # print("***********")
    # print(card["name"])
    # print("***********")
    parser.feed(c["description"])
    if c["description"] != "" and "link" not in c["description"]:
        if not any( k in c["description"] for k in triggers_actions):
            print (c["description"])
            
print("***********")
print(card.keys())
print("***********")
print(vocab.keys())
print("***********")
print(keyword.keys())


new_list = []
for key in cards.keys():
    c = cards[key]
    new_list.append({
        "code": key,
        "name": c["name"],
        "desc": c["descriptionRaw"]
    })


new_list_json = json.dumps(new_list, indent=2)

with open('data.json', 'w') as outfile:
    json.dump(new_list_json, outfile, indent=2)


# print(len(cards.keys()))

actions_on_units = ["Give", "Grant", "Kill", "Heal", "Deal", "Transform", "ChangeCost", "SetCost", "Strike-Attack", "SetKeyword", "Silence", "Drain", "ModifyCounter", "SetVar", "LevelUp"]
actions_on_cards = ["Draw", "Create", "Shuffle", "Summon-Play", "Toss", "Cast-Play", "Discard", "Revive", "Steal", "Capture", "Recall", "Remove_from_combat", "Pick"]
actions_on_board = ["RefillMana", "StrikeNexus", "Rally"]
events_on_cards = ["Allegiance", "Drawn", "Discarded", "Have_X_Cards", "Cast", "Summoned", "Deep", "Daybreak", "Nightfall"]
events_on_units = ["Damage", "Supported", "Strongest", "Weakest", "Behold", "Take_Damage", "Dies", "Survived", "KeywordChanged", "FirstAttack", "FirstRoundAttack"]
events_on_board = ["RoundStart", "RoundEnd", "NexusDamage", "OppNexusDamage", "Plunder", "Number_of_allies"]
keywords_on_units = ['stun', 'recall', 'fleeting', 'playskillmark', 'barrier', 'lifesteal', 'elusive', 'frostbite', 'last', 'ephemeral', 'obliterate', 'attackskillmark', 'capture', 'quick', 'weakest', 'challenger', 'fearsome', 'drain', 'overwhelm', 'tough', 'burst', 'skill', 'enlightened', 'fast', 'slow', 'double', 'vulnerable', 'scout', 'spellshield', 'nightfall', 'invoke', 'fury', 'regeneration', 'daybreak']




#### DATA.JSON
# keywords:
## - effect = [A,B] : A or B    - effect = [[A,B]] : A and B
### - target: ally, evt_target, atking_ennemy,other_allies,ennemy,supported, unit, self

#--- ACTIONS ---#
### - stats: +x|+y
### - deal: x
### - strike
### - buff: (+skill,-skill)

### - trigger: (summoned, round_end, support)
#### - source: player
#### - target: ennemy
#### - event: (stun, recall)




##### TRIGGER - register(trigger, triggerFilter, action, params, targets, params, targetfilter)
##### SUMMON_CONDITION - test(condition, param)
##### ACTION (action, params, target, params, targetfilter)

##### LEVEL_UP (trigger, triggerFilter, action, params, targets, params, targetfilter)


# Trigger.Play should be facultative
##### broadcast triggers on event and execute action if necessary
#-------- Persistent
##  Yasuo: (Trigger.Keyword_cCanged, ["stun", "recall"], Action.Deal, 2, Target.triggered, None)
#   Nautilus: (Trigger.Always, None, Action.ChangeCost, -4, Target.subtype, SubType.SeaMonster)
#   Citybreaker (Trigger.RoundStart, None, Action.Deal, 1, Target.oppNexus)
#   The Leviathan (Action.DrawSpecific, "02NX001") 3x(Trigger.RoundStart, None, Action.Deal, 1, Target.oppNexus)
#   Scales of the Dragon (Trigger.Summon-Play, None, Action.Create, "02IO002T1")
#   Cloud Drinker (Trigger.Always, None, Action.ChangeCost, -1, Target.spells, SpellType.Burst)
#   Fiora (Trigger.UnitKilled, (None, FioraID), Action.ModifyCounter, 1) (Trigger.Counter, 2, ActionLevelUp)
#   Spectral Matron (Trigger.Summon-Play, None, Action.SetVar, 1, Target.allyinhand, id) (Action.Summon, None, Target.Var) (Action.SetKeyword, Keyword.Ephemeral, Target.Var)
# *******Pb de variables à transmettre à l_action suivante
#
# on_keyword(['stun','recall']) do Action.deal(2)
#-------- Instant
#   Riptide: if (Action.RemoveFromCombat, None, Target.card, id) then (Action.Rally, None, Target.player, None)
#   Vladimir's Transfusion if (Action.Deal, 1, Target.ally, id) then (Action.Grant, (2,2), Target.ally, [id])
#   

#
# (evt) {
#       if event == "KeywordChanged":
#           if any(k in evt.card.keywords for k in ["stun", "recall"])
#               action("Deal", evt.card, 2)
# 
# }




### CARD - Trigger<ONCE, ALWAYS, ON_BOARD>(origin, type) - condition > action

##Format - Name: Context - Src_Filter - Event(event_src[], event_targets[]) - Action

## YASUO    - Trigger_1: Always - Units - keyword(["stun", "recall"]) - counter++
##          - Trigger_2: Always - counter > 4 - level_up
##          - Trigger_3: OnBoard - Ennemy_units - keywordadded(["stun", "recall"]) - Deal(2, event_src)

## The Leviathan - Trigger_1: Once - Me - onsummon - Draw("02NX001")
#                - Trigger_2: Always - None - round_start - Deal(1, oppNexus)
#                - Trigger_3: Always - None - round_start - Deal(1, oppNexus)
#                - Trigger_4: Always - None - round_start - Deal(1, oppNexus)
# 
# 
# Fiora    - Trigger_1: Always - Units - keyword(["stun", "recall"]) - counter++
##         - Trigger_2: Always - counter > 2 - level_up
##         - Trigger_3: OnBoard - Ennemy_units - keywordadded(["stun", "recall"]) - Deal(2, event_src)