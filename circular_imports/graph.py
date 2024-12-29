from typing import List, Set, Tuple, Dict


def find_cycles(graph: Set[Tuple[str, str]]) -> Set[List[str]]:
    graph_: Dict[str, Set[str]] = {}
    for a, b in graph:
        if a not in graph_:
            graph_[a] = set()
        graph_[a].add(b)

    cycles: List[List[str]] = []
    visited: Set[str] = set()

    def dfs(node: str, visited: Set[str], path: List[str]) -> List[List[str]]:
        visited.add(node)
        path.append(node)
        if node in graph_:
            for neighbor in graph_[node]:
                if neighbor not in visited:
                    dfs(neighbor, visited, path)
                elif neighbor in path:
                    cycles.append(normalize_cycle(path[path.index(neighbor) :]))
        path.pop()
        return cycles

    for node in graph_:
        if node not in visited:
            dfs(node, visited, [])
    cycles.sort()
    return cycles


def normalize_cycle(cycle: List[str]) -> List[str]:
    min_index = cycle.index(min(cycle))
    return cycle[min_index:] + cycle[:min_index]
