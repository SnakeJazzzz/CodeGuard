# Student 8 - Enum-Based Implementation
"""
Rock Paper Scissors using Python Enums for type safety.
Demonstrates cleaner code with enumerated types.
"""

import random
from enum import Enum, auto

class Move(Enum):
    """Enumeration for game moves."""
    ROCK = auto()
    PAPER = auto()
    SCISSORS = auto()

class Outcome(Enum):
    """Enumeration for round outcomes."""
    WIN = auto()
    LOSS = auto()
    TIE = auto()

def parse_move(user_input):
    """Convert string input to Move enum."""
    move_map = {
        'rock': Move.ROCK,
        'r': Move.ROCK,
        'paper': Move.PAPER,
        'p': Move.PAPER,
        'scissors': Move.SCISSORS,
        's': Move.SCISSORS
    }
    return move_map.get(user_input.lower())

def judge_round(player_move, computer_move):
    """Determine outcome using enum comparison."""
    if player_move == computer_move:
        return Outcome.TIE

    win_conditions = {
        Move.ROCK: Move.SCISSORS,
        Move.SCISSORS: Move.PAPER,
        Move.PAPER: Move.ROCK
    }

    if win_conditions[player_move] == computer_move:
        return Outcome.WIN
    else:
        return Outcome.LOSS

def main():
    """Main game function using enums."""
    score_tracker = {
        Outcome.WIN: 0,
        Outcome.LOSS: 0,
        Outcome.TIE: 0
    }

    print("Rock Paper Scissors - Enum Edition")
    print("="*40)

    while True:
        print("\nOptions:")
        print("  1. Play")
        print("  2. Score")
        print("  3. Reset")
        print("  4. Quit")

        selection = input("\n> ")

        if selection == '1':
            # Play round
            print("\nEnter move (rock/paper/scissors or r/p/s):")
            user_input = input("> ")

            player_move = parse_move(user_input)
            if not player_move:
                print("Invalid move!")
                continue

            computer_move = random.choice(list(Move))

            print(f"\nYou: {player_move.name}")
            print(f"CPU: {computer_move.name}")

            result = judge_round(player_move, computer_move)
            score_tracker[result] += 1

            if result == Outcome.WIN:
                print(">>> YOU WIN! <<<")
            elif result == Outcome.LOSS:
                print(">>> YOU LOSE <<<")
            else:
                print(">>> TIE <<<")

        elif selection == '2':
            # Display score
            print("\n" + "="*40)
            print("SCOREBOARD")
            print("="*40)
            print(f"Wins:   {score_tracker[Outcome.WIN]}")
            print(f"Losses: {score_tracker[Outcome.LOSS]}")
            print(f"Ties:   {score_tracker[Outcome.TIE]}")

            total = sum(score_tracker.values())
            if total > 0:
                win_pct = (score_tracker[Outcome.WIN] / total) * 100
                print(f"\nWin Rate: {win_pct:.1f}%")
                print(f"Games: {total}")

        elif selection == '3':
            # Reset scores
            if input("Reset? (y/n): ").lower() == 'y':
                for outcome in Outcome:
                    score_tracker[outcome] = 0
                print("Reset complete!")

        elif selection == '4':
            # Exit
            print("\nFinal Stats:")
            print(f"W: {score_tracker[Outcome.WIN]} | " +
                  f"L: {score_tracker[Outcome.LOSS]} | " +
                  f"T: {score_tracker[Outcome.TIE]}")
            print("\nGoodbye!")
            break

        else:
            print("Invalid selection!")

if __name__ == "__main__":
    main()
