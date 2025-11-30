# Student 19 - Recursive Menu
"""
Rock Paper Scissors using recursion for game flow.
Demonstrates tail recursion pattern for menu loop.
"""

import random
import sys

# Increase recursion limit for deep menu navigation
sys.setrecursionlimit(5000)

def get_validated_choice():
    """Get validated move from player."""
    valid = ['rock', 'paper', 'scissors']
    choice = input("\nRock, Paper, or Scissors? ").lower().strip()

    if choice in valid:
        return choice
    else:
        print("Invalid choice!")
        return get_validated_choice()  # Recursive call

def determine_winner(player, computer):
    """Determine the winner."""
    if player == computer:
        return 'tie'

    wins = {
        'rock': 'scissors',
        'scissors': 'paper',
        'paper': 'rock'
    }

    return 'player' if wins[player] == computer else 'computer'

def play_round_recursive(scores):
    """Play a round recursively."""
    print("\n" + "-"*40)
    print("ROUND")
    print("-"*40)

    player_move = get_validated_choice()
    computer_move = random.choice(['rock', 'paper', 'scissors'])

    print(f"\nYou: {player_move}")
    print(f"Computer: {computer_move}")

    winner = determine_winner(player_move, computer_move)

    if winner == 'tie':
        print("Result: TIE!")
        scores['ties'] += 1
    elif winner == 'player':
        print("Result: YOU WIN!")
        scores['player'] += 1
    else:
        print("Result: COMPUTER WINS!")
        scores['computer'] += 1

    input("\nPress Enter to continue...")

def show_scores_recursive(scores):
    """Show scores recursively."""
    print("\n" + "="*40)
    print("SCORES")
    print("="*40)
    print(f"Your Wins:     {scores['player']}")
    print(f"Computer Wins: {scores['computer']}")
    print(f"Ties:          {scores['ties']}")

    total = sum(scores.values())
    print(f"Total Played:  {total}")

    if total > 0:
        percentage = (scores['player'] / total) * 100
        print(f"Win Percentage: {percentage:.1f}%")

    input("\nPress Enter to return...")

def reset_scores_recursive(scores):
    """Reset scores with recursive confirmation."""
    confirm = input("\nType 'yes' to reset: ").lower().strip()

    if confirm == 'yes':
        scores['player'] = 0
        scores['computer'] = 0
        scores['ties'] = 0
        print("Scores reset!")
    else:
        print("Not resetting.")

    input("\nPress Enter to continue...")

def menu_loop_recursive(scores):
    """
    Recursive menu loop (tail recursion).
    Base case: user chooses to exit.
    Recursive case: user chooses any other option.
    """
    print("\n" + "="*40)
    print("MAIN MENU")
    print("="*40)
    print("1) Play Round")
    print("2) View Scores")
    print("3) Reset Scores")
    print("4) Exit Game")

    choice = input("\nYour choice: ").strip()

    if choice == '1':
        play_round_recursive(scores)
        return menu_loop_recursive(scores)  # Tail recursion

    elif choice == '2':
        show_scores_recursive(scores)
        return menu_loop_recursive(scores)  # Tail recursion

    elif choice == '3':
        reset_scores_recursive(scores)
        return menu_loop_recursive(scores)  # Tail recursion

    elif choice == '4':
        # Base case - exit
        print("\n" + "="*40)
        print("FINAL SCORES")
        print("="*40)
        print(f"Player: {scores['player']}")
        print(f"Computer: {scores['computer']}")
        print(f"Ties: {scores['ties']}")
        print("\nThanks for playing!")
        return  # Base case - stop recursion

    else:
        print("\nInvalid choice! Choose 1-4.")
        return menu_loop_recursive(scores)  # Tail recursion

def main():
    """Main entry point."""
    print("="*40)
    print("Rock Paper Scissors - Recursive Edition")
    print("="*40)
    print("\nThis game uses recursive function calls!")

    scores = {
        'player': 0,
        'computer': 0,
        'ties': 0
    }

    # Start recursive menu loop
    menu_loop_recursive(scores)

if __name__ == "__main__":
    main()
