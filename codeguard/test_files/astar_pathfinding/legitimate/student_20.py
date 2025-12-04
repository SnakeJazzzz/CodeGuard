"""
A* Pathfinding with Jump Point Search Optimization
Advanced implementation - Student 20
"""

class JumpPointSearch:
    """
    Jump Point Search - optimized A* for uniform-cost grids
    Reduces nodes explored by "jumping" over intermediate nodes
    """

    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def is_walkable(self, x, y):
        """Check if position is within bounds and walkable"""
        return (0 <= x < self.rows and
                0 <= y < self.cols and
                self.grid[x][y] == 0)

    def jump(self, x, y, dx, dy, goal):
        """
        Recursively jump in direction (dx, dy) until hitting obstacle or forced neighbor
        Returns jump point or None
        """
        nx, ny = x + dx, y + dy

        if not self.is_walkable(nx, ny):
            return None

        if (nx, ny) == goal:
            return (nx, ny)

        # Check for forced neighbors
        if dx != 0 and dy != 0:  # Diagonal
            # Check horizontal and vertical
            if (self.is_walkable(nx + dx, ny) and not self.is_walkable(nx, ny - dy)) or \
               (self.is_walkable(nx, ny + dy) and not self.is_walkable(nx - dx, ny)):
                return (nx, ny)

            # Check diagonal jumps
            if self.jump(nx, ny, dx, 0, goal) is not None or \
               self.jump(nx, ny, 0, dy, goal) is not None:
                return (nx, ny)

        else:  # Horizontal or vertical
            if dx != 0:  # Horizontal
                if (self.is_walkable(nx, ny + 1) and not self.is_walkable(nx - dx, ny + 1)) or \
                   (self.is_walkable(nx, ny - 1) and not self.is_walkable(nx - dx, ny - 1)):
                    return (nx, ny)
            else:  # Vertical
                if (self.is_walkable(nx + 1, ny) and not self.is_walkable(nx + 1, ny - dy)) or \
                   (self.is_walkable(nx - 1, ny) and not self.is_walkable(nx - 1, ny - dy)):
                    return (nx, ny)

        return self.jump(nx, ny, dx, dy, goal)

    def get_successors(self, x, y, goal):
        """Get jump points from current position"""
        successors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dx, dy in directions:
            jump_point = self.jump(x, y, dx, dy, goal)
            if jump_point:
                successors.append(jump_point)

        return successors

    def heuristic(self, pos, goal):
        """Octile distance for 8-directional movement"""
        dx = abs(pos[0] - goal[0])
        dy = abs(pos[1] - goal[1])
        return max(dx, dy) + (1.414 - 1) * min(dx, dy)

    def distance(self, a, b):
        """Actual distance between two points"""
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        if dx == 0 or dy == 0:
            return dx + dy
        else:
            return 1.414 * min(dx, dy) + abs(dx - dy)

    def search(self, start, goal):
        """JPS A* search"""
        import heapq

        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        visited = set()

        while open_set:
            _, current = heapq.heappop(open_set)

            if current in visited:
                continue

            visited.add(current)

            if current == goal:
                return self._reconstruct_path(came_from, start, goal)

            for successor in self.get_successors(current[0], current[1], goal):
                if successor in visited:
                    continue

                tentative_g = g_score[current] + self.distance(current, successor)

                if successor not in g_score or tentative_g < g_score[successor]:
                    came_from[successor] = current
                    g_score[successor] = tentative_g
                    f_score = tentative_g + self.heuristic(successor, goal)
                    heapq.heappush(open_set, (f_score, successor))

        return None

    def _reconstruct_path(self, came_from, start, goal):
        """Reconstruct path from jump points"""
        path = [goal]
        current = goal

        while current != start:
            prev = came_from[current]
            # Fill in intermediate points
            path.extend(self._interpolate(prev, current))
            current = prev

        path.append(start)
        return list(reversed(path))

    def _interpolate(self, start, end):
        """Fill in points between jump points"""
        points = []
        x0, y0 = start
        x1, y1 = end

        dx = 1 if x1 > x0 else -1 if x1 < x0 else 0
        dy = 1 if y1 > y0 else -1 if y1 < y0 else 0

        x, y = x0 + dx, y0 + dy

        while (x, y) != end:
            points.append((x, y))
            x += dx
            y += dy

        return points

    def visualize(self, path, start, goal):
        """Display grid with path"""
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

if __name__ == "__main__":
    test_grid = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    jps = JumpPointSearch(test_grid)

    start_pos = (0, 0)
    goal_pos = (7, 11)

    print("Jump Point Search (Optimized A*)")
    print(f"Start: {start_pos}")
    print(f"Goal: {goal_pos}")
    print("-" * 50)

    result = jps.search(start_pos, goal_pos)

    if result:
        print(f"\nPath found! Length: {len(result)} steps")
        jps.visualize(result, start_pos, goal_pos)
    else:
        print("\nNo path found!")
        jps.visualize(None, start_pos, goal_pos)
