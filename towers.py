def construct_frame_stewart_matrix(n: int, k: int):
    M = [[0] * (k + 1) for _ in range(n + 1)]
    x = [[0] * (k + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        M[i][3] = 2 ** i - 1
        x[i][3] = i - 1
    for j in range(3, k + 1):
        M[0][j] = 0
        if n >= 1:
            M[1][j] = 1

    def h(l, i, j):
        return 2 * M[l][j] + M[i - l][j - 1]

    for j in range(4, k + 1):
        if n >= 1:
            x[1][j] = 1
        for i in range(2, n + 1):
            prev = x[i - 1][j]
            step = 1 if (prev < i - 1 and h(prev + 1, i, j) <= h(prev, i, j)) else 0
            x[i][j] = min(i - 1, prev + step)
            if x[i][j] == 1:
                M[i][j] = 2 * M[1][j] + M[i - 1][j - 1]
            else:
                M[i][j] = 2 * M[x[i][j]][j] + M[i - x[i][j]][j - 1]

    return M, x


def execute_moves(n, j, source, target, spares, start, split, moves_out):
    if n == 0:
        return
    if n == 1:
        moves_out.append((source, target))
        return
    l = split[n][j]
    intermediate = spares[start]

    # Phase 1: move l disks source -> intermediate, using all j towers
    spares[start] = target
    execute_moves(l, j, source, intermediate, spares, start, split, moves_out)
    spares[start] = intermediate

    # Phase 2: move n-l disks source -> target, using j-1 towers
    execute_moves(n - l, j - 1, source, target, spares, start + 1, split, moves_out)

    # Phase 3: move l disks intermediate -> target, using all j towers
    spares[start] = source
    execute_moves(l, j, intermediate, target, spares, start, split, moves_out)
    spares[start] = intermediate


def get_solution(n: int, k: int):
    M, x = construct_frame_stewart_matrix(n, k)
    spares = list(range(2, k))
    moves = []
    execute_moves(n, k, 1, k, spares, 0, x, moves)
    return M[n][k], moves
