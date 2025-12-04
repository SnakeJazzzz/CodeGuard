#!/usr/bin/env python3
# A* Pathfinding - Student 18
# Using classes for Grid and Position

class Position:
    def __init__(self, r, c):
        self.row = r
        self.col = c

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def __repr__(self):
        return f"({self.row},{self.col})"

    def distance_to(self, other):
        return abs(self.row - other.row) + abs(self.col - other.col)

class GridWorld:
    def __init__(self, data):
        self.data = data
        self.num_rows = len(data)
        self.num_cols = len(data[0]) if data else 0

    def is_walkable(self, pos):
        if 0 <= pos.row < self.num_rows and 0 <= pos.col < self.num_cols:
            return self.data[pos.row][pos.col] == 0
        return False

    def adjacent_positions(self, pos):
        adj = []
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            new_pos = Position(pos.row + dr, pos.col + dc)
            if self.is_walkable(new_pos):
                adj.append(new_pos)
        return adj

def a_star_search(world, start_pos, goal_pos):
    open_set = [start_pos]
    closed_set = set()
    g_costs = {start_pos: 0}
    parents = {}

    while open_set:
        # Select node with minimum f score
        current = min(open_set, key=lambda p: g_costs[p] + p.distance_to(goal_pos))

        if current == goal_pos:
            # Reconstruct path
            path = []
            while current in parents:
                path.append(current)
                current = parents[current]
            path.append(start_pos)
            return list(reversed(path))

        open_set.remove(current)
        closed_set.add(current)

        for neighbor in world.adjacent_positions(current):
            if neighbor in closed_set:
                continue

            tentative_g = g_costs[current] + 1

            if neighbor not in open_set:
                open_set.append(neighbor)
            elif tentative_g >= g_costs.get(neighbor, float('inf')):
                continue

            parents[neighbor] = current
            g_costs[neighbor] = tentative_g

    return None

def display_grid(world, path, start_pos, goal_pos):
    path_positions = set(path) if path else set()

    for r in range(world.num_rows):
        for c in range(world.num_cols):
            p = Position(r, c)
            if p == start_pos:
                symbol = 'S'
            elif p == goal_pos:
                symbol = 'G'
            elif p in path_positions:
                symbol = '*'
            elif world.data[r][c] == 1:
                symbol = '#'
            else:
                symbol = '.'
            print(symbol, end=' ')
        print()

# Main execution
grid_data = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
    [0, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

world = GridWorld(grid_data)
start = Position(0, 0)
goal = Position(7, 7)

print("A* Pathfinding Algorithm")
print(f"Grid: {world.num_rows}x{world.num_cols}")
print(f"Start: {start}")
print(f"Goal: {goal}")
print()

result = a_star_search(world, start, goal)

if result:
    print(f"Path found with {len(result)} nodes:")
    display_grid(world, result, start, goal)
    print("\nPath sequence:")
    for i, pos in enumerate(result):
        print(f"  {i}: {pos}")
else:
    print("No path found!")
    display_grid(world, None, start, goal)
