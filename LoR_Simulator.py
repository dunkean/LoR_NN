import random
import itertools
import uuid 

short_sk = ["QA", "Ov", "El", "Im", "Ch", "Re", "LB", "Li", "To", "Ba", "Fe", "CB", "DA", "Ep"]
sk = [  'Quick Attack', 'Overwhelm', 'Elusive', 'Imbue', 'Challenger', 
        'Regeneration', 'Last Breath', 'Lifesteal', 'Tough', 'Barrier', 
        'Fearsome', "Can't Block", 'Double Attack', 'Ephemeral']
score_sk = [ 3, 2, 2, 0, 1, 2, 1, 2, 1, 3, 1, -1, 4, -1]
class Unit:
    code = None
    id = -1
    dmg = 0 ## Delta fight hp
    atk = 0 ## Current attack
    hp = 0
    skills = []
    rarity = None
    effects = []
    dead = False

    def __init__(self, atk, hp, skills, id):
        self.atk = atk
        self.hp = hp
        self.id = id
        if skills != None:
            self.skills = skills
        pass

    def clone(unit):
        if unit == None:
            return None
        a = Unit(unit.atk, unit.hp, unit.skills, unit.id)
        return a

    def has(self, skill):
        if skill in self.skills:
            return True
        return False

    def __str__(self):
        symbol = "*" if self.dead else ""
        return symbol + str(self.atk) + "|" + str(self.hp) + "(" + ", ".join(sk[short_sk.index(c)] for c in self.skills) + ") > " + str(self.dmg)


def solv_duel(A, B, nex_dmg = 0, onex_dmg = 0, compute_DA = True): ## atkr, blkr
    ## ATTACKER
    if B != None and not B.dead:
        B.dmg += A.atk
        if B.has("To"): B.dmg -= 1
        if B.has("Ba"): 
            if B.dmg > 0:
                B.skills.remove("Ba")
            B.dmg = 0
        if A.has("Ov") and B.dmg > B.hp:
            nex_dmg += (B.dmg - B.hp)
        if A.has("Li"): onex_dmg -= A.atk 

        if not A.has("QA") or B.hp > B.dmg:
            A.dmg = B.atk
            if A.has("Ba"): A.dmg = 0
            elif A.has("To"): A.dmg -= 1
            if B.has("Li"): nex_dmg -= B.atk

        if A.dmg >= A.hp: A.dead = True
        if B.dmg >= B.hp: B.dead = True

        if A.has("DA") and compute_DA and not A.dead:
            A, B, nex_dmg, onex_dmg = solv_duel(A, B, nex_dmg, onex_dmg, False)

        if A.has("Re") and A.dmg < A.hp: A.dmg  = 0
        if B.has("Re") and B.dmg < B.hp: B.dmg  = 0
        # if A.has("LB"): apply effect
        if A.has("Ep"): A.dead = True
        if B.has("Ep"): B.dead = True
    else:
        nex_dmg += A.atk
        if A.has("Ep"): A.dead = True

    return A, B, nex_dmg, onex_dmg


def solve_fight(atkrs, blokrs):
    nex_dmg = 0
    onex_dmg = 0
    new_atkrs = []
    new_blkrs = []
    for i in range(len(atkrs)):
        A = Unit.clone(atkrs[i])
        B = Unit.clone(blokrs[i])
        if A == None:
            continue
        if B != None and (\
            ( B.has("CB") ) \
        or ( A.has("El") and not B.has("El") ) \
        or ( A.has("Fe") and B.atk <= 3 )):
            # print("Removing", B)
            B = None
        # print(A, "vs", B)
        A, B, nex_dmg, onex_dmg = solv_duel(A, B, nex_dmg, onex_dmg)
        new_atkrs.append(A)
        new_blkrs.append(B)
        # print(A, "vs", B)
        # print("------------")
    return -onex_dmg, -nex_dmg, new_atkrs, new_blkrs


def evaluate_board(units, prt = False):
    nb = 0
    score = 0
    for u in units:
        unit_score = 0
        if u != None and not u.dead:
            nb += 1
            unit_score += u.atk * u.atk
            unit_score += u.hp * u.hp
            skill_score = 0
            for s in u.skills:
                skill_score += score_sk[short_sk.index(s)]
            unit_score *= (0.3*skill_score+1)
            if prt:
                print(u, "score:", round(unit_score,2))
            score += unit_score
    if prt: print("-----------------")
    return score #* (1 + (nb / 20))
    

