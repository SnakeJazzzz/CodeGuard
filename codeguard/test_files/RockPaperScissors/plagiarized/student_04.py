# Student 4 - Advanced Implementation
"""
Rock Paper Scissors with mixed programming approaches.
Uses class for score management and index-based game logic.
"""

import random

class ScoreTracker:
    """Simple class to track game scores."""
    def __init__(self):
        self.player = 0
        self.computer = 0
        self.ties = 0

    def reset(self):
        self.player = 0
        self.computer = 0
        self.ties = 0

    def display(self):
        print("\n=== Current Score ===")
        print(f"Player Wins: {self.player}")
        print(f"Computer Wins: {self.computer}")
        print(f"Ties: {self.ties}")
        print(f"Total Games: {self.player + self.computer + self.ties}")

# Global score object
score = ScoreTracker()

def main_menu():
    """Display main menu and get user choice."""
    print("\n=== Rock Paper Scissors ===")
    print("1. Play Game")
    print("2. View Score")
    print("3. Reset Score")
    print("4. Exit")

    while True:
        choice = input("\nEnter your choice (1-4): ")
        if choice in ['1', '2', '3', '4']:
            return choice
        else:
            print("Invalid choice. Please enter 1-4.")

def play_game():
    """Play using index-based logic with modulo."""
    global score

    choices = ['rock', 'paper', 'scissors']

    print("\n--- New Round ---")
    player_choice = input("Enter rock, paper, or scissors: ").lower()

    while player_choice not in choices:
        print("Invalid choice!")
        player_choice = input("Enter rock, paper, or scissors: ").lower()

    computer_choice = random.choice(choices)
    print(f"Computer chose: {computer_choice}")

    # Convert to indices
    player_idx = choices.index(player_choice)
    computer_idx = choices.index(computer_choice)

    # Use modulo math to determine winner
    # (player - computer) % 3: 0=tie, 1=player wins, 2=computer wins
    result = (player_idx - computer_idx) % 3

    if result == 0:
        print("It's a tie!")
        score.ties += 1
    elif result == 1:
        print("You win this round!")
        score.player += 1
    else:
        print("Computer wins this round!")
        score.computer += 1

def reset_score():
    """Reset all scores to zero."""
    global score

    confirm = input("\nAre you sure you want to reset? (yes/no): ").lower()
    if confirm == 'yes':
        score.reset()
        print("Score reset successfully!")
    else:
        print("Reset cancelled.")

if __name__ == "__main__":
    print("Welcome to Rock Paper Scissors!")

    while True:
        choice = main_menu()

        if choice == '1':
            play_game()
        elif choice == '2':
            score.display()
        elif choice == '3':
            reset_score()
        elif choice == '4':
            print("\nThanks for playing! Goodbye!")
            break
