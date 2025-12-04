"""
A* Implementation - Functional Programming Approach
Author: Student 2
"""

from queue import PriorityQueue
from math import sqrt

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

def reconstruct_path(came_from, current):
    """Backtrack from goal to start to get path"""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]

def astar_search(grid, start, goal):
    """Main A* algorithm using functional approach"""
    open_set = PriorityQueue()
    open_set.put((0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: euclidean_distance(start, goal)}

    explored = set()

    while not open_set.empty():
        _, current = open_set.get()

        if current in explored:
            continue

        explored.add(current)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor in get_valid_neighbors(grid, current):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + euclidean_distance(neighbor, goal)
                open_set.put((f_score[neighbor], neighbor))

    return None

def visualize_grid(grid, path, start, goal):
    """Display grid with path"""
    path_set = set(path) if path else set()

    for r in range(len(grid)):
        for c in range(len(grid[0])):
            pos = (r, c)
            if pos == start:
                print('S', end=' ')
            elif pos == goal:
                print('G', end=' ')
            elif pos in path_set:
                print('*', end=' ')
            elif grid[r][c] == 1:
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

    result = astar_search(maze, start_pos, goal_pos)

    if result:
        print(f"Success! Path found with {len(result)} steps")
        visualize_grid(maze, result, start_pos, goal_pos)
    else:
        print("No path exists")

if __name__ == "__main__":
    main()
