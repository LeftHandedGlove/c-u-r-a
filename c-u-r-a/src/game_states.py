import enum
import abc
from game_window import GameWindow, GameImages, GameEvent


class States(enum.Enum):
    IDLE = 0
    WAITING_FOR_GAME_TO_LOAD = 1
    SELECTING_LANGUAGE = 2
    STARTING_NEW_GAME = 3
    HANDLING_EVENT = 4
    NODE_JUMP = 5


class BaseState:
    def __init__(self, game_window:GameWindow):
        self.game_window = game_window
        self.previous_state = States.IDLE

    def run(self, previous_state) -> States:
        self.previous_state = previous_state
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
        found, _ = self.game_window.look_for_image(GameImages.LANG_SELECT_ENG)
        if found:
            return States.SELECTING_LANGUAGE
        else:
            return States.WAITING_FOR_GAME_TO_LOAD
        

class SelectingLanguageState(BaseState):
    def __init__(self, game_window: GameWindow):
        super().__init__(game_window)

    def state_actions(self):
        self.game_window.click_on_image(GameImages.LANG_SELECT_ENG)

    def check_for_state_change(self) -> States:
        found, _ = self.game_window.look_for_image(GameImages.TITLE_NEW_GAME)
        if found:
            return States.STARTING_NEW_GAME
        else:
            return States.SELECTING_LANGUAGE
        

class StartingNewGameState(BaseState):
    def __init__(self, game_window: GameWindow):
        super().__init__(game_window)

    def state_actions(self):
        self.game_window.click_on_image(GameImages.TITLE_NEW_GAME)
        found, _ = self.game_window.wait_for_image(GameImages.TITLE_OVERRIDE_SAVE, timeout=1)
        if found:
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
        

class HandlingEvent(BaseState):
    def __init__(self, game_window: GameWindow):
        super().__init__(game_window)
        self.node_events = []
        self.event_memory = {}

    def state_actions(self):
        if self.previous_state == States.NODE_JUMP:
            self.node_events.clear()
        game_event = self.game_window.read_event_text()
        
    def check_for_state_change(self) -> States:
        return States.IDLE
    
    def fill_out_event_from_memory(self, event:GameEvent) -> GameEvent:
        if event.pre_options_text in self.event_memory.keys():
            pass
        else:
            self.event_memory[event.pre_options_text] = event
        return event
