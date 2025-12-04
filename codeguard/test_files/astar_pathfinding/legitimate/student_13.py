# A* using only lists and basic operations
# Beginner friendly code

grid = [
    [0,0,0,0,0,0,0,0,0,0],
    [0,0,1,1,1,0,0,0,0,0],
    [0,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,1,0,0,1,1,0],
    [0,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,0],
    [0,1,1,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0],
    [0,0,0,0,0,0,0,0,0,0]
]

def find_path(grid, start, goal):
    open_list = []
    closed_list = []

    # add start to open list
    open_list.append(start)

    # store g scores
    g_score = {}
    g_score[start] = 0

    # store parent for path reconstruction
    parent = {}

    while open_list:
        # find node with lowest f score
        current = None
        current_f = 999999

        for node in open_list:
            g = g_score[node]
            # calculate h (manhattan distance)
            h = abs(node[0] - goal[0]) + abs(node[1] - goal[1])
            f = g + h

            if f < current_f:
                current_f = f
                current = node

        # check if we reached goal
        if current == goal:
            # reconstruct path
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            path.reverse()
            return path

        # move current from open to closed
        open_list.remove(current)
        closed_list.append(current)

        # get neighbors
        row = current[0]
        col = current[1]

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

        # process neighbors
        for neighbor in neighbors:
            n_row = neighbor[0]
            n_col = neighbor[1]

            # skip if wall
            if grid[n_row][n_col] == 1:
                continue

            # skip if in closed list
            if neighbor in closed_list:
                continue

            # calculate new g score
            new_g = g_score[current] + 1

            # check if neighbor is in open list
            if neighbor not in open_list:
                open_list.append(neighbor)
                parent[neighbor] = current
                g_score[neighbor] = new_g
            else:
                # check if this path is better
                if new_g < g_score[neighbor]:
                    parent[neighbor] = current
                    g_score[neighbor] = new_g

    # no path found
    return None

# run algorithm
start_pos = (0, 0)
goal_pos = (9, 9)

path = find_path(grid, start_pos, goal_pos)

# print results
if path:
    print("Path found!")
    print("Length:", len(path))

    # print grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (i, j) == start_pos:
                print('S', end=' ')
            elif (i, j) == goal_pos:
                print('G', end=' ')
            elif (i, j) in path:
                print('*', end=' ')
            elif grid[i][j] == 1:
                print('#', end=' ')
            else:
                print('.', end=' ')
        print()
else:
    print("No path found")
