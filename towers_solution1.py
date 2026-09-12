"""
Towers and Disks (multi-peg Tower of Hanoi), Solution 1: brute-force
linear scan over the split point.

bottom_up(n, k)               -> M[n][k] only, O(n^2 k) time, O(nk) space
space_optimized(n, k)         -> M[n][k] only, O(n^2 k) time, O(n) space
construct_min_moves_matrix(n, k) -> (M, split), O(n^2 k) time, O(nk) space
execute_moves(...)            -> Theta(M[n][k]) time, O(n) space
get_solution(n, k)            -> (M[n][k], list_of_moves)
"""

import math


def bottom_up(n: int, k: int) -> int:
    M = [[0] * (k + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        M[i][3] = 2 ** i - 1
    for j in range(3, k + 1):
        M[0][j] = 0
        if n >= 1:
            M[1][j] = 1

    for i in range(2, n + 1):
        for j in range(4, k + 1):
            M[i][j] = min(2 * M[l][j] + M[i - l][j - 1] for l in range(1, i))

    return M[n][k]


def space_optimized(n: int, k: int) -> int:
    curr = [2 ** i - 1 for i in range(n + 1)]
    nxt = [0] * (n + 1)

    for j in range(4, k + 1):
        nxt[0] = 0
        if n >= 1:
            nxt[1] = 1
        for i in range(2, n + 1):
            nxt[i] = min(2 * nxt[l] + curr[i - l] for l in range(1, i))
        curr, nxt = nxt, curr

    return curr[n]


def construct_min_moves_matrix(n: int, k: int):
    M = [[0] * (k + 1) for _ in range(n + 1)]
    split = [[0] * (k + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        M[i][3] = 2 ** i - 1
        split[i][3] = i - 1
    for j in range(3, k + 1):
        M[0][j] = 0
        split[0][j] = 0
        if n >= 1:
            M[1][j] = 1
            split[1][j] = 0

    for i in range(2, n + 1):
        for j in range(4, k + 1):
            M[i][j] = math.inf
            for l in range(1, i):
                moves = 2 * M[l][j] + M[i - l][j - 1]
                if moves < M[i][j]:
                    M[i][j] = moves
                    split[i][j] = l

    return M, split


def execute_moves(n, j, source, target, start):
    if n == 0:
        return
    if n == 1:
        moves.append((source, target))
        return
    l = split[n][j]
    intermediate = spares[start]

    # Phase 1: move l disks source -> intermediate, using all j towers
    spares[start] = target
    execute_moves(l, j, source, intermediate, start)
    spares[start] = intermediate

    # Phase 2: move n-l disks source -> target, using j-1 towers
    execute_moves(n - l, j - 1, source, target, start + 1)

    # Phase 3: move l disks intermediate -> target, using all j towers
    spares[start] = source
    execute_moves(l, j, intermediate, target, start)
    spares[start] = intermediate


def get_solution(n: int, k: int):
    global M, split, spares, moves
    M, split = construct_min_moves_matrix(n, k)
    spares = list(range(2, k))
    moves = []
    execute_moves(n, k, 1, k, 0)
    return M[n][k], moves
