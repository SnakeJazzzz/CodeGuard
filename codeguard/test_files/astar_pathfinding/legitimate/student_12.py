#!/usr/bin/env python3
# A* with custom heap implementation
# Student 12

class MinHeap:
    def __init__(self):
        self.heap = []

    def push(self, item):
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)

    def pop(self):
        if not self.heap:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()

        root = self.heap[0]
        self.heap[0] = self.heap.pop()
        self._sift_down(0)
        return root

    def _sift_up(self, idx):
        parent = (idx - 1) // 2
        if idx > 0 and self.heap[idx][0] < self.heap[parent][0]:
            self.heap[idx], self.heap[parent] = self.heap[parent], self.heap[idx]
            self._sift_up(parent)

    def _sift_down(self, idx):
        smallest = idx
        left = 2 * idx + 1
        right = 2 * idx + 2

        if left < len(self.heap) and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < len(self.heap) and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right

        if smallest != idx:
            self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
            self._sift_down(smallest)

    def __len__(self):
        return len(self.heap)

def heuristic_func(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar_custom(grid, start, goal):
    heap = MinHeap()
    heap.push((0, start, [start]))

    visited = set()

    while len(heap) > 0:
        f, current, path = heap.pop()

        if current in visited:
            continue

        visited.add(current)

        if current == goal:
            return path

        x, y = current

        neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]

        for nx, ny in neighbors:
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                if grid[nx][ny] == 0 and (nx, ny) not in visited:
                    new_path = path + [(nx, ny)]
                    g = len(new_path) - 1
                    h = heuristic_func((nx, ny), goal)
                    f = g + h
                    heap.push((f, (nx, ny), new_path))

    return None

grid_map = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
]

result_path = astar_custom(grid_map, (0, 0), (7, 7))

if result_path:
    print("Path:", result_path)
    print("Steps:", len(result_path))

    for i in range(len(grid_map)):
        for j in range(len(grid_map[0])):
            if (i, j) == (0, 0):
                print('S', end='')
            elif (i, j) == (7, 7):
                print('G', end='')
            elif (i, j) in result_path:
                print('*', end='')
            elif grid_map[i][j] == 1:
                print('#', end='')
            else:
                print('.', end='')
        print()
else:
    print("No path")
