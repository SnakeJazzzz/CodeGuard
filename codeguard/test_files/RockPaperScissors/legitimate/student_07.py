# Student 7 - Full OOP with Game Class
"""
Rock Paper Scissors using Object-Oriented Programming.
Encapsulates all game logic and state within a class.
"""

import random

class RockPaperScissors:
    """Complete RPS game implementation using OOP principles."""

    def __init__(self):
        """Initialize game with score tracking."""
        self.player_wins = 0
        self.computer_wins = 0
        self.ties = 0
        self.options = ['rock', 'paper', 'scissors']

    def play_round(self):
        """Execute a single round of the game."""
        print("\n" + "-"*30)
        print("NEW ROUND")
        print("-"*30)

        player_choice = self._get_player_move()
        computer_choice = random.choice(self.options)

        print(f"\nPlayer: {player_choice}")
        print(f"Computer: {computer_choice}")

        self._evaluate_round(player_choice, computer_choice)

    def _get_player_move(self):
        """Private method to get validated player input."""
        while True:
            move = input(f"\nChoose {'/'.join(self.options)}: ").lower()
            if move in self.options:
                return move
            print("Invalid move! Try again.")

    def _evaluate_round(self, player, computer):
        """Private method to determine and record round outcome."""
        if player == computer:
            print("\nResult: TIE")
            self.ties += 1
        elif self._does_beat(player, computer):
            print("\nResult: PLAYER WINS")
            self.player_wins += 1
        else:
            print("\nResult: COMPUTER WINS")
            self.computer_wins += 1

    def _does_beat(self, choice1, choice2):
        """Check if choice1 beats choice2."""
        winning_combos = {
            'rock': 'scissors',
            'scissors': 'paper',
            'paper': 'rock'
        }
        return winning_combos[choice1] == choice2

    def display_score(self):
        """Show current game statistics."""
        print("\n" + "="*30)
        print("SCORE SUMMARY")
        print("="*30)
        print(f"Player Victories:   {self.player_wins}")
        print(f"Computer Victories: {self.computer_wins}")
        print(f"Tied Rounds:        {self.ties}")
        print(f"Total Rounds:       {self.total_rounds()}")
        print("="*30)

    def reset_score(self):
        """Reset all scores to initial state."""
        response = input("\nConfirm reset (type YES): ")
        if response == "YES":
            self.player_wins = 0
            self.computer_wins = 0
            self.ties = 0
            print("Score has been reset!")
        else:
            print("Reset cancelled.")

    def total_rounds(self):
        """Calculate total rounds played."""
        return self.player_wins + self.computer_wins + self.ties

    def run(self):
        """Main game loop."""
        print("\n" + "="*40)
        print("ROCK PAPER SCISSORS - OOP Edition")
        print("="*40)

        while True:
            print("\n[1] Play Round")
            print("[2] View Score")
            print("[3] Reset Score")
            print("[4] Exit Game")

            choice = input("\nEnter choice: ").strip()

            if choice == '1':
                self.play_round()
            elif choice == '2':
                self.display_score()
            elif choice == '3':
                self.reset_score()
            elif choice == '4':
                print("\nThank you for playing!")
                self.display_score()
                break
            else:
                print("Invalid choice! Please enter 1-4.")

if __name__ == "__main__":
    game = RockPaperScissors()
    game.run()
