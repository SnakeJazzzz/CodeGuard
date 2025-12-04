"""
Minimal A* implementation
Basic approach, no fancy stuff
"""

def astar_pathfind(maze, start_pos, end_pos):
    open = [start_pos]
    closed = []
    parents = {}
    g = {start_pos: 0}

    while len(open) > 0:
        # find node with lowest f
        current = None
        for node in open:
            if current is None:
                current = node
            else:
                g_current = g[node]
                h_current = abs(node[0]-end_pos[0]) + abs(node[1]-end_pos[1])
                f_current = g_current + h_current

                g_best = g[current]
                h_best = abs(current[0]-end_pos[0]) + abs(current[1]-end_pos[1])
                f_best = g_best + h_best

                if f_current < f_best:
                    current = node

        if current == end_pos:
            # build path
            p = []
            while current in parents:
                p.append(current)
                current = parents[current]
            p.append(start_pos)
            p.reverse()
            return p

        open.remove(current)
        closed.append(current)

        # check neighbors
        r, c = current
        neighbors = []
        if r > 0: neighbors.append((r-1, c))
        if r < len(maze)-1: neighbors.append((r+1, c))
        if c > 0: neighbors.append((r, c-1))
        if c < len(maze[0])-1: neighbors.append((r, c+1))

        for neighbor in neighbors:
            nr, nc = neighbor

            if maze[nr][nc] == 1:
                continue

            if neighbor in closed:
                continue

            new_g = g[current] + 1

            if neighbor not in open:
                open.append(neighbor)
            elif new_g >= g[neighbor]:
                continue

            parents[neighbor] = current
            g[neighbor] = new_g

    return None

# test maze
m = [
    [0,0,0,0,0],
    [0,1,1,1,0],
    [0,0,0,0,0],
    [0,1,1,1,0],
    [0,0,0,0,0]
]

p = astar_pathfind(m, (0,0), (4,4))

print(p)

if p:
    for i in range(len(m)):
        for j in range(len(m[0])):
            if (i,j) == (0,0):
                print('S', end='')
            elif (i,j) == (4,4):
                print('G', end='')
            elif (i,j) in p:
                print('*', end='')
            elif m[i][j] == 1:
                print('#', end='')
            else:
                print('.', end='')
        print()
