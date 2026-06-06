"""Pure-Python, layer-aware force-directed layout.

Computes 2D positions for nodes so the renderers (interactive canvas and static SVG) share one
deterministic layout. Uses numpy when available for speed, with a dependency-free fallback.
Nodes are gently pulled toward a per-layer cluster center so layers separate visually, echoing
the original dashboard's clustered look.
"""

from __future__ import annotations

import math
import random

WIDTH = 1400.0
HEIGHT = 900.0


# --- Layered "swimlane" layout: layers become stacked container boxes of gridded cards. -----
CARD_W = 196.0
CARD_H = 60.0
_GAP_X = 26.0
_GAP_Y = 22.0
_PAD = 18.0
_HEADER = 36.0
_LANE_GAP = 48.0
_LEFT = 48.0
_TOP = 48.0
_MAX_COLS = 8
_UNASSIGNED = 1_000_000

# Order within a lane: a file first, then its classes, then its functions.
_TYPE_RANK = {
    "file": 0, "config": 0, "document": 0, "service": 0, "pipeline": 0, "table": 0,
    "schema": 0, "resource": 0, "endpoint": 0, "module": 0, "class": 1, "function": 2, "concept": 3,
}


def compute_layered_layout(records, n_layers):
    """records: list of {id, layer(int or -1), type, filePath, name}.

    Returns (positions{id:(cx,cy)}, containers[{layerKey,x,y,w,h,count}], CARD_W, CARD_H).
    """
    import math
    from collections import defaultdict

    groups: dict[int, list] = defaultdict(list)
    for r in records:
        layer = r.get("layer")
        key = layer if isinstance(layer, int) and layer >= 0 else _UNASSIGNED
        groups[key].append(r)

    positions: dict[str, tuple[float, float]] = {}
    containers: list[dict] = []
    y = _TOP
    for key in sorted(groups):
        members = groups[key]
        members.sort(key=lambda r: (r.get("filePath") or "", _TYPE_RANK.get(r["type"], 9), r["name"]))
        n = len(members)
        cols = min(_MAX_COLS, max(1, int(math.ceil(math.sqrt(n * 1.7)))))
        rows = int(math.ceil(n / cols))
        inner_w = cols * CARD_W + (cols - 1) * _GAP_X
        inner_h = rows * CARD_H + (rows - 1) * _GAP_Y
        cw = inner_w + 2 * _PAD
        ch = inner_h + _PAD + _HEADER
        containers.append({"layerKey": key, "x": _LEFT, "y": y, "w": cw, "h": ch, "count": n})
        for i, r in enumerate(members):
            rr, cc = divmod(i, cols)
            cx = _LEFT + _PAD + cc * (CARD_W + _GAP_X) + CARD_W / 2
            cy = y + _HEADER + rr * (CARD_H + _GAP_Y) + CARD_H / 2
            positions[r["id"]] = (round(cx, 1), round(cy, 1))
        y += ch + _LANE_GAP
    return positions, containers, CARD_W, CARD_H


def compute_layout(node_ids, edges, layer_of, width=WIDTH, height=HEIGHT, seed=42):
    """node_ids: list[str]; edges: list[(src, tgt, weight)]; layer_of: dict[id->layer_key].

    Returns dict[id] -> (x, y).
    """
    n = len(node_ids)
    if n == 0:
        return {}
    if n == 1:
        return {node_ids[0]: (width / 2, height / 2)}

    idx = {nid: i for i, nid in enumerate(node_ids)}
    clusters = sorted({layer_of.get(nid, "_") for nid in node_ids}, key=str)
    k = len(clusters)
    cx, cy = width / 2, height / 2
    radius = min(width, height) * 0.34
    center = {}
    for ci, c in enumerate(clusters):
        if k == 1:
            center[c] = (cx, cy)
        else:
            ang = 2 * math.pi * ci / k
            center[c] = (cx + radius * math.cos(ang), cy + radius * math.sin(ang))

    rng = random.Random(seed)
    init = []
    for nid in node_ids:
        ccx, ccy = center[layer_of.get(nid, clusters[0])]
        init.append((ccx + rng.uniform(-60, 60), ccy + rng.uniform(-60, 60)))

    cluster_center = [center[layer_of.get(nid, clusters[0])] for nid in node_ids]
    edge_list = [(idx[s], idx[t], w) for (s, t, w) in edges if s in idx and t in idx]

    try:
        if n <= 1200:
            import numpy as np  # noqa
            pos = _layout_numpy(init, edge_list, cluster_center, n, width, height, seed)
        else:
            pos = _layout_python(init, edge_list, cluster_center, n, width, height, rng)
    except Exception:
        pos = _layout_python(init, edge_list, cluster_center, n, width, height, rng)

    return {nid: (round(pos[i][0], 1), round(pos[i][1], 1)) for i, nid in enumerate(node_ids)}


