# Student 15 - Match/Case Pattern (Python 3.10+)
"""
Rock Paper Scissors using match/case pattern matching.
Requires Python 3.10 or higher for structural pattern matching.
"""

import random
import sys

def get_player_move():
    """Get player's move with validation."""
    move = input("\nEnter rock, paper, or scissors: ").lower().strip()

    match move:
        case "rock" | "paper" | "scissors":
            return move
        case _:
            print("Invalid move!")
            return get_player_move()

def determine_outcome(player, computer):
    """Determine game outcome using match/case."""
    match (player, computer):
        case (p, c) if p == c:
            return "tie"
        case ("rock", "scissors") | ("scissors", "paper") | ("paper", "rock"):
            return "player"
        case _:
            return "computer"

def display_result(outcome):
    """Display result using pattern matching."""
    match outcome:
        case "tie":
            print(">> It's a TIE!")
            return "ties"
        case "player":
            print(">> YOU WIN!")
            return "player"
        case "computer":
            print(">> COMPUTER WINS!")
            return "computer"

def play_round(scores):
    """Execute one round of the game."""
    print("\n" + "-"*40)
    print("NEW ROUND")
    print("-"*40)

    player_move = get_player_move()
    computer_move = random.choice(["rock", "paper", "scissors"])

    print(f"\nYou chose: {player_move}")
    print(f"Computer chose: {computer_move}")

    outcome = determine_outcome(player_move, computer_move)
    score_key = display_result(outcome)
    scores[score_key] += 1

def show_scores(scores):
    """Display scores using match for formatting."""
    print("\n" + "="*40)
    print("SCOREBOARD")
    print("="*40)

    for category, count in scores.items():
        match category:
            case "player":
                print(f"Player Wins:   {count}")
            case "computer":
                print(f"Computer Wins: {count}")
            case "ties":
                print(f"Ties:          {count}")

    total = sum(scores.values())
    print("-"*40)
    print(f"Total Games:   {total}")

    if total > 0:
        win_pct = (scores["player"] / total) * 100
        print(f"Win Rate:      {win_pct:.1f}%")

def reset_scores(scores):
    """Reset scores with confirmation."""
    response = input("\nReset all scores? (yes/no): ").lower()

    match response:
        case "yes":
            for key in scores:
                scores[key] = 0
            print("Scores reset!")
        case _:
            print("Reset cancelled.")

def process_menu_choice(choice, scores):
    """Process menu selection using match/case."""
    match choice:
        case "1":
            play_round(scores)
            return True
        case "2":
            show_scores(scores)
            return True
        case "3":
            reset_scores(scores)
            return True
        case "4":
            return False
        case _:
            print("Invalid choice! Enter 1-4.")
            return True

def main():
    """Main game loop using pattern matching."""
    # Check Python version
    if sys.version_info < (3, 10):
        print("This program requires Python 3.10 or higher for match/case support.")
        return

    print("Rock Paper Scissors - Pattern Matching Edition")
    print("="*40)

    scores = {
        "player": 0,
        "computer": 0,
        "ties": 0
    }

    running = True

    while running:
        print("\n" + "="*40)
        print("MENU")
        print("="*40)
        print("1) Play Round")
        print("2) View Score")
        print("3) Reset Score")
        print("4) Exit")

        choice = input("\nYour choice: ").strip()
        running = process_menu_choice(choice, scores)

    print("\nFinal Statistics:")
    show_scores(scores)
    print("\nThanks for playing!")

if __name__ == "__main__":
    main()
