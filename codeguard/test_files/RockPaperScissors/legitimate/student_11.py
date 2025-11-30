# Student 11 - Rules Engine Approach
"""
Rock Paper Scissors with rules as data.
Separates rules definition from game engine logic.
"""

import random

# Rules defined as data structure
GAME_RULES = [
    {'winner': 'rock', 'loser': 'scissors', 'verb': 'crushes'},
    {'winner': 'scissors', 'loser': 'paper', 'verb': 'cuts'},
    {'winner': 'paper', 'loser': 'rock', 'verb': 'covers'}
]

def get_all_moves():
    """Extract all valid moves from rules."""
    moves = set()
    for rule in GAME_RULES:
        moves.add(rule['winner'])
        moves.add(rule['loser'])
    return sorted(list(moves))

def find_winning_rule(move1, move2):
    """Find rule where move1 beats move2."""
    for rule in GAME_RULES:
        if rule['winner'] == move1 and rule['loser'] == move2:
            return rule
    return None

def evaluate_game(player, computer):
    """Evaluate game using rules engine."""
    if player == computer:
        return {
            'winner': None,
            'message': "It's a tie!"
        }

    rule = find_winning_rule(player, computer)

    if rule:
        return {
            'winner': 'player',
            'message': f"{rule['winner'].capitalize()} {rule['verb']} {rule['loser']}. You win!"
        }
    else:
        rule = find_winning_rule(computer, player)
        return {
            'winner': 'computer',
            'message': f"{rule['winner'].capitalize()} {rule['verb']} {rule['loser']}. Computer wins!"
        }

def get_user_move(valid_moves):
    """Get and validate user move."""
    print(f"\nAvailable moves: {', '.join(valid_moves)}")

    while True:
        move = input("Your choice: ").lower().strip()
        if move in valid_moves:
            return move
        print(f"Invalid! Choose from: {', '.join(valid_moves)}")

def display_score_table(scores):
    """Display scores in table format."""
    print("\n" + "="*40)
    print(" "*15 + "SCORES")
    print("="*40)
    print(f"  Player Wins     : {scores['player']:3d}")
    print(f"  Computer Wins   : {scores['computer']:3d}")
    print(f"  Ties            : {scores['ties']:3d}")
    print("-"*40)
    print(f"  Total Games     : {sum(scores.values()):3d}")
    print("="*40)

def main_game():
    """Main game loop with rules engine."""
    print("Welcome to Rules Engine RPS!")
    print("\nThis game uses a configurable rules system.")

    valid_moves = get_all_moves()
    scores = {'player': 0, 'computer': 0, 'ties': 0}

    while True:
        print("\n" + "-"*40)
        print("MENU")
        print("-"*40)
        print("[P] Play")
        print("[S] Score")
        print("[R] Reset")
        print("[Q] Quit")

        action = input("\nAction: ").upper().strip()

        if action == 'P':
            print("\n--- NEW ROUND ---")
            player_move = get_user_move(valid_moves)
            computer_move = random.choice(valid_moves)

            print(f"\nYou chose: {player_move}")
            print(f"Computer chose: {computer_move}")

            result = evaluate_game(player_move, computer_move)
            print(f"\n{result['message']}")

            if result['winner'] == 'player':
                scores['player'] += 1
            elif result['winner'] == 'computer':
                scores['computer'] += 1
            else:
                scores['ties'] += 1

        elif action == 'S':
            display_score_table(scores)

        elif action == 'R':
            confirm = input("\nConfirm reset (type YES): ")
            if confirm == 'YES':
                scores = {'player': 0, 'computer': 0, 'ties': 0}
                print("Scores reset!")
            else:
                print("Cancelled.")

        elif action == 'Q':
            print("\nThanks for playing!")
            display_score_table(scores)
            break

        else:
            print("Invalid action!")

if __name__ == "__main__":
    main_game()
