# Student 6 - List Index with Modulo Math
"""
Rock Paper Scissors using mathematical approach.
Uses modulo arithmetic to determine winner elegantly.
"""

import random

CHOICES = ['rock', 'paper', 'scissors']

def get_choice_index():
    """Get player choice and convert to index."""
    print("\nMake your choice:")
    for i, choice in enumerate(CHOICES):
        print(f"{i}: {choice}")

    while True:
        try:
            idx = int(input("Enter 0, 1, or 2: "))
            if 0 <= idx <= 2:
                return idx
        except ValueError:
            pass
        print("Invalid! Enter 0, 1, or 2.")

def calculate_winner(player_idx, computer_idx):
    """
    Calculate winner using modulo arithmetic.
    (player - computer) % 3:
      0 = tie
      1 = player wins
      2 = computer wins
    """
    diff = (player_idx - computer_idx) % 3
    return diff

def main():
    """Main game function using index-based logic."""
    wins = [0, 0, 0]  # [player, computer, ties]

    print("=== Rock Paper Scissors (Math Edition) ===\n")

    while True:
        print("\n" + "="*40)
        print("MENU")
        print("="*40)
        print("[1] Play")
        print("[2] View Statistics")
        print("[3] Reset Statistics")
        print("[4] Exit")

        choice = input("\nYour choice: ").strip()

        if choice == '1':
            print("\n--- New Game ---")
            player_idx = get_choice_index()
            computer_idx = random.randint(0, 2)

            print(f"\nYou picked: {CHOICES[player_idx]}")
            print(f"Computer picked: {CHOICES[computer_idx]}")

            result = calculate_winner(player_idx, computer_idx)

            if result == 0:
                print("\n>> TIE!")
                wins[2] += 1
            elif result == 1:
                print("\n>> YOU WIN!")
                wins[0] += 1
            else:
                print("\n>> COMPUTER WINS!")
                wins[1] += 1

        elif choice == '2':
            print("\n--- Statistics ---")
            print(f"Player Wins:   {wins[0]}")
            print(f"Computer Wins: {wins[1]}")
            print(f"Ties:          {wins[2]}")
            print(f"Total Played:  {sum(wins)}")

            if sum(wins) > 0:
                win_rate = (wins[0] / sum(wins)) * 100
                print(f"Win Rate:      {win_rate:.1f}%")

        elif choice == '3':
            confirm = input("Reset all stats? (yes/no): ")
            if confirm.lower() == 'yes':
                wins = [0, 0, 0]
                print("Statistics cleared!")

        elif choice == '4':
            print("\nGame Over!")
            print(f"Final Record: {wins[0]}W - {wins[1]}L - {wins[2]}T")
            break

        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
