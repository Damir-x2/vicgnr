from __future__ import annotations

import random
from typing import Callable

L = (
    ("\u03A6", "harmed", 2),  # Phi
    ("\u03A8", "stable", 1),  # Psi
    ("\u03A9", "unharmed", 0),  # Omega
)
R = tuple(one[0] for one in L)

F = {
    1: ["A", "F", "L", "P", "T", "X"],
    2: ["E", "R", "Y", "B", "D"],
    3: ["N", "V", "W", "O", "Q"],
    4: ["M", "K", "Z", "G", "J", "C"],
    5: ["I", "5", "2", "7", "0"],
}

C = {
    "black": -2,
    "red": -1,
    "yellow": 0,
    "green": 1,
    "blue": 2,
}

OK_SUM = (0, 1, 2)
SUM_TXT = {2: "harmed", 1: "stable", 0: "unharmed"}


def _fix_lvl(lvl):
    return max(1, min(5, lvl))


def _get_fake_ltrs(lvl):
    lvl = _fix_lvl(lvl)
    out = []
    for i in range(1, lvl + 1):
        out.extend(F[i])
    return [x for x in out if x not in R]


def _sum_rings(rings):
    return sum(C[c] for c in rings)


def _rnd_rings(rnd):
    cls = list(C.keys())
    return [rnd.choice(cls) for _ in range(5)]


def _make_rings(rnd, ok: Callable[[int], bool], max_try=5000):
    for _ in range(max_try):
        rings = _rnd_rings(rnd)
        val = _sum_rings(rings)
        if ok(val):
            return rings, val
    raise RuntimeError(
        "Could not generate visual victim with the required constraints."
    )


def gen_ltr_items(real_n, fake_n, lvl, rnd):
    items = []
    pool = _get_fake_ltrs(lvl)

    for _ in range(real_n):
        ch, st, kits = rnd.choice(L)
        items.append(
            {
                "item_type": "letter",
                "is_real": True,
                "payload": {"letter": ch, "rescue_kits_count": kits},
                "value_sum": None,
                "status": st,
            }
        )

    for _ in range(fake_n):
        ch = rnd.choice(pool)
        items.append(
            {
                "item_type": "letter",
                "is_real": False,
                "payload": {"letter": ch, "rescue_kits_count": 0},
                "value_sum": None,
                "status": "false",
            }
        )

    return items


def gen_vis_items(real_n, fake_n, rnd):
    items = []

    for _ in range(real_n):
        need = rnd.choice(OK_SUM)
        rings, val = _make_rings(rnd, ok=lambda s: s == need)
        items.append(
            {
                "item_type": "visual",
                "is_real": True,
                "payload": {"rings": rings, "rescue_kits_count": val},
                "value_sum": val,
                "status": SUM_TXT[val],
            }
        )

    for _ in range(fake_n):
        rings, val = _make_rings(rnd, ok=lambda s: s not in OK_SUM)
        items.append(
            {
                "item_type": "visual",
                "is_real": False,
                "payload": {"rings": rings, "rescue_kits_count": 0},
                "value_sum": val,
                "status": "false",
            }
        )

    return items


def gen_kit_items(real_ltr, fake_ltr, real_vis, fake_vis, lvl, seed=None):
    rnd = random.Random(seed)

    arr = []
    arr.extend(gen_ltr_items(real_ltr, fake_ltr, lvl, rnd))
    arr.extend(gen_vis_items(real_vis, fake_vis, rnd))

    rnd.shuffle(arr)
    for i, one in enumerate(arr, start=1):
        one["position"] = i

    return arr
