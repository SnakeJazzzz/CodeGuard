"""
A* Pathfinding Algorithm Implementation
Student 4 - Object-Oriented Approach
"""

import heapq

# Cell class for grid representation
class Cell:
    def __init__(self, loc, prev=None):
        self.loc = loc
        self.prev = prev
        self.cost_from_start = 0
        self.heuristic_cost = 0
        self.total_cost = 0

    def __lt__(self, otherCell):
        return self.total_cost < otherCell.total_cost

    def __eq__(self, otherCell):
        return self.loc == otherCell.loc

# Pathfinding class using A* algorithm
class PathFinder:
    def __init__(self, map):
        self.map = map
        self.height = len(map)
        self.width = len(map[0])

    # Calculate Manhattan distance between two points
    def calculate_heuristic(self, location1, location2):
        return abs(location1[0] - location2[0]) + abs(location1[1] - location2[1])

    # Get neighboring cells that are valid
    def get_adjacent_cells(self, cell):
        adjacent = []
        moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for move in moves:
            next_loc = (cell.loc[0] + move[0], cell.loc[1] + move[1])

            if (0 <= next_loc[0] < self.height and
                0 <= next_loc[1] < self.width and
                self.map[next_loc[0]][next_loc[1]] != 1):
                adjacent.append(Cell(next_loc, cell))

        return adjacent

    # Find shortest path using A* algorithm
    def search_path(self, begin, end):
        begin_cell = Cell(begin)
        end_cell = Cell(end)

        to_explore = []
        already_explored = set()

        heapq.heappush(to_explore, begin_cell)

        while to_explore:
            active = heapq.heappop(to_explore)
            already_explored.add(active.loc)

            if active == end_cell:
                route = []
                while active:
                    route.append(active.loc)
                    active = active.prev
                return route[::-1]

            for adjacent in self.get_adjacent_cells(active):
                if adjacent.loc in already_explored:
                    continue

                adjacent.cost_from_start = active.cost_from_start + 1
                adjacent.heuristic_cost = self.calculate_heuristic(adjacent.loc, end)
                adjacent.total_cost = adjacent.cost_from_start + adjacent.heuristic_cost

                if not any(n.loc == adjacent.loc and n.total_cost <= adjacent.total_cost for n in to_explore):
                    heapq.heappush(to_explore, adjacent)

        return None

    # Print the grid with path visualization
    def show_result(self, route, begin, end):
        for row in range(self.height):
            for col in range(self.width):
                if (row, col) == begin:
                    print('S', end=' ')
                elif (row, col) == end:
                    print('G', end=' ')
                elif route and (row, col) in route:
                    print('*', end=' ')
                elif self.map[row][col] == 1:
                    print('#', end=' ')
                else:
                    print('.', end=' ')
            print()

if __name__ == "__main__":
    # Grid definition with obstacles
    map = [
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

    begin = (0, 0)
    end = (9, 9)

    finder = PathFinder(map)
    route = finder.search_path(begin, end)

    if route:
        print("Path found!")
        print(f"Path length: {len(route)}")
        finder.show_result(route, begin, end)
    else:
        print("No path found!")
