"""
A* Pathfinding using Diagonal Movements
Uses Chebyshev distance heuristic
"""

import heapq
from dataclasses import dataclass, field
from typing import Tuple, List, Optional

@dataclass(order=True)
class PrioritizedNode:
    priority: float
    position: Tuple[int, int] = field(compare=False)
    g_cost: float = field(default=0, compare=False)
    parent: Optional[Tuple[int, int]] = field(default=None, compare=False)

class DiagonalAStarPathfinder:
    """A* with diagonal movement support"""

    def __init__(self, grid: List[List[int]]):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])

    @staticmethod
    def chebyshev_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Chebyshev distance for diagonal movement"""
        dx = abs(pos1[0] - pos2[0])
        dy = abs(pos1[1] - pos2[1])
        return max(dx, dy)

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int, float]]:
        """Get neighbors with costs (diagonal = sqrt(2), straight = 1)"""
        row, col = pos
        neighbors = []

        # 8-directional movement
        directions = [
            (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),  # straight
            (-1, -1, 1.414), (-1, 1, 1.414), (1, -1, 1.414), (1, 1, 1.414)  # diagonal
        ]

        for dr, dc, cost in directions:
            new_row, new_col = row + dr, col + dc

            if (0 <= new_row < self.height and
                0 <= new_col < self.width and
                self.grid[new_row][new_col] == 0):
                neighbors.append(((new_row, new_col), cost))

        return neighbors

    def find_path(self, start: Tuple[int, int], goal: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        """Execute A* search with diagonal movement"""
        frontier = []
        start_node = PrioritizedNode(0, start, 0, None)
        heapq.heappush(frontier, start_node)

        visited = set()
        came_from = {}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)

            if current.position in visited:
                continue

            visited.add(current.position)

            if current.position == goal:
                # Reconstruct path
                path = []
                pos = goal
                while pos in came_from:
                    path.append(pos)
                    pos = came_from[pos]
                path.append(start)
                return path[::-1]

            for neighbor, move_cost in self.get_neighbors(current.position):
                new_cost = cost_so_far[current.position] + move_cost

                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + self.chebyshev_distance(neighbor, goal)
                    heapq.heappush(frontier, PrioritizedNode(priority, neighbor, new_cost, current.position))
                    came_from[neighbor] = current.position

        return None

    def visualize(self, path: Optional[List[Tuple[int, int]]], start: Tuple[int, int], goal: Tuple[int, int]):
        """Display grid with path"""
        path_set = set(path) if path else set()

        print("\n" + "="*30)
        for r in range(self.height):
            for c in range(self.width):
                pos = (r, c)
                if pos == start:
                    print('S ', end='')
                elif pos == goal:
                    print('G ', end='')
                elif pos in path_set:
                    print('* ', end='')
                elif self.grid[r][c] == 1:
                    print('# ', end='')
                else:
                    print('. ', end='')
            print()
        print("="*30)

if __name__ == "__main__":
    maze = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    pathfinder = DiagonalAStarPathfinder(maze)
    result = pathfinder.find_path((0, 0), (7, 11))

    if result:
        print(f"Path found! Length: {len(result)} nodes")
        pathfinder.visualize(result, (0, 0), (7, 11))
    else:
        print("No path found!")
