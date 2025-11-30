# Student 18 - Matrix-Based Winner Determination
"""
Rock Paper Scissors using outcome matrix.
Uses 2D array for O(1) winner lookup.
"""

import random

# Move indices
ROCK = 0
PAPER = 1
SCISSORS = 2

# Move names
MOVE_NAMES = ['rock', 'paper', 'scissors']

# Outcome matrix: outcome[player][computer]
# 0 = tie, 1 = player wins, -1 = computer wins
OUTCOME_MATRIX = [
    [0,  -1,  1],   # rock vs [rock, paper, scissors]
    [1,   0, -1],   # paper vs [rock, paper, scissors]
    [-1,  1,  0]    # scissors vs [rock, paper, scissors]
]

def get_move_index():
    """Get player move and convert to index."""
    print("\nSelect your move:")
    for i, name in enumerate(MOVE_NAMES):
        print(f"  {i+1}. {name.capitalize()}")

    while True:
        try:
            choice = int(input("\nEnter 1-3: "))
            if 1 <= choice <= 3:
                return choice - 1
        except ValueError:
            pass
        print("Invalid! Enter a number 1-3.")

def lookup_outcome(player_idx, computer_idx):
    """
    Look up outcome in matrix.
    Returns: (result_code, result_string)
    """
    outcome = OUTCOME_MATRIX[player_idx][computer_idx]

    outcome_map = {
        0: ('tie', 'TIE'),
        1: ('player', 'PLAYER WINS'),
        -1: ('computer', 'COMPUTER WINS')
    }

    return outcome_map[outcome]

def display_score_matrix(scores):
    """Display scores in matrix-like format."""
    print("\n" + "="*40)
    print(" "*10 + "SCOREBOARD")
    print("="*40)

    # Display as a simple table
    headers = ["Category", "Count"]
    print(f"{headers[0]:<20} {headers[1]:>10}")
    print("-"*40)

    score_labels = ['Player Wins', 'Computer Wins', 'Ties']
    score_keys = ['player', 'computer', 'ties']

    for label, key in zip(score_labels, score_keys):
        print(f"{label:<20} {scores[key]:>10}")

    print("-"*40)
    total = sum(scores.values())
    print(f"{'Total Games':<20} {total:>10}")
    print("="*40)

def play_round(scores):
    """Play one round using matrix lookup."""
    print("\n" + "~"*40)
    print("ROUND IN PROGRESS")
    print("~"*40)

    player_idx = get_move_index()
    computer_idx = random.randint(0, 2)

    player_name = MOVE_NAMES[player_idx]
    computer_name = MOVE_NAMES[computer_idx]

    print(f"\nYou selected:      {player_name.upper()}")
    print(f"Computer selected: {computer_name.upper()}")

    result_code, result_msg = lookup_outcome(player_idx, computer_idx)

    print(f"\nOutcome: {result_msg}")

    # Update scores
    if result_code == 'tie':
        scores['ties'] += 1
    elif result_code == 'player':
        scores['player'] += 1
    else:
        scores['computer'] += 1

def reset_scores(scores):
    """Reset all scores to zero."""
    print("\n" + "!"*40)
    print("RESET OPERATION")
    print("!"*40)

    confirm = input("Type RESET to confirm: ")

    if confirm == "RESET":
        scores['player'] = 0
        scores['computer'] = 0
        scores['ties'] = 0
        print("\nScores have been cleared!")
    else:
        print("\nReset cancelled.")

def main():
    """Main game loop with matrix-based logic."""
    print("="*40)
    print("Rock Paper Scissors - Matrix Edition")
    print("="*40)
    print("\nUsing outcome matrix for O(1) lookups!")

    scores = {
        'player': 0,
        'computer': 0,
        'ties': 0
    }

    while True:
        print("\n" + "="*40)
        print("MENU OPTIONS")
        print("="*40)
        print("[1] Play Game")
        print("[2] View Scores")
        print("[3] Reset Scores")
        print("[4] Exit")

        choice = input("\nSelection: ").strip()

        if choice == '1':
            play_round(scores)

        elif choice == '2':
            display_score_matrix(scores)

        elif choice == '3':
            reset_scores(scores)

        elif choice == '4':
            print("\n" + "="*40)
            print("GAME OVER")
            print("="*40)
            display_score_matrix(scores)
            print("\nThank you for playing!")
            break

        else:
            print("\nInvalid choice! Please enter 1-4.")

if __name__ == "__main__":
    main()
