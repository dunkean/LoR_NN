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

bot_active = True
bot_running = True

class Bot:
    game_count = 0
    victories_count = 0
    
    global bot_active
    LoR = None
    brain = None
    mode = "bot"
    mulligan_done = False

    def __init__(self, mode):
        self.mode = mode
        self.LoR = LoR_Handler(LoR_func.launch_application())
        self.brain = LoR_Brain.Brain()

    def start(self):
        if not Server.game_in_progress():
            self.launch_match(self.mode)
        
        while(True):
            if self.game_count >= 6:
                return
            if bot_active:
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
        if not bot_active:
            return
        state = self.LoR.wait_for_next_state()
        cards_to_mulligan = self.brain.mulligan(state.opponent.army.pit)
        logging.info(state.opponent.army.pit)
        self.LoR.mulligan_cards(cards_to_mulligan)
        self.LoR.click_next()
        time.sleep(2)
        

    def play_game(self): # no failsafe for wrong ocr
        if not bot_active:
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
            time.sleep(0.3)
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

            logging.info("...Game Finished...")
            time.sleep(5)
            self.game_count += 1
            if won: self.victories_count += 1
            self.mulligan_done = False
            print("Game", game_id, "Finished", won, "at", time.strftime("%H:%M:%S", time.localtime()), self.victories_count, "/", self.game_count)

def pause():
    global bot_active
    bot_active = not bot_active
    print("Running", bot_active)

def abort_bot():
    global bot_running
    bot_running = False
    print("Stoping bot")
    sys.exit(1)

def main():
    global bot_running
    logging.basicConfig(
        level=logging.WARN,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("debug.log")
        ]
    )
    keyboard.add_hotkey('ctrl+shift+w', abort_bot) 
    keyboard.add_hotkey('ctrl+shift+b', pause)   

    mode = sys.argv[1]

    if sys.argv[1] == "capture":
        LoR_Handler.raw_capture()
    else:
        while(bot_running):
            bot = Bot(mode)
            try:
                print("Start at", time.strftime("%H:%M:%S", time.localtime()))
                bot.start()    
            except:
                mode = "rematch_bot" if (mode == "bot" or mode == "rematch_bot") else "rematch_player"
                print("Exception catch, relaunch")

            mode = "rematch_bot" if (mode == "bot" or mode == "rematch_bot") else "rematch_player"

if __name__ == '__main__':
    print("ctrl+shift+b", "pause/run bot")
    print("ctrl+shift+w", "(de)activate failsafe")
    main()