import os
import enum
import abc
from game_window import GameImages, GameWindow, GameEvent


class States(enum.Enum):
    IDLE = 0
    WAITING_FOR_GAME_TO_LOAD = 1
    SELECTING_LANGUAGE = 2
    STARTING_NEW_GAME = 3
    HANDLING_EVENT = 4


class BaseState:
    def __init__(self, game_window:GameWindow):
        self.game_window = game_window

    def run(self) -> States:
        self.game_window.grab_game_image()
        self.state_actions()
        self.game_window.grab_game_image()
        return self.check_for_state_change()

    @abc.abstractmethod
    def state_actions(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def check_for_state_change(self) -> States:
        raise NotImplementedError()


class IdleState(BaseState):
    def __init__(self, game_window: GameWindow):
        super().__init__(game_window)

    def state_actions(self):
        pass

    def check_for_state_change(self) -> States:
        return States.IDLE


class WaitingForGameToLoadState(BaseState):
    def __init__(self, game_window: GameWindow):
        super().__init__(game_window)

    def state_actions(self):
        pass

    def check_for_state_change(self) -> States:
        center = self.game_window.look_for_image(GameImages.LANG_SELECT_ENG)
        if center[0] != -1:
            return States.SELECTING_LANGUAGE
        else:
            return States.WAITING_FOR_GAME_TO_LOAD
        

class SelectingLanguageState(BaseState):
    def __init__(self, game_window: GameWindow):
        super().__init__(game_window)

    def state_actions(self):
        self.game_window.click_on_image(GameImages.LANG_SELECT_ENG)

    def check_for_state_change(self) -> States:
        center = self.game_window.look_for_image(GameImages.TITLE_NEW_GAME)
        if center[0] != -1:
            return States.STARTING_NEW_GAME
        else:
            return States.HANDLING_EVENT
        

class StartingNewGameState(BaseState):
    def __init__(self, game_window: GameWindow):
        super().__init__(game_window)

    def state_actions(self):
        self.game_window.click_on_image(GameImages.TITLE_NEW_GAME)
        center = self.game_window.wait_for_image(GameImages.TITLE_OVERRIDE_SAVE, timeout=1)
        if center[0] != -1:
            self.game_window.click_on_image(GameImages.TITLE_CONFIRM_OVERRIDE)
            self.game_window.wait_for_image(GameImages.SHIP_SEL_EASY)
        self.game_window.click_on_image(GameImages.SHIP_SEL_EASY)
        self.game_window.click_on_image(GameImages.SHIP_SEL_START)
    
    def check_for_state_change(self) -> States:
        title_found, _ = self.game_window.look_for_image(GameImages.TITLE_NEW_GAME)
        confirm_found, _ = self.game_window.look_for_image(GameImages.TITLE_CONFIRM_OVERRIDE)
        ship_select_found, _ = self.game_window.look_for_image(GameImages.SHIP_SEL_START)
        if title_found or confirm_found or ship_select_found:
            return States.STARTING_NEW_GAME
        else:
            return States.HANDLING_EVENT
        

class Cura():
    def __init__(self):
        # Setup variables and states
        self.state = States.IDLE
        self.game_window = GameWindow()
        self.state_map = {
            States.IDLE: IdleState(self.game_window),
            States.WAITING_FOR_GAME_TO_LOAD: WaitingForGameToLoadState(self.game_window)
        }
        # Actually play the game
        self.game_window.launch_ftl()
        self.play_game()

    def play_game(self):
        self.state = States.WAITING_FOR_GAME_TO_LOAD
        while True:
            self.state = self.state_map[self.state].run()





if __name__ == "__main__":
    cura = Cura()
