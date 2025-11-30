# Student 2 - Menu-Driven RPS Game
"""
Rock Paper Scissors implementation with interactive menu.
This program lets users play against the computer and tracks scores.
"""

import random

# Score tracking variables
user_points = 0
ai_wins = 0
draw_count = 0

def show_options():
    """Shows the menu options to the user and returns their selection."""
    # I created this function to display all available menu options
    # and make sure the user enters a valid choice
    print("\n=== Rock Paper Scissors ===")
    print("1. Play Game")
    print("2. View Score")
    print("3. Reset Score")
    print("4. Exit")

    # Keep asking until we get a valid input
    while True:
        user_input = input("\nEnter your choice (1-4): ")
        if user_input in ['1', '2', '3', '4']:
            return user_input
        else:
            # Tell the user their input was wrong
            print("Invalid choice. Please enter 1-4.")

def start_round():
    """Starts a new round of the game."""
    # Using global so we can modify the score variables
    global user_points, ai_wins, draw_count

    # List of valid game choices
    options = ['rock', 'paper', 'scissors']

    print("\n--- New Round ---")
    # Get the player's choice
    player_move = input("Enter rock, paper, or scissors: ").lower()

    # Validate the input
    while player_move not in options:
        print("Invalid choice!")
        player_move = input("Enter rock, paper, or scissors: ").lower()

    # Computer makes a random choice
    ai_move = random.choice(options)
    print(f"Computer chose: {ai_move}")

    # Determine the winner
    # First check if it's a tie
    if player_move == ai_move:
        print("It's a tie!")
        draw_count += 1
    # Check if player wins
    elif (player_move == 'rock' and ai_move == 'scissors') or \
         (player_move == 'paper' and ai_move == 'rock') or \
         (player_move == 'scissors' and ai_move == 'paper'):
        print("You win this round!")
        user_points += 1
    # Otherwise computer wins
    else:
        print("Computer wins this round!")
        ai_wins += 1

def show_current_score():
    """Displays the current game statistics."""
    # This function prints out all the score information
    print("\n=== Current Score ===")
    print(f"Player Wins: {user_points}")
    print(f"Computer Wins: {ai_wins}")
    print(f"Ties: {draw_count}")
    # Calculate and show total games played
    print(f"Total Games: {user_points + ai_wins + draw_count}")

def clear_scores():
    """Resets all scores back to zero."""
    # Using global to modify the score variables
    global user_points, ai_wins, draw_count

    # Ask for confirmation before resetting
    verify = input("\nAre you sure you want to reset? (yes/no): ").lower()
    if verify == 'yes':
        # Reset everything to 0
        user_points = 0
        ai_wins = 0
        draw_count = 0
        print("Score reset successfully!")
    else:
        # User changed their mind
        print("Reset cancelled.")

if __name__ == "__main__":
    # Welcome message
    print("Welcome to Rock Paper Scissors!")

    # Main game loop
    while True:
        # Get menu selection
        menu_choice = show_options()

        # Execute based on choice
        if menu_choice == '1':
            start_round()
        elif menu_choice == '2':
            show_current_score()
        elif menu_choice == '3':
            clear_scores()
        elif menu_choice == '4':
            # Exit the program
            print("\nThanks for playing! Goodbye!")
            break
