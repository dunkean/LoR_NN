from LoR_Datamodels import Card, CardDesc, State, ActionType, CardType, Database, Stage, CardRarity, TokenType, Skill, CardState, Player
import copy
from dataclasses import dataclass, field
from typing import List, Tuple, Type

def simulate_attack(atkr, atk_player, def_player, execute_dbl_strike = True):
    A = atkr
    B = atkr.opp

    ## ATTACKER
    if B != None and B.hp() > 0:
        bdmg = A.atk()
        admg = 0
        bnex_dmg = 0
        anex_dmg = 0
        if B.has(Skill.Tough): bdmg -= 1
        if B.has(Skill.Barrier): 
            if bdmg > 0:
                B.skills.remove(Skill.Barrier)
            bdmg = 0
        if A.has(Skill.Overwhelm) and bdmg > B.hp():
            bnex_dmg += (bdmg - B.hp())
        if A.has(Skill.Lifesteal): anex_dmg -= A.atk()

        if not A.has(Skill.QuickStrike) or B.hp() > bdmg:
            admg = B.atk()
            if A.has(Skill.Barrier): admg = 0
            elif A.has(Skill.Tough): admg -= 1
            if B.has(Skill.Lifesteal): anex_dmg -= B.atk()

        A._hp = max(A.hp() - admg, 0)
        B._hp = max(B.hp() - bdmg, 0)
        atk_player.hp -= anex_dmg
        def_player.hp -= bnex_dmg

        ## TODO put in Card class
        if A.hp() == 0: A.state = CardState.Dead
        if B.hp() == 0: B.state = CardState.Dead

        if execute_dbl_strike and A.has(Skill.DoubleStrike) and A.state != CardState.Dead:
            simulate_attack(atkr, atk_player, def_player, False)

        if A.has(Skill.Regeneration) and A.state != CardState.Dead: A._hp = A.base_health
        if B.has(Skill.Regeneration) and B.state != CardState.Dead: B._hp = B.base_health
        if A.has(Skill.Ephemeral): A.state = CardState.Dead
        if B.has(Skill.Ephemeral): B.state = CardState.Dead
    else:
        def_player.hp -= A.atk()
        if A.has(Skill.Ephemeral): A.state = CardState.Dead
        if A.has(Skill.DoubleStrike): def_player.hp -= A.atk()


def simulate_fight(state):
    sim_state = copy.deepcopy(state)
    atk_player = None
    def_player = None
    if state.stage == Stage.Block:
        atk_player = sim_state.opponent
        def_player = sim_state.player
    else:
        atk_player = sim_state.player
        def_player = sim_state.opponent

    atkrs = sorted(atk_player.army.pit, key=lambda atkr: atkr.x(), reverse=False)

    for atkr in atkrs:
        simulate_attack(atkr, atk_player, def_player)

    return sim_state


