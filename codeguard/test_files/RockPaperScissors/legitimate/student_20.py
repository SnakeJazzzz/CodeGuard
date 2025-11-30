# Student 20 - Generator-Based Game Loop
"""
Rock Paper Scissors using generators and iterators.
Demonstrates yield-based control flow.
"""

import random

def move_validator():
    """Generator that validates moves."""
    valid_moves = ['rock', 'paper', 'scissors']

    while True:
        move = yield
        if move in valid_moves:
            yield True
        else:
            yield False

def game_round_generator(scores):
    """Generator that yields game rounds."""

    moves = ['rock', 'paper', 'scissors']
    wins = {
        'rock': 'scissors',
        'scissors': 'paper',
        'paper': 'rock'
    }

    while True:
        print("\n" + "-"*40)
        print("NEW ROUND")
        print("-"*40)

        # Get player move
        player_move = None
        while player_move not in moves:
            player_move = input("\nEnter rock/paper/scissors: ").lower()
            if player_move not in moves:
                print("Invalid!")

        computer_move = random.choice(moves)

        print(f"\nYou chose: {player_move}")
        print(f"Computer chose: {computer_move}")

        # Determine outcome
        if player_move == computer_move:
            result = 'tie'
            print(">> TIE!")
            scores['ties'] += 1
        elif wins[player_move] == computer_move:
            result = 'win'
            print(">> YOU WIN!")
            scores['player'] += 1
        else:
            result = 'loss'
            print(">> YOU LOSE!")
            scores['computer'] += 1

        # Yield the result
        yield result

def score_display_generator(scores):
    """Generator that yields formatted score displays."""

    while True:
        yield f"""
{'='*40}
SCORE SUMMARY
{'='*40}
Player Wins:    {scores['player']}
Computer Wins:  {scores['computer']}
Ties:           {scores['ties']}
{'─'*40}
Total Games:    {sum(scores.values())}
{'='*40}
"""

def menu_generator():
    """Generator for menu display."""

    menu_text = """
{'='*40}
MENU
{'='*40}
1) Play Round
2) Show Score
3) Reset Score
4) Quit
{'='*40}
"""

    while True:
        print(menu_text)
        choice = yield
        yield choice

def main():
    """Main game using generators."""
    print("Rock Paper Scissors - Generator Edition")
    print("="*40)

    scores = {
        'player': 0,
        'computer': 0,
        'ties': 0
    }

    # Create generators
    round_gen = game_round_generator(scores)
    score_gen = score_display_generator(scores)

    running = True

    while running:
        print("\n" + "="*40)
        print("MENU")
        print("="*40)
        print("1) Play Round")
        print("2) Show Score")
        print("3) Reset Score")
        print("4) Quit")

        choice = input("\nChoice: ").strip()

        if choice == '1':
            # Use generator to play round
            next(round_gen)

        elif choice == '2':
            # Use generator to display score
            score_display = next(score_gen)
            print(score_display)

        elif choice == '3':
            confirm = input("\nReset scores? (y/n): ").lower()
            if confirm == 'y':
                scores['player'] = 0
                scores['computer'] = 0
                scores['ties'] = 0
                print("Scores reset!")
                # Recreate generators with reset scores
                round_gen = game_round_generator(scores)
                score_gen = score_display_generator(scores)

        elif choice == '4':
            running = False
            print("\nFinal Score:")
            print(next(score_gen))
            print("Thanks for playing!")

        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
