# Simple beginner code for A* algorithm
# Student 19

def find_lowest_f(open_list, g_scores, goal):
    best = None
    best_f = 999999999
    for node in open_list:
        g = g_scores[node]
        h = abs(node[0] - goal[0]) + abs(node[1] - goal[1])
        f = g + h
        if f < best_f:
            best_f = f
            best = node
    return best

def get_path(parents, start, goal):
    path = []
    current = goal
    while current != start:
        path.append(current)
        current = parents[current]
    path.append(start)
    path.reverse()
    return path

def astar(grid, start, goal):
    open_list = []
    closed_list = []
    parents = {}
    g_scores = {}

    open_list.append(start)
    g_scores[start] = 0

    while len(open_list) > 0:
        current = find_lowest_f(open_list, g_scores, goal)

        if current == goal:
            return get_path(parents, start, goal)

        open_list.remove(current)
        closed_list.append(current)

        row = current[0]
        col = current[1]

        # check all 4 neighbors
        neighbors = []

        # up
        if row > 0:
            neighbors.append((row - 1, col))

        # down
        if row < len(grid) - 1:
            neighbors.append((row + 1, col))

        # left
        if col > 0:
            neighbors.append((row, col - 1))

        # right
        if col < len(grid[0]) - 1:
            neighbors.append((row, col + 1))

        for neighbor in neighbors:
            neighbor_row = neighbor[0]
            neighbor_col = neighbor[1]

            # skip if wall
            if grid[neighbor_row][neighbor_col] == 1:
                continue

            # skip if already closed
            if neighbor in closed_list:
                continue

            new_g = g_scores[current] + 1

            # if not in open list, add it
            if neighbor not in open_list:
                open_list.append(neighbor)
                parents[neighbor] = current
                g_scores[neighbor] = new_g
            else:
                # if already in open list, check if new path is better
                if new_g < g_scores[neighbor]:
                    parents[neighbor] = current
                    g_scores[neighbor] = new_g

    # no path found
    return None

# create grid
grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

start_position = (0, 0)
goal_position = (7, 9)

# run A* algorithm
path = astar(grid, start_position, goal_position)

# print result
if path != None:
    print("Path found!")
    print("Length:", len(path))
    print()

    # print grid with path
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if (i, j) == start_position:
                print('S', end=' ')
            elif (i, j) == goal_position:
                print('G', end=' ')
            elif (i, j) in path:
                print('*', end=' ')
            elif grid[i][j] == 1:
                print('#', end=' ')
            else:
                print('.', end=' ')
        print()
else:
    print("No path found!")
