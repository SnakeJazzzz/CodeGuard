# Student 13 - Dataclass for Game State
"""
Rock Paper Scissors using Python dataclasses.
Modern Python with type hints and clean state management.
"""

import random
from dataclasses import dataclass, field
from typing import List

@dataclass
class GameScore:
    """Dataclass to track game scores with type safety."""
    player_wins: int = 0
    computer_wins: int = 0
    ties: int = 0

    def total_games(self) -> int:
        """Calculate total games played."""
        return self.player_wins + self.computer_wins + self.ties

    def win_rate(self) -> float:
        """Calculate player win rate."""
        total = self.total_games()
        return (self.player_wins / total * 100) if total > 0 else 0.0

    def reset(self) -> None:
        """Reset all scores to zero."""
        self.player_wins = 0
        self.computer_wins = 0
        self.ties = 0

    def __str__(self) -> str:
        """String representation of scores."""
        return (f"Player: {self.player_wins} | "
                f"Computer: {self.computer_wins} | "
                f"Ties: {self.ties}")

@dataclass
class GameConfig:
    """Configuration for the game."""
    valid_moves: List[str] = field(default_factory=lambda: ['rock', 'paper', 'scissors'])
    win_map: dict = field(default_factory=lambda: {
        'rock': 'scissors',
        'scissors': 'paper',
        'paper': 'rock'
    })

def get_player_choice(config: GameConfig) -> str:
    """Get validated player input."""
    while True:
        choice = input(f"\nChoose {'/'.join(config.valid_moves)}: ").lower().strip()
        if choice in config.valid_moves:
            return choice
        print("Invalid choice!")

def determine_winner(player: str, computer: str, config: GameConfig) -> str:
    """Determine round winner."""
    if player == computer:
        return 'tie'
    elif config.win_map[player] == computer:
        return 'player'
    else:
        return 'computer'

def play_round(score: GameScore, config: GameConfig) -> None:
    """Execute a single game round."""
    print("\n" + "="*40)
    print("NEW ROUND")
    print("="*40)

    player_move = get_player_choice(config)
    computer_move = random.choice(config.valid_moves)

    print(f"\nYour move: {player_move}")
    print(f"Computer move: {computer_move}")

    winner = determine_winner(player_move, computer_move, config)

    if winner == 'tie':
        print("\n>> TIE!")
        score.ties += 1
    elif winner == 'player':
        print("\n>> YOU WIN!")
        score.player_wins += 1
    else:
        print("\n>> COMPUTER WINS!")
        score.computer_wins += 1

def show_statistics(score: GameScore) -> None:
    """Display detailed statistics."""
    print("\n" + "="*40)
    print("GAME STATISTICS")
    print("="*40)
    print(f"Player Wins:    {score.player_wins}")
    print(f"Computer Wins:  {score.computer_wins}")
    print(f"Ties:           {score.ties}")
    print("-"*40)
    print(f"Total Games:    {score.total_games()}")
    print(f"Win Rate:       {score.win_rate():.1f}%")
    print("="*40)

def main() -> None:
    """Main game function with dataclass state."""
    print("Rock Paper Scissors - Dataclass Edition")
    print("="*40)

    score = GameScore()
    config = GameConfig()

    while True:
        print("\n[1] Play Round")
        print("[2] View Stats")
        print("[3] Reset Score")
        print("[4] Quit")

        choice = input("\nSelection: ").strip()

        if choice == '1':
            play_round(score, config)

        elif choice == '2':
            show_statistics(score)

        elif choice == '3':
            if input("Confirm reset (y/n): ").lower() == 'y':
                score.reset()
                print("Scores reset!")

        elif choice == '4':
            print("\nFinal Statistics:")
            show_statistics(score)
            print("\nGoodbye!")
            break

        else:
            print("Invalid selection!")

if __name__ == "__main__":
    main()