def generate_blk_permutations(atkrs, board):
    board.extend([None for i in range(len(atkrs)+1)])
    perm = list(itertools.permutations(board, len(atkrs)))
    perm = list(dict.fromkeys(perm))
    return perm


def random_unit(lvl = 9, nb_skills = 2):
    skills = random.choices(short_sk, k=random.randint(0,nb_skills))
    atk = random.randint(1,lvl)
    hp = random.randint(1,lvl)
    return Unit(atk, hp, skills, uuid.uuid1())

def evaluate_fight(atk_pit, blk_pit, atk_board, blk_board):
    anex, dnex, atks, blks = solve_fight(atk_pit, blk_pit)
    off_blkrs = []
    off_atkrs = []
    for un in list(blk_board):
        has_blocked = False
        for u in blks:
            if u == None or un == None:
                continue
            if u.id == un.id:
                has_blocked = True
        if has_blocked == False and un != None:
            off_blkrs.append(un)
            if un.has("Ep"): un.dead = True

    for un in list(atk_board):
        has_attacked = False
        for u in atks:
            if u == None or un == None:
                continue
            if u.id == un.id:
                has_attacked = True
        if has_attacked == False and un != None:
            off_atkrs.append(un)
            if un.has("Ep"): un.dead = True
        
    nb_a = sum(1 for p in atk_pit if p != None and p.dead == False)
    nb_a += len(off_atkrs)
    nb_b = sum(1 for p in blk_pit if p != None and p.dead == False)
    nb_b += len(off_blkrs)
    score_nb = (nb_b - nb_a) * (nb_b - nb_a) * (nb_b - nb_a) * 10
    # print("Overwhelm number score:", score_nb)
    ascore = evaluate_board(atks) + evaluate_board(off_atkrs)
    dscore = evaluate_board(blks) + evaluate_board(off_blkrs)
    score = dscore - ascore + dnex*dnex*dnex + 1.5*score_nb
    return score, atks, off_atkrs, blks, off_blkrs, anex, dnex
    
def get_best_block(atkrs, blkrs):
    best_fight = -10000
    b_hp = 0
    b_blkrs = None
    b_atkrs = None
    b_oblkrs = None
    b_oatkrs = None
    worst_fight = 10000
    w_atkrs = None
    w_blkrs = None
    w_oblkrs = None
    w_oatkrs = None
    w_hp = 0
    for blkrs_perm in generate_blk_permutations(atkrs, blkrs):
        # pass
        blkrs_cp = list(blkrs_perm).copy()
        atkrs_cp = list(atkrs).copy()
        score, atks, off_atkrs, blks, off_blkrs, anex, dnex = evaluate_fight(atkrs_cp, blkrs_cp, atkrs, blkrs)
        if score < worst_fight:
            worst_fight = score
            w_blkrs = list(blks)
            w_atkrs = list(atks)
            w_oblkrs = list(off_blkrs)
            w_oatkrs = list(off_atkrs)
            w_hp = dnex
        if score > best_fight:
            best_fight = score
            b_blkrs = list(blks)
            b_atkrs = list(atks)
            b_oblkrs = list(off_blkrs)
            b_oatkrs = list(off_atkrs)
            b_hp = dnex

    print("*******BEST********", round(best_fight,2), ">", b_hp)
    for i in range(len(atkrs)):
        print(b_atkrs[i], "vs", b_blkrs[i])
    for u in b_oblkrs:
        if u != None:
            print("-def@home-", u)
    for u in b_oatkrs:
        if u != None:
            print("-atk@home-", u)
    # evaluate_board(b_blkrs, True)
    print("*******WORST********", round(worst_fight,2), ">", w_hp)
    for i in range(len(atkrs)):
        print(w_atkrs[i], "vs", w_blkrs[i])
    for u in w_oblkrs:
        if u != None:
            print("-def@home-", u)
    for u in w_oatkrs:
        if u != None:
            print("-atk@home-", u)
    print("***********")
    # evaluate_board(w_blkrs, True)
    return b_blkrs


