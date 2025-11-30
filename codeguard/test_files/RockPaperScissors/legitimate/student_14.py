# Student 14 - Nested Functions/Closures
"""
Rock Paper Scissors using closures and nested functions.
Demonstrates scope management with encapsulated functions.
"""

import random

def create_game():
    """Factory function that creates a game with closures."""

    # Enclosed variables (closure)
    player_score = 0
    computer_score = 0
    ties = 0
    moves = ['rock', 'paper', 'scissors']

    def get_move():
        """Nested function to get player move."""
        while True:
            move = input("\nYour move (rock/paper/scissors): ").lower()
            if move in moves:
                return move
            print("Invalid move!")

    def check_winner(p_move, c_move):
        """Nested function to determine winner."""
        if p_move == c_move:
            return 'tie'

        winning = {
            ('rock', 'scissors'),
            ('scissors', 'paper'),
            ('paper', 'rock')
        }

        if (p_move, c_move) in winning:
            return 'player'
        else:
            return 'computer'

    def play():
        """Nested function to play one round."""
        nonlocal player_score, computer_score, ties

        print("\n--- Round Start ---")

        p_move = get_move()
        c_move = random.choice(moves)

        print(f"You: {p_move}")
        print(f"Computer: {c_move}")

        result = check_winner(p_move, c_move)

        if result == 'tie':
            print("Result: TIE")
            ties += 1
        elif result == 'player':
            print("Result: YOU WIN")
            player_score += 1
        else:
            print("Result: COMPUTER WINS")
            computer_score += 1

    def show_score():
        """Nested function to display score."""
        print("\n*** SCOREBOARD ***")
        print(f"Your wins: {player_score}")
        print(f"Computer wins: {computer_score}")
        print(f"Ties: {ties}")
        print(f"Total: {player_score + computer_score + ties}")

    def reset():
        """Nested function to reset scores."""
        nonlocal player_score, computer_score, ties

        if input("Reset scores? (yes/no): ").lower() == 'yes':
            player_score = 0
            computer_score = 0
            ties = 0
            print("Scores reset!")
        else:
            print("Cancelled.")

    def run():
        """Nested function for main loop."""
        print("Welcome to Closure-Based RPS!\n")

        while True:
            print("\n" + "="*30)
            print("1. Play")
            print("2. Score")
            print("3. Reset")
            print("4. Exit")

            choice = input("\nChoice: ")

            if choice == '1':
                play()
            elif choice == '2':
                show_score()
            elif choice == '3':
                reset()
            elif choice == '4':
                print("\nFinal Score:")
                show_score()
                print("\nThanks for playing!")
                break
            else:
                print("Invalid choice!")

    # Return the run function (closure over all nested functions and variables)
    return run

if __name__ == "__main__":
    # Create game instance and run
    game = create_game()
    game()
