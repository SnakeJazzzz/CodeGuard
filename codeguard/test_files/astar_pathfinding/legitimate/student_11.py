"""
A* Pathfinding with Priority Queue and Named Tuples
Professional implementation with type hints
"""

from queue import PriorityQueue
from typing import List, Tuple, Optional, Set, Dict
from collections import namedtuple

# Define a named tuple for grid positions
Position = namedtuple('Position', ['row', 'col'])

# Named tuple for nodes in the search
SearchNode = namedtuple('SearchNode', ['f_score', 'position', 'g_score'])

class Grid:
    """Represents the 2D grid environment"""

    def __init__(self, layout: List[List[int]]):
        self.layout = layout
        self.height = len(layout)
        self.width = len(layout[0]) if layout else 0

    def is_walkable(self, pos: Position) -> bool:
        """Check if a position is walkable (not a wall and in bounds)"""
        return (0 <= pos.row < self.height and
                0 <= pos.col < self.width and
                self.layout[pos.row][pos.col] == 0)

    def get_adjacent_positions(self, pos: Position) -> List[Position]:
        """Get all valid adjacent positions (4-directional)"""
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        adjacent = []

        for dr, dc in deltas:
            new_pos = Position(pos.row + dr, pos.col + dc)
            if self.is_walkable(new_pos):
                adjacent.append(new_pos)

        return adjacent

class AStar:
    """A* pathfinding algorithm implementation"""

    def __init__(self, grid: Grid):
        self.grid = grid

    @staticmethod
    def manhattan_heuristic(pos1: Position, pos2: Position) -> int:
        """Calculate Manhattan distance between two positions"""
        return abs(pos1.row - pos2.row) + abs(pos1.col - pos2.col)

    def find_shortest_path(self, start: Position, goal: Position) -> Optional[List[Position]]:
        """
        Find the shortest path from start to goal using A* algorithm

        Returns:
            List of positions representing the path, or None if no path exists
        """
        frontier = PriorityQueue()
        frontier.put(SearchNode(0, start, 0))

        came_from: Dict[Position, Position] = {}
        cost_so_far: Dict[Position, int] = {start: 0}
        explored: Set[Position] = set()

        while not frontier.empty():
            current_node = frontier.get()
            current_pos = current_node.position

            # Skip if already explored
            if current_pos in explored:
                continue

            explored.add(current_pos)

            # Goal check
            if current_pos == goal:
                return self._reconstruct_path(came_from, start, goal)

            # Explore neighbors
            for next_pos in self.grid.get_adjacent_positions(current_pos):
                new_cost = cost_so_far[current_pos] + 1

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.manhattan_heuristic(next_pos, goal)
                    frontier.put(SearchNode(priority, next_pos, new_cost))
                    came_from[next_pos] = current_pos

        return None  # No path found

    @staticmethod
    def _reconstruct_path(came_from: Dict[Position, Position],
                         start: Position,
                         goal: Position) -> List[Position]:
        """Reconstruct the path from start to goal"""
        path = [goal]
        current = goal

        while current != start:
            current = came_from[current]
            path.append(current)

        return list(reversed(path))

    def visualize_path(self, path: Optional[List[Position]],
                      start: Position,
                      goal: Position) -> None:
        """Print a visual representation of the grid and path"""
        path_set = set(path) if path else set()

        print("\n" + "=" * (self.grid.width * 2 + 1))
        for row in range(self.grid.height):
            for col in range(self.grid.width):
                pos = Position(row, col)

                if pos == start:
                    symbol = 'S'
                elif pos == goal:
                    symbol = 'G'
                elif pos in path_set:
                    symbol = '*'
                elif self.grid.layout[row][col] == 1:
                    symbol = '#'
                else:
                    symbol = '.'

                print(symbol, end=' ')
            print()
        print("=" * (self.grid.width * 2 + 1))

def main():
    # Create test grid
    grid_layout = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    grid = Grid(grid_layout)
    pathfinder = AStar(grid)

    start_position = Position(0, 0)
    goal_position = Position(7, 9)

    print("A* Pathfinding Algorithm")
    print(f"Start: {start_position}")
    print(f"Goal: {goal_position}")

    path = pathfinder.find_shortest_path(start_position, goal_position)

    if path:
        print(f"\nPath found! Length: {len(path)} steps")
        pathfinder.visualize_path(path, start_position, goal_position)
        print(f"\nPath coordinates: {path}")
    else:
        print("\nNo path found!")
        pathfinder.visualize_path(None, start_position, goal_position)

if __name__ == "__main__":
    main()
