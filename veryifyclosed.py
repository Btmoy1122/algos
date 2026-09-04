"""
Verification of the closed-form Frame-Stewart formula from:
  Menon, "On the Optimal General Solution to the Multi-Peg Tower of Hanoi"
  (arXiv:2505.12941v5)

Checks performed:
  1. Theorem 3: the closed form reproduces the Frame-Stewart RECURRENCE's
     own values exactly, for all (p, n) tested.
  2. Regime 1 / Regime 2 explicit formulas match the recurrence.
  3. TRUE global optimality: full brute-force search over the actual
     puzzle state space (independent of the recurrence) confirms the
     claimed values really are the minimum possible, on every case
     small enough to compute exhaustively.
  4. The paper's split-point formula (eq. 18), meant to give the optimal
     first move-group size directly -- this is checked against our own
     DP-derived splitpoint table, and FAILS on a concrete example.

Notation: p = number of towers/pegs, n = number of disks
          (matches the paper's own notation)
"""

import math
from collections import deque

# ---------------------------------------------------------------------
# Binomial coefficients via Pascal's triangle -- built with pure addition
# only (no factorial, multiplication, or division), matching the DP style
# used throughout this book.
# ---------------------------------------------------------------------

_PASCAL_MAX = 500
_PASCAL = [[0] * (_PASCAL_MAX + 2) for _ in range(_PASCAL_MAX + 2)]
for _a in range(_PASCAL_MAX + 1):
    _PASCAL[_a][0] = 1
    for _b in range(1, _a + 1):
        _PASCAL[_a][_b] = _PASCAL[_a - 1][_b - 1] + _PASCAL[_a - 1][_b]


def comb(a, b):
    """C(a, b), looked up from a precomputed Pascal's triangle."""
    if b < 0 or b > a:
        return 0
    return _PASCAL[a][b]


# ---------------------------------------------------------------------
# 1. Our own trusted brute-force Frame-Stewart recurrence (ground truth
#    for "does the closed form match the recurrence")
# ---------------------------------------------------------------------

def build_MFS(P, N):
    """M[n][p] = Frame-Stewart recurrence value, plus the DP's own
    splitpoint table (the arg-min l at each cell)."""
    M = [[0] * (P + 1) for _ in range(N + 1)]
    split = [[0] * (P + 1) for _ in range(N + 1)]
    for n in range(N + 1):
        M[n][3] = 2 ** n - 1
        split[n][3] = n - 1
    for p in range(3, P + 1):
        M[0][p] = 0
        if N >= 1:
            M[1][p] = 1
    for p in range(4, P + 1):
        for n in range(2, N + 1):
            best, best_l = math.inf, -1
            for t in range(1, n):
                v = 2 * M[t][p] + M[n - t][p - 1]
                if v < best:
                    best, best_l = v, t
            M[n][p] = best
            split[n][p] = best_l
    return M, split


# ---------------------------------------------------------------------
# 2. The paper's closed form (their eq. 5-9)
# ---------------------------------------------------------------------

def B(p, i):
    """Regime boundary B_p(i) = C(p-1+i, i+1); B_p(-1) := 0."""
    if i == -1:
        return 0
    return comb(p - 1 + i, i + 1)


def regime_index(p, n):
    """i(p,n) := min{j >= 0 : n <= B_p(j)}"""
    i = 0
    while n > B(p, i):
        i += 1
    return i


def S(p, i):
    """S_p(i) := sum_{k=0}^{i} 2^k * C(p+k-2, k); S_p(-1) := 0."""
    if i == -1:
        return 0
    return sum(2 ** k * comb(p + k - 2, k) for k in range(i + 1))


def M_closed(p, n):
    """The closed-form formula (eq. 9)."""
    if n == 0:
        return 0
    i = regime_index(p, n)
    return 2 ** (i + 1) * n - S(p, i)


def closed_form_split(p, n):
    """The paper's claimed optimal split point (eq. 18):
    t* = n - B_{p-1}(i(p,n))"""
    if n <= 1:
        return 0
    i = regime_index(p, n)
    return n - B(p - 1, i)


# ---------------------------------------------------------------------
# 3. TRUE global optimum via full state-space BFS (independent of the
#    recurrence entirely -- the real ground truth for "is this actually
#    the best possible", not just "is this self-consistent")
# ---------------------------------------------------------------------

