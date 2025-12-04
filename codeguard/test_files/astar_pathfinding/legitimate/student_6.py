# Simple A* pathfinding
# Beginner implementation

def astar(grid, start, end):
    openlist = [start]
    closedlist = []
    gscore = {start: 0}
    parent = {}

    while openlist:
        current = None
        currentf = float('inf')

        for pos in openlist:
            g = gscore[pos]
            h = abs(pos[0] - end[0]) + abs(pos[1] - end[1])
            f = g + h

            if f < currentf:
                currentf = f
                current = pos

        if current == end:
            path = []
            while current in parent:
                path.append(current)
                current = parent[current]
            path.append(start)
            return path[::-1]

        openlist.remove(current)
        closedlist.append(current)

        neighbors = []
        x, y = current
        if x > 0:
            neighbors.append((x-1, y))
        if x < len(grid)-1:
            neighbors.append((x+1, y))
        if y > 0:
            neighbors.append((x, y-1))
        if y < len(grid[0])-1:
            neighbors.append((x, y+1))

        for n in neighbors:
            if grid[n[0]][n[1]] == 1:
                continue
            if n in closedlist:
                continue

            newscore = gscore[current] + 1

            if n not in openlist:
                openlist.append(n)
            elif newscore >= gscore.get(n, float('inf')):
                continue

            parent[n] = current
            gscore[n] = newscore

    return None

grid = [
    [0,0,0,0,0,0,0,0],
    [0,1,1,0,0,0,0,0],
    [0,0,0,0,1,1,0,0],
    [0,0,0,0,0,0,0,0],
    [0,0,1,1,1,0,0,0],
    [0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0]
]

start = (0,0)
end = (7,7)

path = astar(grid, start, end)

if path:
    print("Path:", path)
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if (i,j) == start:
                print('S', end='')
            elif (i,j) == end:
                print('G', end='')
            elif (i,j) in path:
                print('*', end='')
            elif grid[i][j] == 1:
                print('#', end='')
            else:
                print('.', end='')
        print()
else:
    print("No path")
