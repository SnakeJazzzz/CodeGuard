"""A* with dictionary-based grid representation"""

class AStarDict:
    def __init__(self):
        self.obstacles = set()
        self.max_x = 0
        self.max_y = 0

    def add_obstacle(self, x, y):
        self.obstacles.add((x, y))
        self.max_x = max(self.max_x, x)
        self.max_y = max(self.max_y, y)

    def manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def neighbors(self, node):
        x, y = node
        candidates = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        valid = []
        for nx, ny in candidates:
            if 0 <= nx <= self.max_x and 0 <= ny <= self.max_y:
                if (nx, ny) not in self.obstacles:
                    valid.append((nx, ny))
        return valid

    def search(self, start, goal):
        open_set = {start}
        closed_set = set()
        g_scores = {start: 0}
        f_scores = {start: self.manhattan(start, goal)}
        parents = {}

        while open_set:
            current = min(open_set, key=lambda n: f_scores.get(n, float('inf')))

            if current == goal:
                path = [current]
                while current in parents:
                    current = parents[current]
                    path.append(current)
                return path[::-1]

            open_set.remove(current)
            closed_set.add(current)

            for neighbor in self.neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g = g_scores[current] + 1

                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g >= g_scores.get(neighbor, float('inf')):
                    continue

                parents[neighbor] = current
                g_scores[neighbor] = tentative_g
                f_scores[neighbor] = tentative_g + self.manhattan(neighbor, goal)

        return None

    def draw(self, path, start, goal):
        path_set = set(path) if path else set()
        for y in range(self.max_y + 1):
            for x in range(self.max_x + 1):
                pos = (x, y)
                if pos == start:
                    print('S', end='')
                elif pos == goal:
                    print('G', end='')
                elif pos in path_set:
                    print('*', end='')
                elif pos in self.obstacles:
                    print('#', end='')
                else:
                    print('.', end='')
            print()

astar = AStarDict()

obstacles = [
    (3, 1), (3, 2), (3, 3), (3, 4),
    (6, 5), (6, 6), (6, 7),
    (2, 6), (2, 7), (3, 7)
]

for obs in obstacles:
    astar.add_obstacle(obs[0], obs[1])

astar.max_x = 9
astar.max_y = 9

start_point = (0, 0)
goal_point = (9, 9)

result = astar.search(start_point, goal_point)

if result:
    print(f"Found path with {len(result)} steps:")
    astar.draw(result, start_point, goal_point)
else:
    print("Path not found")
