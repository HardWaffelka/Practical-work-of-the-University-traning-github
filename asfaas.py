import heapq

def prim_algorithm(graph):
    n = len(graph) 
    visited = [False] * n 
    min_heap = [(0, 0, -1)]
    total_cost = 0
    mst_edges = []
    
    while min_heap:
        weight, u, parent = heapq.heappop(min_heap)
        if visited[u]:
            continue
        visited[u] = True
        total_cost += weight
        if parent != -1:
            mst_edges.append((parent, u, weight))
            
        for v, w in graph[u]:
            if v < n and not visited[v]:
                heapq.heappush(min_heap, (w, v, u))
                
    return total_cost, mst_edges

graph = {
    0: [(1, 8), (8, 6)],
    1: [(0, 8), (2, 2)],
    2: [(1, 2), (3, 5), (4, 2), (7, 3)],
    3: [(2, 5), (4, 7), (7, 3)],
    4: [(2, 2), (3, 7), (5, 1)],
    5: [(4, 1), (6, 8), (7, 4)],
    6: [(5, 8), (8, 2), (9, 5)],
    7: [(2, 3), (5, 4), (9, 12)],
    8: [(0, 6), (6, 2), (9, 8)],
    9: [(6, 5), (7, 12), (8, 8)],
}

cost, edges = prim_algorithm(graph)
print("Суммарный вес:", cost)
