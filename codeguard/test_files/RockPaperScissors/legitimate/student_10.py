# Student 10 - State Machine Pattern
"""
Rock Paper Scissors using explicit state machine.
Clear state transitions for game flow control.
"""

import random

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_VIEWING = "viewing"
STATE_RESETTING = "resetting"
STATE_EXIT = "exit"

def transition_from_menu(scores):
    """Handle menu state and transition."""
    print("\n*** MAIN MENU ***")
    print("1. Play Game")
    print("2. View Score")
    print("3. Reset Score")
    print("4. Exit")

    choice = input("\nSelect: ").strip()

    state_map = {
        '1': STATE_PLAYING,
        '2': STATE_VIEWING,
        '3': STATE_RESETTING,
        '4': STATE_EXIT
    }

    return state_map.get(choice, STATE_MENU)

def transition_from_playing(scores):
    """Handle playing state and transition."""
    print("\n>>> PLAY ROUND <<<")

    moves = ['rock', 'paper', 'scissors']

    # Get player move
    player = None
    while player not in moves:
        player = input("Enter rock, paper, or scissors: ").lower().strip()
        if player not in moves:
            print("Invalid move!")

    # Computer move
    computer = random.choice(moves)

    print(f"\nPlayer: {player}")
    print(f"Computer: {computer}")

    # Determine winner
    if player == computer:
        print("RESULT: Tie!")
        scores['ties'] += 1
    elif (player == 'rock' and computer == 'scissors') or \
         (player == 'paper' and computer == 'rock') or \
         (player == 'scissors' and computer == 'paper'):
        print("RESULT: You win!")
        scores['player'] += 1
    else:
        print("RESULT: Computer wins!")
        scores['computer'] += 1

    input("\nPress Enter to continue...")
    return STATE_MENU

def transition_from_viewing(scores):
    """Handle viewing state and transition."""
    print("\n*** SCOREBOARD ***")
    print(f"Player:   {scores['player']} wins")
    print(f"Computer: {scores['computer']} wins")
    print(f"Ties:     {scores['ties']}")
    print(f"Total:    {sum(scores.values())} games")

    input("\nPress Enter to return to menu...")
    return STATE_MENU

def transition_from_resetting(scores):
    """Handle resetting state and transition."""
    print("\n*** RESET SCORES ***")
    confirm = input("Are you sure? (yes/no): ").lower().strip()

    if confirm == 'yes':
        scores['player'] = 0
        scores['computer'] = 0
        scores['ties'] = 0
        print("Scores have been reset!")
    else:
        print("Reset cancelled.")

    input("\nPress Enter to continue...")
    return STATE_MENU

def run_state_machine():
    """Execute state machine game loop."""
    print("=== Rock Paper Scissors State Machine ===\n")

    # Initialize scores
    scores = {
        'player': 0,
        'computer': 0,
        'ties': 0
    }

    # Initial state
    current_state = STATE_MENU

    # State machine loop
    while current_state != STATE_EXIT:

        if current_state == STATE_MENU:
            current_state = transition_from_menu(scores)

        elif current_state == STATE_PLAYING:
            current_state = transition_from_playing(scores)

        elif current_state == STATE_VIEWING:
            current_state = transition_from_viewing(scores)

        elif current_state == STATE_RESETTING:
            current_state = transition_from_resetting(scores)

    # Exit state reached
    print("\n=== GAME OVER ===")
    print(f"Final Score - You: {scores['player']}, Computer: {scores['computer']}, Ties: {scores['ties']}")
    print("Thanks for playing!")

if __name__ == "__main__":
    run_state_machine()
