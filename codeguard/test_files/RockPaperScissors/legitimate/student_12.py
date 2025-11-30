# Student 12 - Lambda-Heavy Implementation
"""
Rock Paper Scissors using lambdas and functional constructs.
Demonstrates concise lambda-based approach.
"""

import random

# Lambda for determining if move1 beats move2
beats = lambda m1, m2: {'rock': 'scissors', 'scissors': 'paper', 'paper': 'rock'}[m1] == m2

# Lambda for getting random computer move
computer_move = lambda: random.choice(['rock', 'paper', 'scissors'])

# Lambda for validating move
is_valid = lambda move: move in ['rock', 'paper', 'scissors']

def main():
    """Main game using lambda functions."""
    print("Rock Paper Scissors - Lambda Edition\n")

    # Scores as list: [player, computer, ties]
    s = [0, 0, 0]

    # Menu actions as lambda dictionary
    actions = {
        '1': lambda: play_round(s),
        '2': lambda: print(f"\nScore - You: {s[0]} | CPU: {s[1]} | Ties: {s[2]} | Total: {sum(s)}"),
        '3': lambda: (s.clear(), s.extend([0, 0, 0]), print("Reset!")) if input("Sure? (y/n): ") == 'y' else None,
        '4': lambda: None
    }

    def play_round(scores):
        """Play a round using lambdas."""
        # Get valid input
        player = None
        while not (player and is_valid(player)):
            player = input("\nRock, Paper, or Scissors? ").lower()

        cpu = computer_move()
        print(f"You: {player} | CPU: {cpu}")

        # Determine outcome using lambda
        if player == cpu:
            print("Tie!")
            scores[2] += 1
        elif beats(player, cpu):
            print("You win!")
            scores[0] += 1
        else:
            print("CPU wins!")
            scores[1] += 1

    # Game loop
    while True:
        print("\n" + "="*30)
        print("1) Play")
        print("2) Score")
        print("3) Reset")
        print("4) Exit")

        choice = input("\n> ")

        if choice in actions:
            result = actions[choice]()
            if choice == '4':
                print(f"\nFinal: {s[0]}-{s[1]}-{s[2]}")
                print("Bye!")
                break
        else:
            print("Invalid!")

if __name__ == "__main__":
    main()
