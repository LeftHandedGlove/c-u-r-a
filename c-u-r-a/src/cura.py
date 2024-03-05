from game_window import GameWindow
from game_states import (
    States,
    IdleState,
    WaitingForGameToLoadState,
    SelectingLanguageState,
    StartingNewGameState,
)
        

class Cura():
    def __init__(self):
        # Setup variables and states
        self.state = States.IDLE
        self.game_window = GameWindow()
        self.state_map = {
            States.IDLE: IdleState(self.game_window),
            States.WAITING_FOR_GAME_TO_LOAD: WaitingForGameToLoadState(self.game_window),
            States.SELECTING_LANGUAGE: SelectingLanguageState(self.game_window),
            States.STARTING_NEW_GAME: StartingNewGameState(self.game_window)
        }
        # Actually play the game
        self.game_window.launch_ftl()
        self.play_game()

    def play_game(self):
        self.state = States.WAITING_FOR_GAME_TO_LOAD
        while True:
            # Try to run the current state
            try:
                previous_state = self.state
                self.state = self.state_map[self.state].run(previous_state)
            except KeyError:
                print(f"Unknown state {self.state}, switching to IDLE state")
                self.state = States.IDLE
            # Report changes
            if previous_state != self.state:
                print(f"Switching from {previous_state} -> {self.state}")
            

if __name__ == "__main__":
    cura = Cura()
