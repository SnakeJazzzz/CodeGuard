#!/usr/bin/env python3
# A* Pathfinding - Interactive Version
# Student 9

import sys

WALL = '#'
EMPTY = '.'
START = 'S'
GOAL = 'G'
PATH = '*'

def get_heuristic(point1, point2, heuristic_type='manhattan'):
    """Calculate heuristic based on type"""
    x1, y1 = point1
    x2, y2 = point2

    if heuristic_type == 'manhattan':
        return abs(x1 - x2) + abs(y1 - y2)
    elif heuristic_type == 'euclidean':
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5
    else:
        # Octile distance
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return (dx + dy) + (1.414 - 2) * min(dx, dy)

def get_successors(state, grid):
    """Generate successor states"""
    x, y = state
    rows, cols = len(grid), len(grid[0])
    successors = []

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] != 1:
            successors.append((nx, ny))

    return successors

def reconstruct_solution(parents, start, goal):
    """Rebuild path from parent pointers"""
    if goal not in parents:
        return None

    path = []
    current = goal
    while current != start:
        path.append(current)
        current = parents[current]
    path.append(start)
    return path[::-1]

def a_star_algorithm(grid, start, goal, heuristic='manhattan'):
    """A* search implementation"""
    from heapq import heappush, heappop

    open_list = []
    heappush(open_list, (0, start))

    g_values = {start: 0}
    parents = {}
    closed = set()

    while open_list:
        f_val, current = heappop(open_list)

        if current in closed:
            continue

        closed.add(current)

        if current == goal:
            return reconstruct_solution(parents, start, goal)

        for successor in get_successors(current, grid):
            if successor in closed:
                continue

            tentative_g = g_values[current] + 1

            if successor not in g_values or tentative_g < g_values[successor]:
                g_values[successor] = tentative_g
                h_val = get_heuristic(successor, goal, heuristic)
                f_val = tentative_g + h_val
                parents[successor] = current
                heappush(open_list, (f_val, successor))

    return None

def render_grid(grid, path=None, start=None, goal=None):
    """Render the grid with path"""
    path_coords = set(path) if path else set()

    for i, row in enumerate(grid):
        for j, cell in enumerate(row):
            coord = (i, j)
            if coord == start:
                print(START, end=' ')
            elif coord == goal:
                print(GOAL, end=' ')
            elif coord in path_coords:
                print(PATH, end=' ')
            elif cell == 1:
                print(WALL, end=' ')
            else:
                print(EMPTY, end=' ')
        print()

def main():
    # Define test grid
    test_grid = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    start_position = (0, 0)
    goal_position = (9, 14)

    print("Running A* Pathfinding Algorithm")
    print(f"Start: {start_position}, Goal: {goal_position}")
    print("-" * 50)

    solution = a_star_algorithm(test_grid, start_position, goal_position, 'manhattan')

    if solution:
        print(f"\nPath found! Length: {len(solution)} steps")
        print("\nVisualization:")
        render_grid(test_grid, solution, start_position, goal_position)
    else:
        print("\nNo path exists between start and goal!")
        render_grid(test_grid, None, start_position, goal_position)

if __name__ == '__main__':
    main()
