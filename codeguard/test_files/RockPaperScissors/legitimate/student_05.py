# Student 5 - Dictionary-Based Win Conditions
"""
Rock Paper Scissors using comprehensive dictionary approach.
All game logic driven by dictionary lookups for clarity.
"""

import random

# Dictionary mapping what each choice beats
BEATS = {
    'rock': 'scissors',
    'scissors': 'paper',
    'paper': 'rock'
}

def get_player_choice():
    """Get and validate player's move."""
    valid_choices = list(BEATS.keys())
    while True:
        choice = input("Choose rock, paper, or scissors: ").lower().strip()
        if choice in valid_choices:
            return choice
        print(f"Please enter one of: {', '.join(valid_choices)}")

def determine_winner(player, computer):
    """Determine round winner using dictionary lookup."""
    if player == computer:
        return "tie"
    elif BEATS[player] == computer:
        return "player"
    else:
        return "computer"

def run_game():
    """Main game loop with dictionary-driven menu."""
    stats = {'player': 0, 'computer': 0, 'tie': 0}

    menu_actions = {
        '1': 'play',
        '2': 'score',
        '3': 'reset',
        '4': 'quit'
    }

    print("Welcome to Rock, Paper, Scissors!\n")

    while True:
        print("\n--- MENU ---")
        print("1) Play Round")
        print("2) Show Score")
        print("3) Reset Score")
        print("4) Quit")

        action = input("\nSelect option: ").strip()

        if action not in menu_actions:
            print("Invalid option!")
            continue

        command = menu_actions[action]

        if command == 'play':
            player_move = get_player_choice()
            computer_move = random.choice(list(BEATS.keys()))

            print(f"\nYou chose: {player_move}")
            print(f"Computer chose: {computer_move}")

            winner = determine_winner(player_move, computer_move)

            if winner == "tie":
                print("It's a draw!")
                stats['tie'] += 1
            elif winner == "player":
                print("You won!")
                stats['player'] += 1
            else:
                print("Computer won!")
                stats['computer'] += 1

        elif command == 'score':
            print("\n--- SCOREBOARD ---")
            print(f"Your wins: {stats['player']}")
            print(f"Computer wins: {stats['computer']}")
            print(f"Draws: {stats['tie']}")
            total = sum(stats.values())
            print(f"Total rounds: {total}")

        elif command == 'reset':
            if input("Reset scores? (y/n): ").lower() == 'y':
                stats = {'player': 0, 'computer': 0, 'tie': 0}
                print("Scores reset!")

        elif command == 'quit':
            print("\nFinal Score:")
            print(f"You: {stats['player']} | Computer: {stats['computer']} | Draws: {stats['tie']}")
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    run_game()
