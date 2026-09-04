"""
Test suite for towers.py (Solution 3: two-pointer O(nk) construction).

Run with:  pytest test_towers.py -v

Includes three independent oracles:
  1. An independently-written brute-force recurrence (Solution 1 style).
  2. The paper's closed form (Menon, arXiv:2505.12941v5), used only to
     cross-check the VALUE M(p,n) -- not the move reconstruction, since
     the paper's own split-point formula was found to be unreliable.
  3. A move-sequence validator that simulates the actual moves and checks
     every rule of the puzzle is obeyed.

Note on binomial coefficients: rather than using a library factorial-based
routine, coefficients here are built via Pascal's identity
C(a,b) = C(a-1,b-1) + C(a-1,b) -- pure addition, no multiplication,
division, or factorial call of any kind.
"""

import math
import random
import pytest
from towers import construct_frame_stewart_matrix, execute_moves, get_solution


# ---------------------------------------------------------------------
# Oracle 1: independent brute-force recurrence (deliberately simple,
# never shares code with towers.py's two-pointer logic)
# ---------------------------------------------------------------------

def brute_force_M(n_max, k_max):
    M = [[0] * (k_max + 1) for _ in range(n_max + 1)]
    for i in range(n_max + 1):
        M[i][3] = 2 ** i - 1
    for p in range(3, k_max + 1):
        M[0][p] = 0
        if n_max >= 1:
            M[1][p] = 1
    for p in range(4, k_max + 1):
        for n in range(2, n_max + 1):
            best = math.inf
            for t in range(1, n):
                v = 2 * M[t][p] + M[n - t][p - 1]
                best = min(best, v)
            M[n][p] = best
    return M


# ---------------------------------------------------------------------
# Oracle 2: the paper's closed form, using Pascal's-triangle binomial
# coefficients (addition only -- no factorial-style computation)
# ---------------------------------------------------------------------

def build_pascal_triangle(max_a):
    C = [[0] * (max_a + 2) for _ in range(max_a + 2)]
    for a in range(max_a + 1):
        C[a][0] = 1
        for b in range(1, a + 1):
            C[a][b] = C[a - 1][b - 1] + C[a - 1][b]
    return C

_PASCAL_MAX = 400
_PASCAL = build_pascal_triangle(_PASCAL_MAX)

def binom(a, b):
    if b < 0 or b > a:
        return 0
    return _PASCAL[a][b]

def boundary(p, i):
    if i == -1:
        return 0
    return binom(p - 1 + i, i + 1)

def regime_index(p, n):
    i = 0
    while n > boundary(p, i):
        i += 1
    return i

def correction_sum(p, i):
    if i == -1:
        return 0
    return sum(2 ** k * binom(p + k - 2, k) for k in range(i + 1))

def closed_form_M(p, n):
    if n == 0:
        return 0
    i = regime_index(p, n)
    return 2 ** (i + 1) * n - correction_sum(p, i)


# ---------------------------------------------------------------------
# Oracle 3: move-sequence validator -- actually simulates the puzzle
# ---------------------------------------------------------------------

def validate_moves(n, k, moves):
    """Replays every move on a virtual set of k towers, checking every
    rule of the puzzle, and confirms the final state is correct."""
    pegs = [[] for _ in range(k + 1)]  # 1-indexed
    pegs[1] = list(range(n, 0, -1))  # disk n (largest) at bottom, 1 on top

    for (src, dst) in moves:
        assert pegs[src], f"tried to move from empty peg {src}"
        disk = pegs[src][-1]
        if pegs[dst]:
            assert pegs[dst][-1] > disk, (
                f"illegal move: disk {disk} onto smaller disk {pegs[dst][-1]}"
            )
        pegs[src].pop()
        pegs[dst].append(disk)

    for p in range(1, k + 1):
        if p != k:
            assert pegs[p] == [], f"peg {p} not empty at the end: {pegs[p]}"
    assert pegs[k] == list(range(n, 0, -1)), "target peg does not hold all disks in order"


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------

def test_M_matches_brute_force():
    N, K = 60, 12
    Mb = brute_force_M(N, K)
    M, _ = construct_frame_stewart_matrix(N, K)
    for p in range(3, K + 1):
        for n in range(0, N + 1):
            assert M[n][p] == Mb[n][p], f"M[{n}][{p}]: {M[n][p]} != {Mb[n][p]}"


def test_M_matches_closed_form_paper_oracle():
    N, K = 200, 15
    M, _ = construct_frame_stewart_matrix(N, K)
    for p in range(4, K + 1):
        for n in range(0, N + 1):
            assert M[n][p] == closed_form_M(p, n), (
                f"M[{n}][{p}]: {M[n][p]} != closed_form {closed_form_M(p, n)}"
            )


@pytest.mark.parametrize("n,k", [(1, 4), (2, 4), (5, 4), (5, 5), (10, 4),
                                  (10, 6), (15, 5), (20, 7)])
def test_get_solution_produces_valid_moves(n, k):
    total, moves = get_solution(n, k)
    assert len(moves) == total
    validate_moves(n, k, moves)


def test_get_solution_random_stress():
    random.seed(0)
    for _ in range(50):
        n = random.randint(1, 20)
        k = random.randint(4, 8)
        total, moves = get_solution(n, k)
        assert len(moves) == total
        validate_moves(n, k, moves)


def test_pascal_binomials_match_stdlib():
    """Confirms the addition-only Pascal's-triangle binomials used as the
    cross-check oracle are exactly correct, not an approximation."""
    for a in range(0, 100):
        for b in range(0, a + 1):
            assert binom(a, b) == math.comb(a, b)


def test_base_cases():
    M, x = construct_frame_stewart_matrix(10, 5)
    assert M[0][4] == 0
    assert M[1][4] == 1
    assert M[5][3] == 2 ** 5 - 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])