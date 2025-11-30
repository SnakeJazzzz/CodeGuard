# Student 1 - Basic Procedural Implementation
"""
Rock Paper Scissors game with menu system.
Implements basic procedural approach with global score tracking.
"""

import random

# Global score tracking
player_score = 0
computer_score = 0
ties = 0

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
    """Play one round of rock paper scissors."""
    global player_score, computer_score, ties

    choices = ['rock', 'paper', 'scissors']

    print("\n--- New Round ---")
    player_choice = input("Enter rock, paper, or scissors: ").lower()

    while player_choice not in choices:
        print("Invalid choice!")
        player_choice = input("Enter rock, paper, or scissors: ").lower()

    computer_choice = random.choice(choices)
    print(f"Computer chose: {computer_choice}")

    if player_choice == computer_choice:
        print("It's a tie!")
        ties += 1
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
         (player_choice == 'paper' and computer_choice == 'rock') or \
         (player_choice == 'scissors' and computer_choice == 'paper'):
        print("You win this round!")
        player_score += 1
    else:
        print("Computer wins this round!")
        computer_score += 1

def display_score():
    """Show current score."""
    print("\n=== Current Score ===")
    print(f"Player Wins: {player_score}")
    print(f"Computer Wins: {computer_score}")
    print(f"Ties: {ties}")
    print(f"Total Games: {player_score + computer_score + ties}")

def reset_score():
    """Reset all scores to zero."""
    global player_score, computer_score, ties

    confirm = input("\nAre you sure you want to reset? (yes/no): ").lower()
    if confirm == 'yes':
        player_score = 0
        computer_score = 0
        ties = 0
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
            display_score()
        elif choice == '3':
            reset_score()
        elif choice == '4':
            print("\nThanks for playing! Goodbye!")
            break