def _iters(n: int) -> int:
    if n <= 200:
        return 140
    if n <= 600:
        return 90
    if n <= 1200:
        return 60
    return 30


def _layout_numpy(init, edges, cluster_center, n, width, height, seed):
    import numpy as np

    P = np.array(init, dtype=float)
    C = np.array(cluster_center, dtype=float)
    k = math.sqrt((width * height) / n) * 0.85

    A = np.zeros((n, n), dtype=float)
    for i, j, w in edges:
        A[i, j] = A[j, i] = max(A[i, j], 0.4 + 0.6 * w)

    temp = width * 0.10
    for _ in range(_iters(n)):
        diff = P[:, None, :] - P[None, :, :]
        dist = np.sqrt((diff ** 2).sum(-1)) + 1e-6
        unit = diff / dist[..., None]
        rep = (k * k) / dist
        np.fill_diagonal(rep, 0.0)
        disp = (unit * rep[..., None]).sum(1)
        attr = (dist * dist / k) * A
        disp -= (unit * attr[..., None]).sum(1)
        disp += (C - P) * 0.012
        dl = np.sqrt((disp ** 2).sum(-1)) + 1e-9
        lim = np.minimum(dl, temp)
        P += disp / dl[:, None] * lim[:, None]
        P[:, 0] = np.clip(P[:, 0], 24, width - 24)
        P[:, 1] = np.clip(P[:, 1], 24, height - 24)
        temp *= 0.95
    return P.tolist()


def _layout_python(init, edges, cluster_center, n, width, height, rng):
    pos = [list(p) for p in init]
    adj = [[] for _ in range(n)]
    for i, j, w in edges:
        adj[i].append((j, 0.4 + 0.6 * w))
        adj[j].append((i, 0.4 + 0.6 * w))
    k = math.sqrt((width * height) / n) * 0.85
    temp = width * 0.10
    for _ in range(_iters(n)):
        disp = [[0.0, 0.0] for _ in range(n)]
        for i in range(n):
            xi, yi = pos[i]
            for j in range(i + 1, n):
                dx = xi - pos[j][0]
                dy = yi - pos[j][1]
                d2 = dx * dx + dy * dy
                if d2 < 1e-4:
                    dx = rng.random() - 0.5
                    dy = rng.random() - 0.5
                    d2 = dx * dx + dy * dy + 1e-4
                d = math.sqrt(d2)
                f = (k * k) / d
                fx, fy = dx / d * f, dy / d * f
                disp[i][0] += fx
                disp[i][1] += fy
                disp[j][0] -= fx
                disp[j][1] -= fy
        for i in range(n):
            xi, yi = pos[i]
            for (j, w) in adj[i]:
                if j <= i:
                    continue
                dx = xi - pos[j][0]
                dy = yi - pos[j][1]
                d = math.sqrt(dx * dx + dy * dy) + 1e-6
                f = d * d / k * w
                fx, fy = dx / d * f, dy / d * f
                disp[i][0] -= fx
                disp[i][1] -= fy
                disp[j][0] += fx
                disp[j][1] += fy
        for i in range(n):
            ccx, ccy = cluster_center[i]
            disp[i][0] += (ccx - pos[i][0]) * 0.012
            disp[i][1] += (ccy - pos[i][1]) * 0.012
        for i in range(n):
            dx, dy = disp[i]
            d = math.sqrt(dx * dx + dy * dy) + 1e-9
            lim = min(d, temp)
            pos[i][0] = min(width - 24, max(24, pos[i][0] + dx / d * lim))
            pos[i][1] = min(height - 24, max(24, pos[i][1] + dy / d * lim))
        temp *= 0.95
    return pos
