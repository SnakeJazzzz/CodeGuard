# Student 16 - Tuple-Based Approach
"""
Rock Paper Scissors using tuples and set operations.
Demonstrates tuple comparisons for game logic.
"""

import random

# Valid moves as a tuple (immutable)
MOVES = ('rock', 'paper', 'scissors')

# Winning combinations as set of tuples
WINNING_COMBOS = {
    ('rock', 'scissors'),
    ('scissors', 'paper'),
    ('paper', 'rock')
}

def validate_move(move):
    """Check if move is valid using tuple membership."""
    return move in MOVES

def get_player_input():
    """Get validated player input."""
    print(f"\nValid moves: {' | '.join(MOVES)}")

    while True:
        move = input("Your choice: ").lower().strip()
        if validate_move(move):
            return move
        print(f"Invalid! Choose from {MOVES}")

def evaluate_round(player, computer):
    """
    Evaluate round using tuple comparison and set lookup.
    Returns: (outcome, message) tuple
    """
    combo = (player, computer)

    if player == computer:
        return ('tie', f"Both chose {player}")

    if combo in WINNING_COMBOS:
        return ('player', f"{player.capitalize()} beats {computer}")

    return ('computer', f"{computer.capitalize()} beats {player}")

def update_scores(scores, outcome):
    """
    Update score tuple and return new tuple.
    scores: (player_wins, computer_wins, ties)
    """
    player_wins, computer_wins, ties = scores

    if outcome == 'player':
        return (player_wins + 1, computer_wins, ties)
    elif outcome == 'computer':
        return (player_wins, computer_wins + 1, ties)
    else:
        return (player_wins, computer_wins, ties + 1)

def format_scores(scores):
    """Format score tuple as string."""
    player_wins, computer_wins, ties = scores
    total = sum(scores)

    return f"""
{'='*40}
SCORE SUMMARY
{'='*40}
Player Wins:    {player_wins}
Computer Wins:  {computer_wins}
Ties:           {ties}
{'─'*40}
Total Games:    {total}
{'='*40}
"""

def play_game_round(scores):
    """Play one round and return updated scores."""
    print("\n" + "~"*40)
    print("ROUND START")
    print("~"*40)

    player_move = get_player_input()
    computer_move = random.choice(MOVES)

    print(f"\nYou:      {player_move}")
    print(f"Computer: {computer_move}")

    outcome, message = evaluate_round(player_move, computer_move)
    print(f"\n{message}")

    if outcome == 'tie':
        print("Result: TIE")
    elif outcome == 'player':
        print("Result: YOU WIN!")
    else:
        print("Result: COMPUTER WINS!")

    return update_scores(scores, outcome)

def main():
    """Main game using tuple-based state."""
    print("Rock Paper Scissors - Tuple Edition")
    print("="*40)

    # Score as tuple: (player_wins, computer_wins, ties)
    scores = (0, 0, 0)

    menu_options = ('Play', 'Score', 'Reset', 'Quit')

    while True:
        print("\n" + "="*40)
        print("MENU")
        print("="*40)

        for i, option in enumerate(menu_options, 1):
            print(f"{i}) {option}")

        choice = input("\nSelect (1-4): ").strip()

        if choice == '1':
            scores = play_game_round(scores)

        elif choice == '2':
            print(format_scores(scores))

        elif choice == '3':
            confirm = input("Reset? (y/n): ").lower()
            if confirm == 'y':
                scores = (0, 0, 0)
                print("Scores reset!")

        elif choice == '4':
            print("\nGame Over!")
            print(format_scores(scores))
            print("Thanks for playing!")
            break

        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