def true_optimal_bfs(p, n):
    """Exhaustive BFS over every reachable disk/peg configuration.
    Only feasible for small p^n -- this is NOT an algorithm to use in
    practice, it's a verification oracle for small cases."""
    start = tuple([0] * n)
    goal = tuple([p - 1] * n)
    if start == goal:
        return 0
    visited = {start}
    queue = deque([(start, 0)])
    while queue:
        state, dist = queue.popleft()
        tops = {}
        for disk in range(n):
            peg = state[disk]
            if peg not in tops or disk < tops[peg]:
                tops[peg] = disk
        for src_peg, d in tops.items():
            for dst_peg in range(p):
                if dst_peg == src_peg:
                    continue
                if dst_peg not in tops or tops[dst_peg] > d:
                    new_state = list(state)
                    new_state[d] = dst_peg
                    new_state = tuple(new_state)
                    if new_state == goal:
                        return dist + 1
                    if new_state not in visited:
                        visited.add(new_state)
                        queue.append((new_state, dist + 1))
    return None


# ---------------------------------------------------------------------
# Run all checks
# ---------------------------------------------------------------------

if __name__ == "__main__":
    P, N = 12, 40
    M, split_table = build_MFS(P, N)

    print("=" * 70)
    print("CHECK 1: Closed form vs. recurrence (Theorem 3)")
    print("=" * 70)
    mismatches = [
        (p, n, M_closed(p, n), M[n][p])
        for p in range(3, P + 1)
        for n in range(0, N + 1)
        if M_closed(p, n) != M[n][p]
    ]
    print(f"p in [3,{P}], n in [0,{N}]: {len(mismatches)} mismatches")
    if mismatches:
        print("  ", mismatches[:5])

    print("\n" + "=" * 70)
    print("CHECK 2: Regime 1 formula  M(p,n) = 4n - 2p + 1")
    print("=" * 70)
    r1_mismatches = []
    for p in range(3, P + 1):
        lo, hi = p - 1, comb(p, 2)
        for n in range(lo + 1, min(hi, N) + 1):
            formula = 4 * n - 2 * p + 1
            if formula != M[n][p]:
                r1_mismatches.append((p, n, formula, M[n][p]))
    print(f"{len(r1_mismatches)} mismatches")

    print("\n" + "=" * 70)
    print("CHECK 3: Regime 2 formula  M(p,n) = 8n - 2p^2 + 1")
    print("=" * 70)
    r2_mismatches = []
    for p in range(3, P + 1):
        lo, hi = comb(p, 2), comb(p + 1, 3)
        for n in range(lo + 1, min(hi, N) + 1):
            formula = 8 * n - 2 * p ** 2 + 1
            if formula != M[n][p]:
                r2_mismatches.append((p, n, formula, M[n][p]))
    print(f"{len(r2_mismatches)} mismatches")

    print("\n" + "=" * 70)
    print("CHECK 4: TRUE global optimum via full state-space BFS")
    print("(independent of the recurrence -- the real test)")
    print("=" * 70)
    bfs_cases = [(4, 4), (4, 6), (4, 7), (4, 8), (4, 9), (4, 10),
                 (5, 5), (6, 6), (7, 7)]
    for p, n in bfs_cases:
        claimed = M_closed(p, n)
        actual = true_optimal_bfs(p, n)
        status = "MATCH" if actual == claimed else "MISMATCH !!"
        print(f"  p={p}, n={n}: claimed={claimed}, true_optimum={actual}  [{status}]")

    print("\n" + "=" * 70)
    print("CHECK 5: Split-point formula (eq. 18) -- KNOWN TO FAIL")
    print("=" * 70)
    p, n = 5, 11
    paper_split = closed_form_split(p, n)
    our_split = split_table[n][p]
    paper_cost = 2 * M[paper_split][p] + M[n - paper_split][p - 1]
    true_cost = M[n][p]
    print(f"  p={p}, n={n}")
    print(f"  paper's formula says split at l={paper_split} -> costs {paper_cost} moves")
    print(f"  our verified DP says split at l={our_split} -> costs {true_cost} moves")
    print(f"  paper's split is {'OPTIMAL' if paper_cost == true_cost else 'SUBOPTIMAL -- DOES NOT MATCH'}")