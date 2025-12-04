"""
A* Pathfinding with Bidirectional Search Optimization
Advanced Implementation - Student 14
"""

from collections import deque
import heapq

class BidirectionalAStar:
    """
    Bidirectional A* search - searches from both start and goal simultaneously
    More efficient for large grids
    """

    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def heuristic(self, pos1, pos2):
        """Manhattan distance heuristic"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(self, pos):
        """Get valid neighboring positions"""
        neighbors = []
        for dr, dc in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            new_r, new_c = pos[0] + dr, pos[1] + dc
            if (0 <= new_r < self.rows and
                0 <= new_c < self.cols and
                self.grid[new_r][new_c] == 0):
                neighbors.append((new_r, new_c))
        return neighbors

    def search(self, start, goal):
        """Bidirectional A* search"""
        # Forward search (from start)
        forward_frontier = [(0, start)]
        forward_visited = {start: (None, 0)}  # pos: (parent, g_score)

        # Backward search (from goal)
        backward_frontier = [(0, goal)]
        backward_visited = {goal: (None, 0)}

        meeting_point = None
        best_cost = float('inf')

        while forward_frontier and backward_frontier:
            # Expand forward
            f_score, f_current = heapq.heappop(forward_frontier)

            if f_current in backward_visited:
                # Found intersection
                total_cost = forward_visited[f_current][1] + backward_visited[f_current][1]
                if total_cost < best_cost:
                    best_cost = total_cost
                    meeting_point = f_current

            if f_score > best_cost:
                break

            for f_neighbor in self.get_neighbors(f_current):
                new_g = forward_visited[f_current][1] + 1

                if f_neighbor not in forward_visited or new_g < forward_visited[f_neighbor][1]:
                    forward_visited[f_neighbor] = (f_current, new_g)
                    h = self.heuristic(f_neighbor, goal)
                    heapq.heappush(forward_frontier, (new_g + h, f_neighbor))

            # Expand backward
            if not backward_frontier:
                break

            b_score, b_current = heapq.heappop(backward_frontier)

            if b_current in forward_visited:
                # Found intersection
                total_cost = forward_visited[b_current][1] + backward_visited[b_current][1]
                if total_cost < best_cost:
                    best_cost = total_cost
                    meeting_point = b_current

            if b_score > best_cost:
                break

            for b_neighbor in self.get_neighbors(b_current):
                new_g = backward_visited[b_current][1] + 1

                if b_neighbor not in backward_visited or new_g < backward_visited[b_neighbor][1]:
                    backward_visited[b_neighbor] = (b_current, new_g)
                    h = self.heuristic(b_neighbor, start)
                    heapq.heappush(backward_frontier, (new_g + h, b_neighbor))

        if meeting_point is None:
            return None

        # Reconstruct path
        # Forward path
        forward_path = []
        current = meeting_point
        while current is not None:
            forward_path.append(current)
            current = forward_visited[current][0]
        forward_path.reverse()

        # Backward path
        backward_path = []
        current = backward_visited[meeting_point][0]
        while current is not None:
            backward_path.append(current)
            current = backward_visited[current][0]

        return forward_path + backward_path

    def display(self, path, start, goal):
        """Display the grid with path"""
        if path:
            path_set = set(path)
        else:
            path_set = set()

        print("\n Grid Visualization:")
        print("  ", end="")
        for c in range(self.cols):
            print(f"{c:2}", end="")
        print()

        for r in range(self.rows):
            print(f"{r:2} ", end="")
            for c in range(self.cols):
                pos = (r, c)
                if pos == start:
                    print('S ', end='')
                elif pos == goal:
                    print('G ', end='')
                elif pos in path_set:
                    print('* ', end='')
                elif self.grid[r][c] == 1:
                    print('# ', end='')
                else:
                    print('. ', end='')
            print()

def main():
    test_grid = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]

    pathfinder = BidirectionalAStar(test_grid)

    start_pos = (0, 0)
    goal_pos = (8, 11)

    print("Bidirectional A* Pathfinding")
    print(f"Grid size: {len(test_grid)}x{len(test_grid[0])}")
    print(f"Start: {start_pos}")
    print(f"Goal: {goal_pos}")
    print("-" * 50)

    result = pathfinder.search(start_pos, goal_pos)

    if result:
        print(f"\nPath found! Length: {len(result)} steps")
        pathfinder.display(result, start_pos, goal_pos)
    else:
        print("\nNo path found!")
        pathfinder.display(None, start_pos, goal_pos)

if __name__ == "__main__":
    main()
