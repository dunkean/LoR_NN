import logging
import sys
import time

import keyboard

from LoR_ScreenHandler import LoR_Handler
import LoR_ServerHandler as Server
import LoR_func
import LoR_Brain, LoR_Datamodels


class Bot:
    game_count = 0
    victories_count = 0
    
    actions_active = True
    log_active = False
    bot_active = True

    LoR = None
    brain = None
    mode = "bot"

    def __init__(self, mode):
        self.mode = mode
        self.LoR = LoR_Handler(LoR_func.launch_application())
        self.brain = LoR_Brain.Brain()

    def pause(self):
        self.bot_active = not self.bot_active

    def log(self):
        self.log_active = not self.log_active

    def actions(self):
        self.actions_active = not self.actions_active
       
    def start(self):
        if not Server.game_in_progress():
            self.launch_match(self.mode)
        
        while(True):
            if self.bot_active:
                self.run_session()
            time.sleep(2)


    def launch_match(self, mode): ### @TODO ADD "Ok" rect button for rematch
        # logging.info("Launching match vs %s", mode)
        if mode == "bot":
            self.LoR.wait_n_click_img(["Play", "vsAI"])
        elif mode == "challenger":
            self.LoR.wait_n_click_img(["Friends", "Spare", "Challenge"])
        elif mode == "challenged":
            self.LoR.wait_n_click_img(["Accept"])
        elif mode == "rematch_bot":
            self.LoR.wait_n_click_img(["Play", "vsAI"])
        elif mode == "rematch_player":
            self.LoR.wait_n_click_img(["Continue", "Ready"])

        self.LoR.wait_for_game_to_start()
        time.sleep(3)

    def mulligan(self):
        logging.info("Mulligan...")
        cards = Server.get_my_cards()
        cards_to_mulligan = self.brain.mulligan(cards)
        self.LoR.mulligan_cards(cards_to_mulligan)
    

    def play_game(self): # no failsafe for wrong ocr
        state = self.LoR.wait_for_next_state()
        
        print(state.to_str())
        time.sleep(1)

        # if state.turn == 
        # action = self.brain.choose_next_action(state)
        # btn = LoR.ocr_btn_txt() #replace with pattern matching
        # if not_my_turn():
        #     time.sleep(1)
        #     continue

        # action = brain.choose_next_action()
        # if action.type == "cast":
        #     for card in action.cards:
        #         logging.info("Casting > %s", card["name"])
        #         LoR.drag_to_center(card)
        #         time.sleep(1)
        # elif action.type == "cast_n_target":
        #     for card in action.cards:
        #         LoR.drag_to_center(card)
        #         for target in card.targets:
        #             logging.info("Casting %s to %s", card, target)
        #             LoR.click_card(card)
        #             time.sleep(0.1)
        #     time.sleep(0.4)
        # elif action.type == "attack":
        #     for card in action.cards:
        #         logging.info("Attack with %s", card["name"])
        #         LoR.drag_to_center(card)
        #         time.sleep(0.2)
        # elif action.type == "block":
        #     for card in action.cards:
        #         logging.info("Blocking %s with %s", card["name"], card.target["name"])
        #         LoR.drag_to_block((card, card.target))
        #         time.sleep(0.5)

        # LoR.click_next()

    

    def run_session(self):
        if not Server.game_in_progress(): ## Relaunch a game
            if self.mode == "bot":
                self.launch_match("rematch_bot")
            else:
                self.launch_match("rematch_player")

        elif self.LoR.detect("Mulligan") != None:
            # logging.info("Mulligan detected")
            self.mulligan()

        else:
            last_game_id, _ = Server.get_last_game()
            game_id = last_game_id
            won = False

            while (game_id == last_game_id):
                self.play_game()
                game_id, won = Server.get_last_game()

            self.game_count += 1
            if won: self.victories_count += 1

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("debug.log")
        ]
    )

    if sys.argv[1] == "capture":
        LoR_Handler.raw_capture()
    else:
        bot = Bot(sys.argv[1])
        keyboard.add_hotkey('ctrl+shift+b', bot.pause)
        keyboard.add_hotkey('ctrl+shift+l', bot.log)
        keyboard.add_hotkey('ctrl+shift+a', bot.actions)
        try:
            bot.start()    
        except:
            print("Games/Won: ", game_count, "/", vic_count)


if __name__ == '__main__':
    print("ctrl+shift+b", "(de)activate bot")
    print("ctrl+shift+l", "(de)activate log")
    print("ctrl+shift+a", "(de)activate actions")
    main()