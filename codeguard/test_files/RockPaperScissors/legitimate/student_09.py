# Student 9 - Functional Programming Style
"""
Rock Paper Scissors using functional programming principles.
Pure functions with immutable data structures.
"""

import random
from typing import Tuple, Dict

def create_initial_state() -> Dict:
    """Create initial game state."""
    return {
        'player_wins': 0,
        'computer_wins': 0,
        'ties': 0
    }

def get_valid_move() -> str:
    """Pure input function with validation."""
    moves = ('rock', 'paper', 'scissors')
    while True:
        choice = input("Your move (rock/paper/scissors): ").strip().lower()
        if choice in moves:
            return choice
        print("Invalid! Choose rock, paper, or scissors.")

def determine_winner(player: str, computer: str) -> str:
    """Pure function to determine round winner."""
    if player == computer:
        return 'tie'

    beats = {
        ('rock', 'scissors'): 'player',
        ('scissors', 'paper'): 'player',
        ('paper', 'rock'): 'player',
        ('scissors', 'rock'): 'computer',
        ('paper', 'scissors'): 'computer',
        ('rock', 'paper'): 'computer'
    }

    return beats[(player, computer)]

def update_score(state: Dict, winner: str) -> Dict:
    """Pure function returning new state (immutable update)."""
    new_state = state.copy()

    if winner == 'player':
        new_state['player_wins'] += 1
    elif winner == 'computer':
        new_state['computer_wins'] += 1
    else:
        new_state['ties'] += 1

    return new_state

def play_single_round(state: Dict) -> Dict:
    """Play one round and return new state."""
    print("\n--- Round Start ---")

    player_move = get_valid_move()
    computer_move = random.choice(['rock', 'paper', 'scissors'])

    print(f"Player chose: {player_move}")
    print(f"Computer chose: {computer_move}")

    winner = determine_winner(player_move, computer_move)

    outcome_messages = {
        'player': "You win this round!",
        'computer': "Computer wins this round!",
        'tie': "It's a tie!"
    }

    print(outcome_messages[winner])

    return update_score(state, winner)

def display_statistics(state: Dict) -> None:
    """Display current statistics (side effect isolated)."""
    print("\n" + "="*35)
    print("GAME STATISTICS")
    print("="*35)
    print(f"Player Wins:   {state['player_wins']}")
    print(f"Computer Wins: {state['computer_wins']}")
    print(f"Ties:          {state['ties']}")

    total = sum(state.values())
    print(f"Total Games:   {total}")

    if total > 0:
        ratio = state['player_wins'] / total
        print(f"Win Ratio:     {ratio:.2%}")

def reset_state_with_confirmation(state: Dict) -> Dict:
    """Reset state if user confirms."""
    response = input("\nReset all scores? (yes/no): ").strip().lower()

    if response == 'yes':
        print("Scores reset!")
        return create_initial_state()
    else:
        print("Reset cancelled.")
        return state

def show_menu() -> str:
    """Display menu and get choice."""
    print("\n" + "-"*35)
    print("MENU")
    print("-"*35)
    print("1) Play Round")
    print("2) View Statistics")
    print("3) Reset Scores")
    print("4) Exit")

    return input("\nChoice: ").strip()

def game_loop() -> None:
    """Main game loop using functional approach."""
    print("Welcome to Functional Rock Paper Scissors!\n")

    state = create_initial_state()

    while True:
        choice = show_menu()

        if choice == '1':
            state = play_single_round(state)

        elif choice == '2':
            display_statistics(state)

        elif choice == '3':
            state = reset_state_with_confirmation(state)

        elif choice == '4':
            print("\nFinal Statistics:")
            display_statistics(state)
            print("\nThanks for playing!")
            break

        else:
            print("Invalid choice! Please enter 1-4.")

if __name__ == "__main__":
    game_loop()
