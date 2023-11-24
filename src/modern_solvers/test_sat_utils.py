from itertools import combinations
from itertools import product
from itertools import starmap
from math import factorial
from pprint import pprint

from .sat_utils import *


def cnf_eq(c1, c2):
    return set(map(frozenset, c1)) == set(map(frozenset, c2))


def comb(clause):
    return "(" + ", ".join(sorted(clause)) + ")"


def cnr(n, r):
    return factorial(n) // factorial(r) // factorial(n - r)


elements = (
    "x\N{subscript one}",
    "x\N{subscript two}",
    "x\N{subscript three}",
    "x\N{subscript four}",
    "x\N{subscript five}",
    "x\N{subscript six}",
)
for n in range(len(elements) + 1):
    ans_eq = solve_all(Q(elements) == n)
    assert all(len(row) == n for row in ans_eq)
    assert len(ans_eq) == cnr(len(elements), n)
for n in range(len(elements)):
    ans_gt = solve_all(Q(elements) > n)
    assert all(len(row) > n for row in ans_gt)
    assert len(ans_gt) == sum(
        cnr(len(elements), k) for k in range(n + 1, len(elements) + 1)
    )
for n in range(1, len(elements) + 1):
    ans_lt = solve_all(Q(elements) < n)
    assert all(len(row) < n for row in ans_lt)
    assert len(ans_lt) == sum(cnr(len(elements), k) for k in range(n))
for n in range(1, len(elements) + 1):
    ans_ge = solve_all(Q(elements) >= n)
    assert all(len(row) >= n for row in ans_ge)
    assert len(ans_ge) == sum(
        cnr(len(elements), k) for k in range(n, len(elements) + 1)
    )
for n in range(len(elements)):
    ans_le = solve_all(Q(elements) <= n)
    assert all(len(row) <= n for row in ans_le)
    assert len(ans_le) == sum(cnr(len(elements), k) for k in range(n + 1))

assert all(set(row) == set(elements) for row in solve_all(all_of(elements)))
assert all(len(set(row) & set(elements)) >= 1 for row in solve_all(some_of(elements)))
assert all(len(set(row) & set(elements)) == 1 for row in solve_all(one_of(elements)))
assert all(len(set(row) & set(elements)) == 0 for row in solve_all(none_of(elements)))

assert set(all_of(elements)) == set(from_dnf([elements]))
assert set(none_of(elements)) == set(all_of(list(map(neg, elements))))
assert set(some_of(elements)) == {tuple(elements)}
assert set(basic_fact("A")) == {("A",)}
assert set(basic_fact("A") + basic_fact("B")) == {("A",), ("B",)}


def from_dnf_no_cancel(groups) -> "cnf":
    "Convert from or-of-ands to and-of-ors"
    # Variant that doesn't seek to eliminate positive and negative of same literal
    cnf = {frozenset()}
    for group in groups:
        literals = {frozenset([literal]) for literal in group}
        cnf = set(starmap(frozenset.union, product(cnf, literals)))
    return list(map(tuple, cnf))


dnf = [["A", "B", "E"], ["~A", "C", "D"], ["~A", "E", "~D"]]
cnf_biggest = list(product(*dnf))
cnf_big = from_dnf_no_cancel(dnf)
cnf_little = from_dnf(dnf)
assert len(cnf_biggest) > len(cnf_big) > len(cnf_little)
assert set(map(frozenset, solve_all(cnf_biggest))) == set(
    map(frozenset, solve_all(cnf_big))
)
assert set(map(frozenset, solve_all(cnf_big))) == set(
    map(frozenset, solve_all(cnf_little))
)

# https://hackrly.wordpress.com/2018/01/24/conjunctive-normal-formcnf-and-disjunctive-normal-formdnf-from-truth-table-explained/#more-42
dnf = [("x", "y", "z"), ("x", "~y", "~z"), ("~x", "y", "~z"), ("~x", "~y", "z")]
cnf = [("~x", "~y", "z"), ("~x", "y", "~z"), ("x", "~y", "~z"), ("x", "y", "z")]
assert set(map(frozenset, from_dnf(dnf))) == set(map(frozenset, cnf))

print("Tests passed")
