"""
A* Pathfinding Algorithm Implementation
Student 1 - Object-Oriented Approach
"""

# This is my implementation of the A* algorithm
# I spent a lot of time working on this assignment

import heapq

# Node class represents each cell in the grid
class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0  # cost from start
        self.h = 0  # heuristic cost to goal
        self.f = 0  # total cost

    def __lt__(self, other):
        return self.f < other.f

    def __eq__(self, other):
        return self.position == other.position

# Main pathfinding class
class AStarPathfinder:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    # Manhattan distance heuristic
    def heuristic(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    # Get valid neighbors for a node
    def get_neighbors(self, node):
        neighbors = []
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for direction in directions:
            new_pos = (node.position[0] + direction[0], node.position[1] + direction[1])

            if (0 <= new_pos[0] < self.rows and
                0 <= new_pos[1] < self.cols and
                self.grid[new_pos[0]][new_pos[1]] != 1):
                neighbors.append(Node(new_pos, node))

        return neighbors

    # Main A* algorithm implementation
    def find_path(self, start, goal):
        start_node = Node(start)
        goal_node = Node(goal)

        open_list = []
        closed_set = set()

        heapq.heappush(open_list, start_node)

        while open_list:
            current = heapq.heappop(open_list)
            closed_set.add(current.position)

            if current == goal_node:
                path = []
                while current:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]

            for neighbor in self.get_neighbors(current):
                if neighbor.position in closed_set:
                    continue

                neighbor.g = current.g + 1
                neighbor.h = self.heuristic(neighbor.position, goal)
                neighbor.f = neighbor.g + neighbor.h

                if not any(n.position == neighbor.position and n.f <= neighbor.f for n in open_list):
                    heapq.heappush(open_list, neighbor)

        return None

    # Display the grid with the path
    def display_path(self, path, start, goal):
        for i in range(self.rows):
            for j in range(self.cols):
                if (i, j) == start:
                    print('S', end=' ')
                elif (i, j) == goal:
                    print('G', end=' ')
                elif path and (i, j) in path:
                    print('*', end=' ')
                elif self.grid[i][j] == 1:
                    print('#', end=' ')
                else:
                    print('.', end=' ')
            print()

# Main execution
if __name__ == "__main__":
    # Define the grid
    grid = [
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

    start = (0, 0)
    goal = (9, 9)

    pathfinder = AStarPathfinder(grid)
    path = pathfinder.find_path(start, goal)

    if path:
        print("Path found!")
        print(f"Path length: {len(path)}")
        pathfinder.display_path(path, start, goal)
    else:
        print("No path found!")
