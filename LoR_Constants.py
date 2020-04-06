
def mulligan_button_pos(card, app_height):
    x = card["TopLeftX"] + int(card["Width"]/2)
    y = app_height - card["TopLeftY"] + int(1.2*card["Height"])
    return (x, y)

def game_button_pos(face_card, app_width, app_height):
    x = app_width - int( face_card[0] + 0.5 * face_card[2] )
    y = app_height/2
    return (x,y)

def game_button_rect(face_card, app_width, app_height):
    x = app_width - int( face_card[0] + 1.2 * face_card[2] )
    y = int(app_height/2) - int(0.35 * face_card[3])
    w = int(1.2 * face_card[2])
    h = int(0.7 * face_card[3])
    return (x,y,w,h)

def status_number_rect(name, opp_face_card, face_card, app_width, app_height):
    if name == "hp":
        return hp_rect(face_card, app_width, app_height)
    elif name == "opp_hp":
        return opp_hp_rect(opp_face_card, app_width, app_height)
    elif name == "mana":
        return mana_rect(face_card, app_width, app_height)
    elif name == "opp_mana":
        return opp_mana_rect(opp_face_card, app_width, app_height)
    elif name == "smana":
        return smana_rect(face_card, app_width, app_height)
    elif name == "opp_smana":
         return opp_smana_rect(opp_face_card, app_width, app_height)

def hp_rect(face_card, app_width, app_height):
    #print(face_card)
    x = face_card[0] + int(0.9 * face_card[2])
    y = face_card[1] + int(0.2 * face_card[3])
    w = int(0.5 * face_card[2])
    h = int(0.8 * face_card[3])
    return (x,y,w,h) 

def opp_hp_rect(opp_face_card, app_width, app_height):
    x = opp_face_card[0] + int(0.9 * opp_face_card[2])
    y = opp_face_card[1] + int(0.2 * opp_face_card[3])
    w = int(0.5 * opp_face_card[2])
    h = int(0.8 * opp_face_card[3])
    return (x,y,w,h) 

def mana_rect(face_card, app_width, app_height):
    x = app_width - (face_card[0] + int(1.3 * face_card[2]))
    y = int (app_height/2 + 0.85 * face_card[3])
    w = int(0.34 * face_card[2])
    h = int(0.36 * face_card[3])
    return (x,y,w,h)

def opp_mana_rect(opp_face_card, app_width, app_height):
    x = app_width - (opp_face_card[0] + int(1.3 * opp_face_card[2]))
    y = int (app_height/2 - 1.2 * opp_face_card[3])
    w = int(0.34 * opp_face_card[2])
    h = int(0.36 * opp_face_card[3])
    return (x,y,w,h)

def smana_rect(face_card, app_width, app_height):
    x = app_width - (face_card[0] + int(0.88 * face_card[2]))
    y = int (app_height/2 + 1.25 * face_card[3])
    w = int(0.25 * face_card[2])
    h = int(0.25 * face_card[3])
    return (x,y,w,h)

def opp_smana_rect(opp_face_card, app_width, app_height):
    x = app_width - (opp_face_card[0] + int(0.88 * opp_face_card[2]))
    y = int (app_height/2 - 1.5 * opp_face_card[3])
    w = int(0.25 * opp_face_card[2])
    h = int(0.25 * opp_face_card[3])
    return (x,y,w,h)

def atk_token_rect(face_card, app_width, app_height):
    x = app_width - (face_card[0] + int(1.5 * face_card[2]))
    y = int (app_height/2 + 1.45 * face_card[3])
    w = int(0.8 * face_card[2])
    h = int(0.8 * face_card[3])
    return (x,y,w,h)

def opp_atk_token_rect(opp_face_card, app_width, app_height):
    x = app_width - (opp_face_card[0] - int(0.5 * opp_face_card[2]))
    y = int (app_height/2 - 2 * opp_face_card[3])
    w = int(0.8 * opp_face_card[2])
    h = int(0.8 * opp_face_card[3])
    return (x,y,w,h)