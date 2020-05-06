
def mulligan_button_pos(card, app_height):
    x = card["TopLeftX"] + int(card["Width"]/2)
    y = app_height - card["TopLeftY"] + int(1.2*card["Height"])
    return (x, y)

def game_button_pos(face_card, app_width, app_height):
    x = app_width - int( face_card[0] + 0.5 * face_card[2] )
    y = app_height/2
    return (x,y)

def game_button_rect(face_card, app_width, app_height):
    x = app_width - int( face_card[0] + 1.15 * face_card[2] )
    y = int(app_height/2) - int(0.35 * face_card[3])
    w = int(1.4 * face_card[2])
    h = int(0.7 * face_card[3])
    return (x,y,w,h)

def card_prop_rect(card, prop, pos, app_width, app_height):
    l = card.rect[0]
    t = card.rect[1]
    w = card.size[0]
    h = card.size[1]
    b = card.rect[3]

    if prop == "hp":
        if pos == "bot":
            return (l+int(w/2+h/20) , b-int(h/4) , int(h/3) , int(6.5*h/30))
        else:
            return (l+int(w/2+h/20) ,  t+int(h/20) , int(h/3) , int(h/5))
    elif prop == "atk":
        if pos == "bot":
            return (l+int(w/2-h/3) , b-int(h/4) , int(h/3) , int(6*h/30))
        else:
            return (l+int(w/2-h/3) , t+int(h/20) , int(h/3) , int(h/5))
    elif prop == "cost":
        if pos == "bot": ## should not happen
            return (0,0,0,0)
        else:
            return (l, t, int(h/6) , int(h/6))


def status_number_rect(name, opp, face_card, opp_face_card, app_width, app_height):
    if name == "hp":
        if opp:
            return opp_hp_rect(opp_face_card, app_width, app_height)
        else:
            return hp_rect(face_card, app_width, app_height)
    elif name == "mana":
        if opp:
            return opp_mana_rect(opp_face_card, app_width, app_height)
        else:
            return mana_rect(face_card, app_width, app_height)
    elif name == "smana":
        if opp:
            return opp_smana_rect(opp_face_card, app_width, app_height)
        else:
            return smana_rect(face_card, app_width, app_height)

def hp_rect(face_card, app_width, app_height):
    #print(face_card)
    x = face_card[0] + int(0.9 * face_card[2])
    y = face_card[1] + int(0.2 * face_card[3])
    w = int(0.5 * face_card[2])
    h = int(0.6 * face_card[3])
    return (x,y,w,h) 

def opp_hp_rect(opp_face_card, app_width, app_height):
    x = opp_face_card[0] + int(0.92 * opp_face_card[2])
    y = opp_face_card[1] + int(0.2 * opp_face_card[3])
    w = int(0.5 * opp_face_card[2])
    h = int(0.6 * opp_face_card[3])
    return (x,y,w,h) 

def mana_rect(face_card, app_width, app_height):
    x = app_width - (face_card[0] + int(1.35 * face_card[2]))
    y = int (app_height/2 + 0.83 * face_card[3])
    w = int(0.45 * face_card[2])
    h = int(0.40 * face_card[3])
    return (x,y,w,h)

def opp_mana_rect(opp_face_card, app_width, app_height):
    x = app_width - (opp_face_card[0] + int(1.4 * opp_face_card[2]))
    y = int (app_height/2 - 1.2 * opp_face_card[3])
    w = int(0.51 * opp_face_card[2])
    h = int(0.36 * opp_face_card[3])
    return (x,y,w,h)

def smana_rect(face_card, app_width, app_height):
    x = app_width - (face_card[0] + int(0.93 * face_card[2]))
    y = int (app_height/2 + 1.25 * face_card[3])
    w = int(0.28 * face_card[2])
    h = int(0.25 * face_card[3])
    return (x,y,w,h)

def opp_smana_rect(opp_face_card, app_width, app_height):
    x = app_width - (opp_face_card[0] + int(0.92 * opp_face_card[2]))
    y = int (app_height/2 - 1.49 * opp_face_card[3])
    w = int(0.28 * opp_face_card[2])
    h = int(0.28 * opp_face_card[3])
    return (x,y,w,h)

def atk_token_rect(face_card, app_width, app_height):
    x = app_width - (face_card[0] + int(1.5 * face_card[2]))
    y = int (app_height/2 + 1.45 * face_card[3])
    w = int(0.8 * face_card[2])
    h = int(0.8 * face_card[3])
    return (x,y,w,h)

def opp_atk_token_rect(opp_face_card, app_width, app_height):
    x = app_width - (opp_face_card[0] + int(1.5 * opp_face_card[2]))
    y = int (app_height/2 - 2.2 * opp_face_card[3])
    w = int(0.8 * opp_face_card[2])
    h = int(0.8 * opp_face_card[3])
    return (x,y,w,h)