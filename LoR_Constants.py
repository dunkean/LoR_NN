
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

def number_rect(name, face_card, opp_face_card, app_width, app_height):
        #     status.hp = self.ocr_number("hp", 6)
        # status.opp_hp = self.ocr_number("opp_hp", 6)
        # status.mana = self.ocr_number("mana", 3)
        # status.opp_mana = self.ocr_number("opp_mana", 3)
        # status.smana = self.ocr_number("smana", 4)
        # status.opp_smana = self.ocr_number("opp_smana", 4)


#     def hp_rect(self, face_card):
#         return (face_card["TopLeftX"]+ 0.90*face_card["Width"], 
#             self.client_size[1]-face_card["TopLeftY"]+0.2*face_card["Height"], 
#             face_card["TopLeftX"] + 1.4*face_card["Width"],
#             self.client_size[1]-face_card["TopLeftY"]+face_card["Height"])

#     def mana_rect(self, face_card, opp = False):
#         if(opp == True):
#             return (self.client_size[0] - (face_card["TopLeftX"]+1.3*face_card["Width"]), 
#                     self.client_size[1]/2 - 1.25*face_card["Height"],
#                     self.client_size[0] - (face_card["TopLeftX"]+0.98*face_card["Width"]),
#                     self.client_size[1]/2 - 0.85*face_card["Height"] )
#         else:
#             return (self.client_size[0] - (face_card["TopLeftX"]+1.30*face_card["Width"]), 
#                     self.client_size[1]/2 + 0.80*face_card["Height"],
#                     self.client_size[0] - (face_card["TopLeftX"]+0.98*face_card["Width"]),
#                     self.client_size[1]/2 + 1.2*face_card["Height"])

#     def smana_rect(self, face_card, opp = False):
#         if(opp == True):
#             return (self.client_size[0] - (face_card["TopLeftX"]+0.88*face_card["Width"]), 
#                     self.client_size[1]/2 - 1.50*face_card["Height"],
#                     self.client_size[0] - (face_card["TopLeftX"]+0.63*face_card["Width"]),
#                     self.client_size[1]/2 - 1.25*face_card["Height"] )
#         else:
#             return (self.client_size[0] - (face_card["TopLeftX"]+0.88*face_card["Width"]), 
#                     self.client_size[1]/2 + 1.25*face_card["Height"],
#                     self.client_size[0] - (face_card["TopLeftX"]+0.63*face_card["Width"]),
#                     self.client_size[1]/2 + 1.50*face_card["Height"])


    
#     def atk_token_rect(self, face_card, opp = False):
#         if(opp == True):
#             return (self.client_size[0] - (face_card["TopLeftX"]+1.8*face_card["Width"]), 
#                     self.client_size[1]/2 - 2*face_card["Height"],
#                     self.client_size[0] - face_card["TopLeftX"],
#                     self.client_size[1]/2 - face_card["Height"] )
#         else:
#             return (self.client_size[0] - (face_card["TopLeftX"]+1.8*face_card["Width"]), 
#                     self.client_size[1]/2 + face_card["Height"],
#                     self.client_size[0] - face_card["TopLeftX"],
#                     self.client_size[1]/2 + 2.5*face_card["Height"])
