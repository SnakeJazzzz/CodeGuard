# Student 17 - Command Pattern
"""
Rock Paper Scissors using Command design pattern.
Each menu action is encapsulated as a command object.
"""

import random
from abc import ABC, abstractmethod

class Command(ABC):
    """Abstract base class for commands."""

    @abstractmethod
    def execute(self, game_context):
        """Execute the command."""
        pass

class PlayCommand(Command):
    """Command to play a round."""

    def execute(self, game_context):
        """Play one round of RPS."""
        print("\n" + "-"*40)
        print("PLAYING ROUND")
        print("-"*40)

        moves = ['rock', 'paper', 'scissors']

        # Get player move
        player_move = None
        while player_move not in moves:
            player_move = input("\nChoose rock/paper/scissors: ").lower()
            if player_move not in moves:
                print("Invalid!")

        computer_move = random.choice(moves)

        print(f"\nPlayer: {player_move}")
        print(f"Computer: {computer_move}")

        # Determine winner
        if player_move == computer_move:
            print(">> TIE")
            game_context['ties'] += 1
        elif self._wins(player_move, computer_move):
            print(">> PLAYER WINS")
            game_context['player'] += 1
        else:
            print(">> COMPUTER WINS")
            game_context['computer'] += 1

    def _wins(self, move1, move2):
        """Check if move1 beats move2."""
        wins = {
            'rock': 'scissors',
            'scissors': 'paper',
            'paper': 'rock'
        }
        return wins[move1] == move2

class ScoreCommand(Command):
    """Command to display score."""

    def execute(self, game_context):
        """Display current scores."""
        print("\n" + "="*40)
        print("SCOREBOARD")
        print("="*40)
        print(f"Player:   {game_context['player']} wins")
        print(f"Computer: {game_context['computer']} wins")
        print(f"Ties:     {game_context['ties']}")

        total = sum(game_context.values())
        print(f"\nTotal:    {total} games")

        if total > 0:
            rate = (game_context['player'] / total) * 100
            print(f"Win Rate: {rate:.1f}%")

class ResetCommand(Command):
    """Command to reset scores."""

    def execute(self, game_context):
        """Reset all scores."""
        print("\n" + "!"*40)
        response = input("Confirm reset (YES/no): ")

        if response == "YES":
            game_context['player'] = 0
            game_context['computer'] = 0
            game_context['ties'] = 0
            print("All scores reset to zero!")
        else:
            print("Reset aborted.")

class ExitCommand(Command):
    """Command to exit game."""

    def execute(self, game_context):
        """Exit the game."""
        print("\nExiting game...")
        return True  # Signal to exit

class CommandInvoker:
    """Invoker that executes commands."""

    def __init__(self):
        """Initialize command registry."""
        self.commands = {
            '1': PlayCommand(),
            '2': ScoreCommand(),
            '3': ResetCommand(),
            '4': ExitCommand()
        }

    def invoke(self, command_key, game_context):
        """Execute command by key."""
        if command_key in self.commands:
            command = self.commands[command_key]
            return command.execute(game_context)
        else:
            print("Unknown command!")
            return False

def display_menu():
    """Display the main menu."""
    print("\n" + "="*40)
    print("MAIN MENU")
    print("="*40)
    print("1) Play Round")
    print("2) View Score")
    print("3) Reset Score")
    print("4) Exit")
    print("="*40)

def main():
    """Main game loop using command pattern."""
    print("Rock Paper Scissors - Command Pattern Edition\n")

    # Game context (shared state)
    game_context = {
        'player': 0,
        'computer': 0,
        'ties': 0
    }

    invoker = CommandInvoker()

    # Game loop
    while True:
        display_menu()
        choice = input("\nEnter command (1-4): ").strip()

        should_exit = invoker.invoke(choice, game_context)

        if should_exit:
            print("\nFinal Score:")
            invoker.invoke('2', game_context)
            print("\nGoodbye!")
            break

if __name__ == "__main__":
    main()
