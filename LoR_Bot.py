import logging
import sys
import time

import keyboard

from LoR_ScreenHandler import LoR_Handler
import LoR_ServerHandler as Server
import LoR_func
import LoR_Brain, LoR_Datamodels
from LoR_Datamodels import Stage, ActionType
from LoR_Brain import Action

class Bot:
    game_count = 0
    victories_count = 0
    
    # actions_active = True
    # log_active = False
    bot_active = True

    LoR = None
    brain = None
    mode = "bot"
    mulligan_done = False

    def __init__(self, mode):
        self.mode = mode
        self.LoR = LoR_Handler(LoR_func.launch_application())
        self.brain = LoR_Brain.Brain()

    def pause(self):
        self.bot_active = not self.bot_active

    # def log(self):
    #     self.log_active = not self.log_active

    # def actions(self):
    #     self.actions_active = not self.actions_active
       
    def start(self):
        if not Server.game_in_progress():
            self.launch_match(self.mode)
        
        while(True):
            if self.bot_active:
                self.run_session()
            time.sleep(0.5)


    def launch_match(self, mode): ### @TODO ADD "Ok" rect button for rematch
        # logging.info("Launching match vs %s", mode)
        if mode == "bot":
            self.LoR.wait_n_click_img(["Play", "vsAI", "Versus", "Replay"])
        elif mode == "challenger":
            self.LoR.wait_n_click_img(["Friends", "Spare", "Challenge", "Versus", "Replay"])
        elif mode == "challenged":
            self.LoR.wait_n_click_img(["Accept", "Versus", "Play"])
        elif mode == "rematch_bot":
            self.LoR.wait_n_click_img(["Continue","Replay"])
        # elif mode == "rematch_player":
        #     self.LoR.wait_n_click_img(["Continue", "Ready"])

        self.LoR.wait_for_game_to_start()
        time.sleep(3)

    def mulligan(self):
        logging.info("Mulligan...")
        if not self.bot_active:
            return
        state = self.LoR.wait_for_next_state()
        cards_to_mulligan = self.brain.mulligan(state.opponent.army.pit)
        logging.info(state.opponent.army.pit)
        self.LoR.mulligan_cards(cards_to_mulligan)
        self.LoR.click_next()
        time.sleep(2)
        

    def play_game(self): # no failsafe for wrong ocr
        if not self.bot_active:
            return
        state = self.LoR.wait_for_next_state()
        if state.stage == Stage.Wait:
            time.sleep(1)
            return
        # print(state.to_str())

        ## Ensure you get a valid state (shot can occure before the end of an animation)
        tries = 0
        while not state.is_valid():
            # print("State invalid")
            state = self.LoR.wait_for_next_state()
            tries += 1
            if tries > 3:
                break


        
        action = self.brain.get_next_action(state)
        # print("Action", action)
        if action.type == ActionType.Cast:
            self.LoR.drag_to_center(action.cards[0])
            for target in action.targets:
                self.LoR.click_card(target)
        elif action.type == ActionType.Block:
            for i in range(len(action.cards)):
                if(action.cards[i] != None):
                    self.LoR.drag_to_card(action.cards[i], action.cards[i].opp)
            self.LoR.click_next()
        elif action.type == ActionType.Attack:
            for i in range(len(action.cards)):
                self.LoR.drag_to_center(action.cards[i])
                if action.cards[i].opp != None:
                    self.LoR.drag_to_card(action.cards[i].opp, action.cards[i])
            self.LoR.click_next()
        elif action.type == ActionType.Pass:
            self.LoR.click_next()
            pass
        # self.LoR.click_next()
        time.sleep(0.5)
 

    def run_session(self):
        if not Server.game_in_progress(): ## Relaunch a game
            if self.mode == "bot" or self.mode == "rematch_bot":
                self.launch_match("rematch_bot")
            elif self.mode == "player" or self.mode == "rematch_player":
                self.launch_match("rematch_player")

        elif self.mulligan_done == False and self.LoR.detect("Mulligan") != None:
            logging.info("Mulligan detected")
            self.mulligan()
            self.mulligan_done = True

        else:
            last_game_id, _ = Server.get_last_game()
            game_id = last_game_id
            won = False
            while (game_id == last_game_id):
                self.play_game()
                game_id, won = Server.get_last_game()

            print("Game", game_id, "Finished", won)
            logging.info("...Game Finished...")
            time.sleep(2)
            self.game_count += 1
            if won: self.victories_count += 1
            self.mulligan_done = False

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
        # keyboard.add_hotkey('ctrl+shift+l', bot.log)
        # keyboard.add_hotkey('ctrl+shift+a', bot.actions)
        # try:
        bot.start()    
        # except:
            # print("Games/Won: ", bot.game_count, "/", bot.victories_count)


if __name__ == '__main__':
    print("ctrl+shift+b", "(de)activate bot")
    # print("ctrl+shift+l", "(de)activate log")
    # print("ctrl+shift+a", "(de)activate actions")
    main()