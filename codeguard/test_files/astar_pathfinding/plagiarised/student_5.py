"""
A* Pathfinding - My Implementation
Student 5
"""

import heapq
from queue import PriorityQueue
from math import sqrt

# Node representation for pathfinding
class PathNode:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.position == other.position

def euclidean_distance(p1, p2):
    """Calculate Euclidean distance heuristic"""
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def get_valid_neighbors(grid, position):
    """Return valid neighboring cells"""
    rows, cols = len(grid), len(grid[0])
    row, col = position
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    return [
        (row + dr, col + dc)
        for dr, dc in moves
        if 0 <= row + dr < rows and 0 <= col + dc < cols
        and grid[row + dr][col + dc] == 0
    ]

# Main A* pathfinding class
class AStarSolver:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def heuristic(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def find_path(self, start, goal):
        start_node = PathNode(start)
        goal_node = PathNode(goal)

        open_list = []
        closed_set = set()

        heapq.heappush(open_list, start_node)

        while open_list:
            current = heapq.heappop(open_list)
            closed_set.add(current.position)

            if current == goal_node:
                path = []
                while current:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            for neighbor_pos in get_valid_neighbors(self.grid, current.position):
                if neighbor_pos in closed_set:
                    continue

                neighbor = PathNode(neighbor_pos, current)
                neighbor.g = current.g + 1
                neighbor.h = euclidean_distance(neighbor.position, goal)
                neighbor.f = neighbor.g + neighbor.h

                if not any(n.position == neighbor.position and n.f <= neighbor.f for n in open_list):
                    heapq.heappush(open_list, neighbor)

        return None

    def visualize_grid(self, path, start, goal):
        path_set = set(path) if path else set()

        for r in range(self.rows):
            for c in range(self.cols):
                pos = (r, c)
                if pos == start:
                    print('S', end=' ')
                elif pos == goal:
                    print('G', end=' ')
                elif pos in path_set:
                    print('*', end=' ')
                elif self.grid[r][c] == 1:
                    print('#', end=' ')
                else:
                    print('.', end=' ')
            print()

def main():
    maze = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    ]

    start_pos = (0, 0)
    goal_pos = (9, 9)

    solver = AStarSolver(maze)
    result = solver.find_path(start_pos, goal_pos)

    if result:
        print(f"Success! Path found with {len(result)} steps")
        solver.visualize_grid(result, start_pos, goal_pos)
    else:
        print("No path exists")

if __name__ == "__main__":
    main()