def generate_atk_permutations(board, blkrs):
    attackers_configs = []
    for i in range(len(board) + 1):
        comb = list(itertools.combinations(board,i))
        attackers_configs.append(comb)
        # print("--- ATTACKERS COMBINATIONS --- of size >", i, "generated", len(comb))    
    
    blockers_configs = []
    blkrs.extend([None for i in range(len(board) + 1)])
    for i in range(len(board) + 1):
        perm = list(itertools.permutations(blkrs,i))
        perm = list(dict.fromkeys(perm))
        blockers_configs.append(perm)
        # print("--- BLOCKERS PERMUTATIONS --- of size >", i, "generated", len(perm))

    atkrs_combi = []
    blkrs_combi = []
    for i in range(len(board) + 1):
        for atkrs in attackers_configs[i]:
            atkrs_combi.append(atkrs)
            tmp = []
            for blkrs in blockers_configs[i]:
                tmp.append(blkrs)
            blkrs_combi.append(tmp)
                # combinations.append((atkrs, blkrs))
    
    # print("Total of possible fights", len(combinations))
    return atkrs_combi, blkrs_combi

def get_best_attack(atkrs, blkrs):
    best_fight = 10000
    b_hp = 0
    b_blkrs = None
    b_atkrs = None
    b_oblkrs = None
    b_oatkrs = None
    worst_fight = -10000
    w_atkrs = None
    w_blkrs = None
    w_oblkrs = None
    w_oatkrs = None
    w_hp = 0
    atkrs_perms, blkrs_perms = generate_atk_permutations(atkrs, blkrs)
    for i in range(len(atkrs_perms)) :
        blkrs_perm = blkrs_perms[i]
        atkrs_perm = atkrs_perms[i]
        o_best_fight = -10000
        o_b_hp = 0
        o_b_blkrs = None
        o_b_oblkrs = None
        o_b_atkrs = None
        o_b_oatkrs = None
        for blk_t in blkrs_perm:
            blkrs_cp = list(blk_t).copy()
            atkrs_cp = list(atkrs_perm).copy()
            score, atks, off_atkrs, blks, off_blkrs, anex, dnex = evaluate_fight(atkrs_cp, blkrs_cp, atkrs, blkrs)
            if score > o_best_fight:
                o_best_fight = score
                o_b_blkrs = list(blks)
                o_b_oblkrs = list(off_blkrs)
                o_b_atkrs = list(atks)
                o_b_oatkrs = list(off_atkrs)
                o_b_hp = dnex

        if o_best_fight > worst_fight:
            worst_fight = o_best_fight
            w_blkrs = o_b_blkrs
            w_atkrs = o_b_atkrs
            w_oblkrs = o_b_oblkrs
            w_oatkrs = o_b_oatkrs
            w_hp = o_b_hp
        if o_best_fight < best_fight:
            best_fight = score
            b_blkrs = o_b_blkrs
            b_atkrs = o_b_atkrs
            b_oblkrs = o_b_oblkrs
            b_oatkrs = o_b_oatkrs
            b_hp = o_b_hp
    
    print("*******BEST********", round(best_fight,2), ">", b_hp)
    for i in range(len(b_atkrs)):
        print(b_atkrs[i], "vs", b_blkrs[i])
    for u in b_oblkrs:
        if u != None:
            print("-def@home-", u)
    for u in b_oatkrs:
        if u != None:
            print("-atk@home-", u)
    # evaluate_board(b_blkrs, True)
    print("*******WORST********", round(worst_fight,2), ">", w_hp)
    for i in range(len(w_atkrs)):
        print(w_atkrs[i], "vs", w_blkrs[i])
    for u in w_oblkrs:
        if u != None:
            print("-def@home-", u)
    for u in w_oatkrs:
        if u != None:
            print("-atk@home-", u)
    print("***********")
    # evaluate_board(w_blkrs, True)


## test fight
atkrs = []
blkrs = []
for i in range(5):
    atkrs.append(random_unit(6,0))

for j in range(3):
    blkrs.append(random_unit(4,0))
        
print(round(evaluate_board(atkrs, True),2), "****** VS ********", round(evaluate_board(blkrs, True),2))
# get_best_block(atkrs, blkrs)
get_best_attack(atkrs, blkrs)



# import json
# json_file = open('set1-en_us.json', encoding="utf8")
# dict = {}
# for p in json.load(json_file):
#     if p["type"] == "Spell":
#         dict[p["descriptionRaw"]] = None

# print(list(dict))

# file = open("log_simu.txt","w") 
# file.write("\n".join(c for c in list(dict)))
# file.close()