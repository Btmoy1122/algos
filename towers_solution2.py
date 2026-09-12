"""
Towers and Disks (multi-peg Tower of Hanoi), Solution 2: binary search
over the split point.

M[.][j] is convex in the split point for fixed i, j, so the arg-min can
be found with a ternary-style binary search instead of a linear scan.

construct_min_moves_matrix(n, k) -> (M, split), O(nk log n) time, O(nk) space
execute_moves(...)                -> Theta(M[n][k]) time, O(n) space
get_solution(n, k)                -> (M[n][k], list_of_moves)
"""


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

    def h(l, i, j):
        return 2 * M[l][j] + M[i - l][j - 1]

    for i in range(2, n + 1):
        for j in range(4, k + 1):
            low, high = 1, i - 1
            while high - low >= 2:
                mid = low + (high - low) // 2
                value = h(mid, i, j) - h(mid + 1, i, j)
                if value > 0:
                    low = mid + 1
                elif value < 0:
                    high = mid
                else:
                    low, high = mid, mid + 1
            val1, val2 = h(low, i, j), h(high, i, j)
            if val1 <= val2:
                M[i][j], split[i][j] = val1, low
            else:
                M[i][j], split[i][j] = val2, high

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
