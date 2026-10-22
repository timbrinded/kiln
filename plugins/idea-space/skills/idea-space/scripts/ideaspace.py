#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11,<3.14"
# dependencies = [
#     "fastembed>=0.7",
#     "numpy>=1.26",
#     "scikit-learn>=1.5",
#     "scipy>=1.13",
#     "threadpoolctl>=3.1",
#     "umap-learn>=0.5.7",
#     "matplotlib>=3.9",
# ]
# ///
"""Map a corpus by meaning, find its empty space, and measure new ideas against it.

  build      ingest a corpus file, embed it, compute nearest-twin stats and neighbourhoods
  survey     the landscape: neighbourhoods, demand, crowded corners, loners
  neighbors  nearest and farthest items to a title or free text
  calibrate  paraphrase baseline ("copy line") and generic "mush" anchors
  blend      blend related seeds, push away from everything, write a brief
  gaps       find holes in the flattened map and write a brief for each
  brief      print a saved brief
  measure    embed a draft, report where it landed and whether it is new enough
  report     rank measured ideas into a markdown report
  plot       render the map (neighbourhoods, holes, ideas) to PNG

Workspace files: corpus.jsonl, emb.npy, stats.npz, meta.json, map.npy, mush.npy,
briefs/<id>.json + .npy, ideas.jsonl.
"""

import argparse
import csv
import hashlib
import html
import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import NoReturn

import numpy as np
from threadpoolctl import threadpool_limits

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"  # fast on CPU; bge-base/large map more finely
DEFAULT_ACCEPT = 0.75  # a draft must be lonelier than this share of the corpus


def die(msg: str) -> NoReturn:
    sys.exit(f"error: {msg}")


def note(msg: str):
    print(msg, file=sys.stderr, flush=True)


def unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def pct(p: float) -> str:
    """Percent floored to 0.1, so the loneliest item reads 99.9% rather than a rounded-up 100%."""
    return f"{math.floor(p * 1000) / 10:.1f}%"


def family(title: str) -> str:
    """Crude series key (first significant title word), so a blend is not four entries of one franchise."""
    words = [w for w in re.findall(r"\w+", title.lower()) if w not in {"the", "a", "an", "of"}]
    return words[0] if words else title


def clip(s: str, n: int) -> str:
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# ---------------------------------------------------------------- ingest


def read_records(path: Path) -> list[dict]:
    if path.suffix == ".csv":
        csv.field_size_limit(sys.maxsize)
        with path.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    if path.suffix in (".jsonl", ".ndjson"):
        with path.open(encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):  # {key: record}
            return [{"_key": k, **v} for k, v in data.items() if isinstance(v, dict)]
        return data
    die(f"unsupported corpus format {path.suffix!r}; use .csv, .json or .jsonl")


def flatten(v) -> str:
    if v is None:
        return ""
    if isinstance(v, dict):
        return ", ".join(map(str, v))
    if isinstance(v, list):
        return ", ".join(s for s in map(flatten, v) if s)
    s = html.unescape(re.sub(r"<[^>]+>", " ", str(v)))
    return re.sub(r"\s+", " ", s).strip()


def split_tags(v) -> list[str]:
    if isinstance(v, dict):
        return [str(k) for k in v]
    if isinstance(v, list):
        return [t for t in map(flatten, v) if t]
    return [t.strip() for t in re.split(r"[,;|]", flatten(v)) if t.strip()]


def to_number(v) -> float:
    try:
        return float(str(v).replace(",", ""))
    except ValueError:
        return 0.0


def normalise(records, text_fields, title_field, tag_fields, pop_fields, min_words):
    for f in [*text_fields, *([title_field] if title_field else []), *tag_fields, *pop_fields]:
        if not any(f in r for r in records[:500]):
            die(f"field {f!r} not found; available: {', '.join(records[0].keys())}")
    items, seen, short, dupes = [], set(), 0, Counter()
    for r in records:
        text = "\n".join(t for t in (flatten(r.get(f)) for f in text_fields) if t)
        if len(text.split()) < min_words:
            short += 1
            continue
        if text.lower() in seen:
            dupes[flatten(r.get(title_field)) if title_field else clip(text, 40)] += 1
            continue
        seen.add(text.lower())
        items.append(
            {
                "id": len(items),
                "title": flatten(r.get(title_field)) if title_field else clip(text, 60),
                "text": text,
                "tags": [t for f in tag_fields for t in split_tags(r.get(f))],
                "pop": sum(to_number(r.get(f)) for f in pop_fields),
            }
        )
    note(f"kept {len(items)} items; dropped {short} under {min_words} words, {dupes.total()} exact duplicates")
    if dupes:
        note("  most duplicated: " + ", ".join(f"{clip(t, 30)} ×{n}" for t, n in dupes.most_common(5)))
    return items


# ---------------------------------------------------------------- geometry


def embed_texts(model, texts: list[str], progress: bool = False) -> np.ndarray:
    """Unit vectors in input order. Batches by length so short texts are not padded to long ones."""
    order = np.argsort([len(t) for t in texts], kind="stable")
    vecs, t0 = [], time.time()
    for n, v in enumerate(model.embed([texts[i] for i in order], batch_size=64), 1):
        vecs.append(v)
        if progress and n % 2000 == 0:
            note(f"  {n}/{len(texts)} ({time.time() - t0:.0f}s)")
    E = np.empty((len(texts), len(vecs[0])), np.float32)
    E[order] = vecs
    return unit(E)


def top_k(Q: np.ndarray, E: np.ndarray, k: int, exclude_self: bool = False):
    """Top-k cosine neighbours of each row of Q in E (both unit-normalised)."""
    k = min(k, len(E) - 1)
    chunk = max(1, int(5e7 // len(E)))
    sims = np.empty((len(Q), k), np.float32)
    idx = np.empty((len(Q), k), np.int64)
    for s in range(0, len(Q), chunk):
        S = Q[s : s + chunk] @ E.T
        if exclude_self:
            r = np.arange(len(S))
            S[r, r + s] = -np.inf
        part = np.argpartition(-S, k - 1, axis=1)[:, :k]
        ps = np.take_along_axis(S, part, 1)
        order = np.argsort(-ps, axis=1)
        idx[s : s + len(S)] = np.take_along_axis(part, order, 1)
        sims[s : s + len(S)] = np.take_along_axis(ps, order, 1)
    return sims, idx


def quantiles(x: np.ndarray, qs=(1, 10, 25, 50, 75, 90, 99)) -> dict:
    return {f"p{q}": float(np.percentile(x, q)) for q in qs}


def map_bounds(xy: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.percentile(xy, 0.5, axis=0), np.percentile(xy, 99.5, axis=0)


def find_holes(xy: np.ndarray, top: int, grid: int = 384) -> list[dict]:
    """Empty patches of the 2-D map with items on every side, largest first."""
    from scipy.ndimage import distance_transform_edt, maximum_filter
    from scipy.spatial import KDTree

    lo, hi = map_bounds(xy)
    span = float((hi - lo).max())
    keep = np.flatnonzero(((xy >= lo) & (xy <= hi)).all(1))  # far outliers would waste the grid
    u = (xy[keep] - lo) / span
    cells = np.minimum((u * grid).astype(int), grid - 1)
    occupied = np.zeros((grid, grid), bool)
    occupied[cells[:, 0], cells[:, 1]] = True
    dist = np.asarray(distance_transform_edt(~occupied)) / grid
    peaks = np.argwhere((dist == maximum_filter(dist, size=5)) & (dist > 2 / grid))
    peaks = peaks[np.argsort(-dist[peaks[:, 0], peaks[:, 1]])]
    tree = KDTree(u)
    holes: list[dict] = []
    for gx, gy in peaks:
        r = float(dist[gx, gy])
        ctr = (np.array([gx, gy]) + 0.5) / grid
        if any(np.linalg.norm(ctr - h["ctr"]) < (h["r"] + r) for h in holes):
            continue
        near = tree.query_ball_point(ctr, 2.5 * r)
        d = u[near] - ctr
        sectors = ((np.arctan2(d[:, 1], d[:, 0]) + np.pi) / (2 * np.pi) * 8).astype(int) % 8
        if (np.bincount(sectors, minlength=8) < 2).any():  # open on some side: not a hole
            continue
        _, rim = tree.query(ctr, 12)
        holes.append({"ctr": ctr, "r": r, "rim": [int(keep[i]) for i in np.atleast_1d(rim)]})
        if len(holes) >= top:
            break
    for h in holes:
        h["xy"] = (h["ctr"] * span + lo).tolist()
        h["radius_xy"] = h["r"] * span
    return holes


# ---------------------------------------------------------------- the space


class Space:
    def __init__(self, ws: str):
        self.ws = Path(ws)
        if not (self.ws / "meta.json").exists():
            die(f"{self.ws} has no map yet; run `build` first")
        self.meta = json.loads((self.ws / "meta.json").read_text())
        self.E = np.load(self.ws / "emb.npy")
        with (self.ws / "corpus.jsonl").open(encoding="utf-8") as f:
            self.items = [json.loads(line) for line in f]
        st = np.load(self.ws / "stats.npz")
        self.nn_sim, self.nn_idx, self.labels = st["nn_sim"], st["nn_idx"], st["labels"]
        self.sorted_nn = np.sort(self.nn_sim)
        self.pop = np.array([it["pop"] for it in self.items], np.float64)
        self.has_tags = any(it["tags"] for it in self.items[:2000])
        self.clusters = {c["id"]: c for c in self.meta["clusters"]}
        self._model = None
        self._titles = [it["title"].lower() for it in self.items]

    @property
    def scale(self) -> dict:
        return self.meta["scale"]

    def save_meta(self):
        (self.ws / "meta.json").write_text(json.dumps(self.meta, indent=1))

    def embed(self, texts: list[str]) -> np.ndarray:
        if self._model is None:
            from fastembed import TextEmbedding

            self._model = TextEmbedding(model_name=self.meta["model"])
        return embed_texts(self._model, texts)

    def closer_twin_pct(self, sim: float) -> float:
        """Share of corpus items whose own nearest twin is closer than `sim`."""
        return 1.0 - np.searchsorted(self.sorted_nn, sim, side="right") / len(self.sorted_nn)

    def pair_pct(self, sim: float) -> float:
        """Share of random item pairs less similar than `sim`."""
        p = self.scale["pairs"]
        return float(np.interp(sim, list(p.values()), [int(k[1:]) / 100 for k in p]))

    def label(self, i: int) -> str:
        return self.clusters[int(self.labels[i])]["label"]

    def resolve(self, q: str) -> dict:
        """A seed from a title, '#<id>', or 'text:<free text>'."""
        if q.startswith("text:"):
            return {"title": f'"{clip(q[5:], 60)}"', "id": None, "vec": self.embed([q[5:]])[0], "text": q[5:]}
        if q.startswith("#") and q[1:].isdigit():
            i = int(q[1:])
        else:
            ql = q.lower()
            cands = [i for i, t in enumerate(self._titles) if t == ql] or [
                i for i, t in enumerate(self._titles) if ql in t
            ]
            if not cands:
                die(f'no item titled like "{q}"; use "text:<description>" to blend a concept outside the corpus')
            cands.sort(key=lambda i: -self.pop[i])
            i = cands[0]
            if len(cands) > 1:
                others = ", ".join(self.items[j]["title"] for j in cands[1:4])
                note(f'"{q}" → {self.items[i]["title"]} #{i} (also matched: {others})')
        it = self.items[i]
        return {"title": it["title"], "id": i, "vec": self.E[i], "text": it["text"]}

    def knn(self, v: np.ndarray, k: int):
        s = self.E @ v
        idx = np.argpartition(-s, k - 1)[:k]
        idx = idx[np.argsort(-s[idx])]
        return s[idx], idx

    def leans(self, idx: np.ndarray) -> list[tuple[str, float]]:
        """Tags (or terms) over-represented among the given neighbours."""
        if self.has_tags:
            n = len(self.items)
            glob = self.meta["tag_counts"]
            local = Counter(t for i in idx for t in set(self.items[i]["tags"]))
            scored = []
            for t, c in local.items():
                share = c / len(idx)
                if c >= 3 and t in glob:
                    scored.append((share * math.log(share / (glob[t] / n)), t, share))
            return [(t, sh) for s, t, sh in sorted(scored, reverse=True)[:8] if s > 0]
        terms = Counter(t for i in idx for t in self.clusters[int(self.labels[i])]["terms"][:5])
        return [(t, c / len(idx)) for t, c in terms.most_common(8)]

    def sample_seeds(self, c: int, m: int, rng: np.random.Generator) -> list[dict]:
        members = np.flatnonzero(self.labels == c)
        if len(members) < m:
            die(f"neighbourhood {c} has only {len(members)} items")
        w = np.log1p(self.pop[members]) + 1
        anchor = rng.choice(members, p=w / w.sum())
        sims = self.E[members] @ self.E[anchor]
        order = np.argsort(-sims)[1:]
        related = order[sims[order] >= self.scale["pairs"]["p90"]][:30]  # closer than 90% of random pairs
        relatives = members[related if len(related) >= m - 1 else order[:10]]
        picked = self.distinct([int(anchor), *map(int, rng.permutation(relatives))], m)
        return [self.resolve(f"#{i}") for i in picked]

    def distinct(self, candidates: list[int], k: int) -> list[int]:
        """Up to k candidates, in order, skipping near-copies and same-series titles of ones already
        picked, and preferring a new neighbourhood for each pick."""
        twin_line = self.scale["nn"]["p75"]
        picked: list[int] = []
        families: set[str] = set()
        for new_neighbourhood_only in (True, False):
            for i in candidates:
                if len(picked) == k:
                    return picked
                if i in picked or (new_neighbourhood_only and self.labels[i] in self.labels[picked]):
                    continue
                if family(self.items[i]["title"]) in families:
                    continue
                if all(self.E[i] @ self.E[j] < twin_line for j in picked):
                    picked.append(i)
                    families.add(family(self.items[i]["title"]))
        return picked

    def push(self, V: np.ndarray, leash: float, steps: int = 150, restarts: int = 6, tau: float = 0.02, dims: int = 24):
        """Blend the seeds, then move away from the nearest existing items until the point settles in
        the emptiest spot nearby. Returns (point, nn_start, nn_end).

        The point moves only along directions in which nearby items actually differ (the top
        principal directions of the neighbourhood). In free space it would slide into dimensions no
        text occupies and look empty without meaning anything. It also stays no farther from the
        blend than the seeds are (times `leash`), so it remains specific to the ingredients."""
        rng = np.random.default_rng(0)
        c = unit(V.mean(0))
        if len(V) > 1:
            radius = float(np.arccos(np.clip(V @ c, -1, 1)).max())
        else:
            radius = float(np.arccos(self.scale["nn"]["p50"]))
        reach = math.tan(min(radius * leash, 1.4))  # cap radius, measured in the plane tangent at c
        pool = self.E[np.argsort(-(self.E @ c))[:2000]]
        local = np.vstack([pool[:300], V])
        local = local - np.outer(local @ c, c)
        B = np.linalg.svd(local, full_matrices=False)[2][:dims].T.astype(np.float32)  # d × dims, ⟂ c

        def point(z):
            return unit(c + B @ z)

        def clamp(z):
            n = np.linalg.norm(z)
            return z if n <= reach else z * (reach / n)

        starts = [np.zeros(dims, np.float32)]
        for _ in range(restarts - 1):
            if len(V) > 1:
                b = rng.dirichlet(np.ones(len(V))).astype(np.float32) @ V
                starts.append(clamp(B.T @ b / (b @ c)))
            else:
                starts.append(unit(rng.normal(size=dims)).astype(np.float32) * rng.uniform(0, reach))
        nn_start = float((self.E @ c).max())
        best_z, best_nn = starts[0], nn_start
        for z in starts:
            for t in range(steps):
                y = c + B @ z
                x = y / np.linalg.norm(y)
                s = pool @ x
                w = np.exp((s - s.max()) / tau)
                g = (w / w.sum()) @ pool
                gz = B.T @ (g - (g @ x) * x)
                gn = np.linalg.norm(gz)
                if gn < 1e-9:
                    break
                z = clamp(z - (0.05 * (1 - t / steps) + 0.005) * reach * gz / gn)
            nn = float((self.E @ point(z)).max())
            if nn < best_nn:
                best_z, best_nn = z, nn
        return point(best_z), nn_start, best_nn

    def make_brief(self, seeds: list[dict], leash: float, origin: dict) -> dict:
        V = np.stack([s["vec"] for s in seeds])
        coherence = None
        if len(V) > 1:
            S = V @ V.T
            mean_sim = float(S[np.triu_indices(len(V), 1)].mean())
            coherence = {"mean_sim": mean_sim, "pair_pct": self.pair_pct(mean_sim)}
        with threadpool_limits(1):  # thousands of tiny mat-vecs: threads only add overhead
            x, nn_start, nn_end = self.push(V, leash)
        sims, idx = self.knn(x, 50)
        between = Counter(int(self.labels[i]) for i in idx).most_common(3)
        bdir = self.ws / "briefs"
        bdir.mkdir(exist_ok=True)
        bid = f"b{max((int(f.stem[1:]) for f in bdir.glob('b*.json')), default=0) + 1:02d}"
        avoid = [
            {"id": int(i), "title": self.items[i]["title"], "sim": float(s), "text": clip(self.items[i]["text"], 320)}
            for s, i in zip(sims[:8], idx[:8])
        ]
        brief = {
            "id": bid,
            "origin": origin,
            "seeds": [{"title": s["title"], "id": s["id"], "text": clip(s["text"], 200)} for s in seeds],
            "coherence": coherence,
            "nn_start": nn_start,
            "nn_end": nn_end,
            "between": [{"id": c, "label": self.clusters[c]["label"], "n": n} for c, n in between],
            "leans": self.leans(idx),
            "avoid": avoid,
            "words": int(np.median([len(self.items[i]["text"].split()) for i in idx[:20]])),
        }
        np.save(bdir / f"{bid}.npy", x)
        (bdir / f"{bid}.json").write_text(json.dumps(brief, indent=1))
        return brief

    def map2d(self) -> np.ndarray:
        f = self.ws / "map.npy"
        if f.exists():
            xy = np.load(f)
            if len(xy) == len(self.E):
                return xy
        import umap

        note("flattening the map with UMAP (cached for next time)…")
        reducer = umap.UMAP(n_neighbors=15, min_dist=0.05, metric="cosine", low_memory=True)
        xy = np.asarray(reducer.fit_transform(self.E), np.float32)
        np.save(f, xy)
        return xy

    def ideas(self) -> list[dict]:
        f = self.ws / "ideas.jsonl"
        if not f.exists():
            return []
        with f.open(encoding="utf-8") as fh:
            return [json.loads(line) for line in fh]


def render_brief(sp: Space, b: dict) -> str:
    o = b["origin"]
    head = (
        "blend of " + " + ".join(s["title"] for s in b["seeds"])
        if o["kind"] == "blend"
        else f"gap of radius {o['radius']:.3f} between " + " / ".join(x["label"] for x in o["between"])
    )
    out = [f"## Brief {b['id']} — {head}", "", "Blended from:"]
    out += [f"  - {s['title']}: {s['text']}" for s in b["seeds"]]
    if b["coherence"]:
        c = b["coherence"]
        if c["pair_pct"] >= 0.9:
            ok = "related"
        elif o["kind"] == "gap":
            ok = "rim items come from different neighbourhoods by design: find the concrete bridge"
        else:
            ok = "WEAKLY RELATED: expect mush unless you find a concrete bridge"
        out.append(
            f"Ingredient coherence: {c['mean_sim']:.2f} mean similarity, above {c['pair_pct']:.0%} of random pairs ({ok})"
        )
    out.append(
        f"Empty space: the plain blend's nearest item is {b['nn_start']:.2f} similar; after the push {b['nn_end']:.2f}. "
        f"Typical item: {sp.scale['nn']['p50']:.2f}. A target point always looks emptier than real text; "
        "only the measured draft counts."
    )
    out.append("Sits between: " + "; ".join(f"{x['label']} ({x['n']})" for x in b["between"]))
    if b["leans"]:
        out.append("Leans toward: " + ", ".join(f"{t} ({s:.0%})" for t, s in b["leans"]))
    out.append("Must not copy (nearest existing items, which also show the corpus's format):")
    out += [f"  {a['sim']:.2f}  {a['title']}: {a['text']}" for a in b["avoid"]]
    out += [
        "",
        f"Write ~{b['words']} words in the same format and register as the items above, then:",
        f'  measure {sp.ws} --brief {b["id"]} --title "<name>" --why "<one line>" --file <draft.txt>',
    ]
    return "\n".join(out)


def brief_line(sp: Space, b: dict) -> str:
    where = " / ".join(x["label"] for x in (b["origin"].get("between") or b["between"]))
    seeds = " + ".join(clip(s["title"], 28) for s in b["seeds"])
    coh = f"coh {b['coherence']['pair_pct']:.0%}" if b["coherence"] else "single seed"
    crowded = " (still crowded)" if b["nn_end"] >= sp.scale["nn"]["p50"] else ""
    return f"{b['id']}  nn {b['nn_start']:.2f}→{b['nn_end']:.2f}{crowded}  {coh}  {seeds}  [{clip(where, 70)}]"


# ---------------------------------------------------------------- commands


def cmd_build(a):
    ws = Path(a.ws)
    ws.mkdir(parents=True, exist_ok=True)
    items = normalise(read_records(Path(a.input)), a.text, a.title, a.tags or [], a.pop or [], a.min_words)
    if len(items) < 50:
        die("need at least 50 items to map anything; gather more")
    if len(items) < 300:
        note("warning: under 300 items, 'empty space' mostly means 'not in your sample'")
    texts = [it["text"] for it in items]
    key = hashlib.sha1((a.model + "\0" + "\0".join(texts)).encode()).hexdigest()
    old = json.loads((ws / "meta.json").read_text()) if (ws / "meta.json").exists() else {}
    if old.get("key") == key and (ws / "emb.npy").exists():
        note("corpus and model unchanged: reusing embeddings")
        E = np.load(ws / "emb.npy")
    else:
        from fastembed import TextEmbedding

        note(f"embedding {len(texts)} items with {a.model} …")
        E = embed_texts(TextEmbedding(model_name=a.model), texts, progress=True)
        np.save(ws / "emb.npy", E)
        for stale in ("map.npy", "mush.npy"):
            (ws / stale).unlink(missing_ok=True)
    with (ws / "corpus.jsonl").open("w", encoding="utf-8") as f:
        f.writelines(json.dumps(it, ensure_ascii=False) + "\n" for it in items)

    note("measuring nearest twins …")
    nn_sim, nn_idx = top_k(E, E, 1, exclude_self=True)
    nn_sim, nn_idx = nn_sim[:, 0], nn_idx[:, 0]
    rng = np.random.default_rng(0)
    pa, pb = rng.integers(0, len(E), 40000), rng.integers(0, len(E), 40000)
    pairs = np.einsum("ij,ij->i", E[pa[pa != pb]], E[pb[pa != pb]])

    note("finding neighbourhoods …")
    from sklearn.cluster import KMeans, MiniBatchKMeans

    k = a.clusters or int(np.clip(math.sqrt(len(E) / 2), 8, 150))
    km = (
        MiniBatchKMeans(k, random_state=0, n_init="auto", batch_size=4096)
        if len(E) > 20000
        else KMeans(k, random_state=0, n_init="auto")
    ).fit(E)
    labels, centers = np.asarray(km.labels_), unit(np.asarray(km.cluster_centers_))
    tag_counts = Counter(t for it in items for t in set(it["tags"]))
    clusters = describe_clusters(E, items, labels, centers, nn_sim, tag_counts)

    meta = {
        "key": key,
        "model": a.model,
        "source": str(Path(a.input).resolve()),
        "n": len(items),
        "dim": int(E.shape[1]),
        "scale": {
            "nn": quantiles(nn_sim),
            "pairs": quantiles(pairs, (1, 10, 25, 50, 75, 90, 95, 99)),
            "median_words": int(np.median([len(t.split()) for t in texts])),
        },
        "tag_counts": dict(tag_counts),
        "clusters": clusters,
        "calibration": old.get("calibration", {}) if old.get("key") == key else {},
    }
    (ws / "meta.json").write_text(json.dumps(meta, indent=1))
    np.savez(ws / "stats.npz", nn_sim=nn_sim, nn_idx=nn_idx, labels=labels)
    s = meta["scale"]["nn"]
    print(
        f"mapped {len(items)} items into {k} neighbourhoods ({E.shape[1]}-d, {a.model}).\n"
        f"typical item is {s['p50']:.2f} similar to its closest twin; loneliest 1% under {s['p1']:.2f}.\n"
        f"next: survey {ws}"
    )


def describe_clusters(E, items, labels, centers, nn_sim, tag_counts) -> list[dict]:
    from scipy import sparse
    from sklearn.feature_extraction.text import TfidfVectorizer

    n, k = len(items), len(centers)
    vec = TfidfVectorizer(stop_words="english", min_df=3 if n >= 300 else 1, max_df=0.3, sublinear_tf=True)
    tf = vec.fit_transform([it["text"] for it in items])
    vocab = vec.get_feature_names_out()
    sizes = np.bincount(labels, minlength=k)
    ind = sparse.csr_matrix((np.ones(n), (labels, np.arange(n))), shape=(k, n))
    lift = np.asarray((ind @ tf).todense()) / sizes[:, None] - np.asarray(tf.mean(axis=0))
    pop = np.array([it["pop"] for it in items])
    out = []
    for c in range(k):
        members = np.flatnonzero(labels == c)
        terms = [str(vocab[j]) for j in np.argsort(-lift[c])[:6]]
        local = Counter(t for i in members for t in set(items[i]["tags"]))
        tags = sorted(
            (
                (cnt / len(members)) * math.log((cnt / len(members)) / (tag_counts[t] / n)),
                t,
            )
            for t, cnt in local.items()
            if cnt >= max(2, 0.1 * len(members))
        )
        tags = [t for s, t in reversed(tags) if s > 0][:4]
        typical = members[np.argsort(-(E[members] @ centers[c]))[:3]]
        out.append(
            {
                "id": c,
                "size": int(len(members)),
                "label": ", ".join(tags[:3]) if tags else ", ".join(terms[:3]),
                "tags": tags,
                "terms": terms,
                "examples": [items[i]["title"] for i in typical],
                "crowding": float(np.median(nn_sim[members])),
                "pop": float(pop[members].sum()),
                "pop_median": float(np.median(pop[members])),
            }
        )
    return out


def cmd_survey(a):
    sp = Space(a.ws)
    m, s, cl = sp.meta, sp.scale, sp.meta["clusters"]
    nn = s["nn"]
    print(f"# {m['n']} items · {m['model']} · median {s['median_words']} words per item\n")
    print("## How new is new (similarity to closest twin)")
    print(
        f"  loneliest 1%: <{nn['p1']:.2f}   loneliest 10%: <{nn['p10']:.2f}   typical: {nn['p50']:.2f}   "
        f"most crowded 10%: >{nn['p90']:.2f}   random pair: {s['pairs']['p50']:.2f}"
    )
    cal = m.get("calibration", {})
    if "copy_line" in cal:
        print(f"  copy line (same item reworded): {cal['copy_line']:.2f}")
    else:
        print("  copy line not calibrated yet: run `calibrate`")

    def row(c):
        demand = f"  demand {c['pop']:,.0f} (median {c['pop_median']:,.0f})" if c["pop"] else ""
        ex = ", ".join(clip(e, 24) for e in c["examples"])
        return f"  [{c['id']:>3}] {c['size']:>5} items  twin {c['crowding']:.2f}{demand}  {clip(c['label'], 40)} — {ex}"

    print(f"\n## Biggest neighbourhoods (of {len(cl)})")
    for c in sorted(cl, key=lambda c: -c["size"])[: a.top]:
        print(row(c))
    if any(c["pop"] for c in cl):
        print("\n## Most demand (sum of the popularity field)")
        for c in sorted(cl, key=lambda c: -c["pop"])[: a.top]:
            print(row(c))
        floor = max(10, m["n"] // 500)
        print(f"\n## Highest median demand (≥{floor} items): a typical item here does well")
        for c in sorted((c for c in cl if c["size"] >= floor), key=lambda c: -c["pop_median"])[: a.top]:
            print(row(c))
    print("\n## Most crowded corners (items are near-copies of each other)")
    for c in sorted(cl, key=lambda c: -c["crowding"])[: max(5, a.top // 2)]:
        print(row(c))
        members = np.flatnonzero(sp.labels == c["id"])
        i = members[np.argmax(sp.nn_sim[members])]
        twin = sp.items[sp.nn_idx[i]]["title"]
        print(f"        e.g. {clip(sp.items[i]['title'], 40)} ≈ {clip(twin, 40)} ({sp.nn_sim[i]:.2f})")
    print("\n## Loners (most original existing items)")
    for i in np.argsort(sp.nn_sim)[: a.top]:
        it = sp.items[i]
        print(
            f"  {sp.nn_sim[i]:.2f}  {clip(it['title'], 40)}  (lonelier than {pct(sp.closer_twin_pct(sp.nn_sim[i]))})"
            f"  in {clip(sp.label(i), 40)}"
        )
    print(f"\nShowing {a.top} per section of {len(cl)} neighbourhoods; --top {len(cl)} shows all.")
    print(f"Blend inside one: blend {sp.ws} --cluster <id>. Finer neighbourhoods: rebuild with --clusters <n>.")


def cmd_neighbors(a):
    sp = Space(a.ws)
    seed = sp.resolve(a.query)
    sims = sp.E @ seed["vec"]
    order = np.argsort(-sims)
    order = [i for i in order if i != seed["id"]]
    where = f" in [{sp.labels[seed['id']]}] {sp.label(seed['id'])}" if seed["id"] is not None else ""
    print(f"# {seed['title']}{where}")
    if seed["id"] is not None:
        nn = float(sp.nn_sim[seed["id"]])
        print(f"closest twin {nn:.2f}: lonelier than {pct(sp.closer_twin_pct(nn))} of the corpus")
    print("\nnearest:")
    for i in order[: a.k]:
        print(f"  {sims[i]:.2f}  {clip(sp.items[i]['title'], 50)}  [{clip(sp.label(i), 40)}]")
    print("farthest:")
    for i in order[-3:][::-1]:
        print(f"  {sims[i]:.2f}  {clip(sp.items[i]['title'], 50)}  [{clip(sp.label(i), 40)}]")


def cmd_calibrate(a):
    sp = Space(a.ws)
    cal = sp.meta.setdefault("calibration", {})
    if not a.paraphrases and not a.mush:
        rng = np.random.default_rng()
        words = np.array([len(it["text"].split()) for it in sp.items])
        lo, hi = np.percentile(words, [25, 75])
        pick = rng.choice(np.flatnonzero((words >= lo) & (words <= hi)), a.n, replace=False)
        print("Paraphrase each item below: same meaning, same length and register, different words.")
        print("Replace proper nouns (titles, characters, brands) with plain descriptions: drafts never contain")
        print("existing names, and keeping them would set the copy line too high.")
        print('Save as JSONL lines {"id": <id>, "text": "<paraphrase>"}.')
        print("Also write 5 deliberately generic descriptions for this domain that say nothing specific")
        print("(plausible but interchangeable), separated by blank lines, to a mush file. Then run:")
        print(f"  calibrate {sp.ws} --paraphrases <file.jsonl> --mush <mush.txt>\n")
        for i in pick:
            print(json.dumps({"id": int(i), "title": sp.items[i]["title"], "text": sp.items[i]["text"]}))
        return
    if a.paraphrases:
        with open(a.paraphrases, encoding="utf-8") as f:
            recs = [json.loads(line) for line in f if line.strip()]
        P = sp.embed([r["text"] for r in recs])
        sims = np.einsum("ij,ij->i", P, sp.E[[int(r["id"]) for r in recs]])
        cal["copy_line"] = float(sims.min())  # a faithful rewording can score this low, so at or above is a copy
        cal["paraphrase_sims"] = [float(x) for x in sims]
        print(
            f"copy line {cal['copy_line']:.2f} (paraphrases ranged {sims.min():.2f}–{sims.max():.2f}); "
            f"{pct(sp.closer_twin_pct(cal['copy_line']))} of items have a twin this close (near-duplicates)"
        )
    if a.mush:
        texts = [t.strip() for t in re.split(r"\n\s*\n", Path(a.mush).read_text(encoding="utf-8")) if t.strip()]
        M = sp.embed(texts)
        centroid = unit(M.mean(0))
        np.save(sp.ws / "mush.npy", centroid)
        cal["mush_p95"] = float(np.percentile(sp.E @ centroid, 95))
        nn = (M @ sp.E.T).max(1)
        print(
            f"mush anchor saved from {len(texts)} generic texts; drafts closer to it than 95% of real items "
            f"(above {cal['mush_p95']:.2f}) are flagged MUSHY"
        )
        print(
            "how lonely mush looks (nearest item, lonelier than): "
            + ", ".join(f"{x:.2f} ({pct(sp.closer_twin_pct(x))})" for x in nn)
        )
        if max(sp.closer_twin_pct(x) for x in nn) >= 0.5:
            print("WARNING: generic text looks novel in this space, so vagueness can fake novelty. Hold drafts to")
            print("concrete specifics and treat MUSHY flags as failures.")
        else:
            print("generic text reads as crowded here, so vagueness will not fake novelty.")
    sp.save_meta()


def cmd_blend(a):
    sp = Space(a.ws)
    rng = np.random.default_rng(a.seed)
    sets: list[tuple[list[dict], dict]] = []
    if a.seeds:
        seeds = [sp.resolve(s) for s in a.seeds]
        sets.append((seeds, {"kind": "blend"}))
    for c in a.cluster or []:
        if c not in sp.clusters:
            die(f"no neighbourhood {c}; see survey")
        for _ in range(a.count):
            sets.append((sp.sample_seeds(c, a.per, rng), {"kind": "blend", "cluster": c}))
    if not sets:
        die("give --seeds and/or --cluster")
    briefs = [sp.make_brief(seeds, a.leash, origin) for seeds, origin in sets]
    if len(briefs) == 1:
        print(render_brief(sp, briefs[0]))
        return
    for b in sorted(briefs, key=lambda b: b["nn_end"]):
        print(brief_line(sp, b))
    print(f"\nshow one with: brief {sp.ws} <id>")


def cmd_gaps(a):
    sp = Space(a.ws)
    holes = find_holes(sp.map2d(), a.top * 8 if a.near else a.top)
    if a.near:
        q = sp.resolve(a.near)["vec"]
        for h in holes:
            h["relevance"] = float(np.mean(sp.E[h["rim"]] @ q))
        holes = sorted(holes, key=lambda h: -h["relevance"])[: a.top]
    if not holes:
        print("no enclosed holes found; the map may be too small or too uniform. Use blend instead.")
        return
    briefs = []
    for h in holes:
        rim = h["rim"]
        seeds = sp.distinct(rim, 4)
        if len(seeds) < 2:  # walled by one franchise or near-copies: nothing to blend
            continue
        by_cluster = Counter(int(sp.labels[i]) for i in rim)
        between = [{"id": c, "label": sp.clusters[c]["label"], "n": n} for c, n in by_cluster.most_common(4)]
        origin = {"kind": "gap", "radius": h["r"], "xy": h["xy"], "radius_xy": h["radius_xy"], "between": between}
        if "relevance" in h:
            origin["relevance"] = h["relevance"]
        briefs.append(sp.make_brief([sp.resolve(f"#{i}") for i in seeds], a.leash, origin))
    order = f"most related to {a.near} first" if a.near else "largest first"
    print(f"{len(briefs)} holes ({order}); nn = nearest-item similarity before→after the push\n")
    for b in briefs:
        near = f"near {b['origin']['relevance']:.2f}  " if a.near else ""
        print(f"r {b['origin']['radius']:.3f}  {near}" + brief_line(sp, b))
    print(f"\nshow one with: brief {sp.ws} <id>")


def cmd_brief(a):
    sp = Space(a.ws)
    f = sp.ws / "briefs" / f"{a.id}.json"
    if not f.exists():
        die(f"no brief {a.id}")
    print(render_brief(sp, json.loads(f.read_text())))


def cmd_measure(a):
    sp = Space(a.ws)
    text = Path(a.file).read_text(encoding="utf-8").strip() if a.file else (a.text or "").strip()
    if not text:
        die("give --file or --text")
    v = sp.embed([text])[0]
    sims, idx = sp.knn(v, 20)
    nn = float(sims[0])
    share = sp.closer_twin_pct(nn)
    cal = sp.meta.get("calibration", {})
    copy_line, typical = cal.get("copy_line"), sp.scale["nn"]["p50"]

    status, flags = "pass", []
    if copy_line and nn >= copy_line:
        status = "copy"
    elif share < a.accept:
        status = "too-close"
    landing = None
    if a.brief:
        x = np.load(sp.ws / "briefs" / f"{a.brief}.npy")
        # The seeds are the target's own ingredients, so new text never beats them; instead ask whether
        # the draft ranks among the items nearest the target.
        to_target = float(v @ x)
        rank = int((sp.E @ x > to_target).sum()) + 1
        landing = {"to_target": to_target, "rank": rank, "on_target": rank <= max(20, 0.01 * len(sp.E))}
        if not landing["on_target"]:
            flags.append("off-target")
    mush = None
    if (sp.ws / "mush.npy").exists() and "mush_p95" in cal:
        mush = float(v @ np.load(sp.ws / "mush.npy"))
        if mush > cal["mush_p95"]:
            flags.append("mushy")
            if status == "pass":
                status = "mushy"

    prior = [r for r in sp.ideas() if (a.brief and r["brief"] == a.brief) or r["title"].lower() == a.title.lower()]
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "brief": a.brief,
        "title": a.title,
        "why": a.why,
        "text": text,
        "draft": len(prior) + 1,
        "nn_sim": nn,
        "closer_twin_pct": share,
        "status": status,
        "accept": a.accept,
        "flags": flags,
        "landing": landing,
        "mush": mush,
        "nearest": [{"id": int(i), "title": sp.items[i]["title"], "sim": float(s)} for s, i in zip(sims, idx)][:10],
        "demand_nearby": float(np.median(sp.pop[idx])),
    }
    with (sp.ws / "ideas.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    lines = [f'# Draft {rec["draft"]} of "{a.title}"' + (f" (brief {a.brief})" if a.brief else "")]
    scale = f"typical twin {typical:.2f}" + (f" · copy line {copy_line:.2f}" if copy_line else "")
    lines.append(f"nearest existing: {sp.items[idx[0]]['title']} at {nn:.2f}  ({scale})")
    lines.append(f"lonelier than {pct(share)} of the corpus → {status.upper()} (needs ≥ {a.accept:.0%})")
    if landing:
        lines.append(
            f"landing: would rank {landing['rank']} of {len(sp.E)} items nearest the brief's target"
            f" → {'on target' if landing['on_target'] else 'off target: the idea landed away from this brief'}"
        )
    if mush is not None:
        lines.append(f"mush: {mush:.2f} to the generic anchor (flag above {cal['mush_p95']:.2f})")
    lines.append("closest items:")
    lines += [f"  {s:.2f}  {sp.items[i]['title']}: {clip(sp.items[i]['text'], 220)}" for s, i in zip(sims[:4], idx[:4])]
    advice = {
        "copy": "This is a reworded existing item. Start again from the brief's ingredients.",
        "too-close": "Find what the draft shares with the closest items above and replace that part "
        "with something none of them do, keep the rest, measure again.",
        "mushy": "The draft is generic. Name the concrete core activity, setting and twist.",
        "off-target": "Off target does not fail the draft; its origin is just loose. Check it reads like a normal item "
        "in the corpus's format and register. If it does, keep it; if it is oddly worded, rewrite it in that style.",
    }
    for problem in dict.fromkeys([status, *flags]):
        if problem in advice:
            lines.append("\n" + advice[problem])
    print("\n".join(lines))


def best_ideas(sp: Space, include_failed: bool) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for r in sp.ideas():
        groups.setdefault(r["brief"] or r["title"].lower(), []).append(r)
    best = []
    for drafts in groups.values():
        passing = [r for r in drafts if r["status"] == "pass"]
        if passing:
            pick = passing[-1]
        elif include_failed:
            pick = min(drafts, key=lambda r: r["nn_sim"])
        else:
            continue
        best.append({**pick, "history": [(r["nn_sim"], r is pick) for r in drafts]})
    return sorted(best, key=lambda r: r["nn_sim"])


def cmd_report(a):
    sp = Space(a.ws)
    ideas = best_ideas(sp, a.all)
    if not ideas:
        die("no measured ideas yet" + ("" if a.all else " that pass; try --all"))
    cal = sp.meta.get("calibration", {})
    typical, copy_line = sp.scale["nn"]["p50"], cal.get("copy_line")
    corpus_pop = float(np.median(sp.pop)) if sp.pop.any() else None
    out = [
        f"# Ideas from the empty space of {sp.meta['n']} items",
        "",
        f"Similarity to the closest existing item: typical item {typical:.2f}"
        + (f", reworded copy {copy_line:.2f}" if copy_line else "")
        + f", loneliest 1% under {sp.scale['nn']['p1']:.2f}. Lower is newer. Newness is not quality.",
        "",
    ]
    for n, r in enumerate(ideas, 1):
        borderline = " (borderline)" if r["status"] == "pass" and r["closer_twin_pct"] < r["accept"] + 0.05 else ""
        out.append(f"## {n}. {r['title']} — lonelier than {pct(r['closer_twin_pct'])} of the corpus{borderline}")
        out += ["", r["text"], ""]
        if r.get("why"):
            out += [f"**Why it's new:** {r['why']}", ""]
        near = ", ".join(f"{x['title']} ({x['sim']:.2f})" for x in r["nearest"][:3])
        out.append(f"- Closest existing: {near}")
        if r["brief"]:
            b = json.loads((sp.ws / "briefs" / f"{r['brief']}.json").read_text())
            origin = (
                "blend of " + " + ".join(s["title"] for s in b["seeds"])
                if b["origin"]["kind"] == "blend"
                else "gap between "
                + " / ".join(x["label"] for x in b["origin"]["between"])
                + ", from rim items "
                + " + ".join(s["title"] for s in b["seeds"])
            )
            loose = " (the draft landed away from this origin)" if "off-target" in r["flags"] else ""
            out.append(f"- Origin: {origin}{loose}")
        if corpus_pop:
            out.append(
                f"- Demand nearby: neighbours' median popularity is {r['demand_nearby'] / corpus_pop:.1f}× the corpus median"
            )
        hist = " → ".join(f"[{h:.2f}]" if chosen else f"{h:.2f}" for h, chosen in r["history"])
        out += [f"- Drafts (nn per attempt, [shown]): {hist} · status {r['status']}", ""]
    text = "\n".join(out)
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"wrote {a.out} ({len(ideas)} ideas)")
    else:
        print(text)


def cmd_plot(a):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle

    sp = Space(a.ws)
    xy = sp.map2d()
    fig, ax = plt.subplots(figsize=(14, 14), dpi=110)
    fig.patch.set_facecolor("#0b0d12")
    ax.set_facecolor("#0b0d12")
    ax.scatter(
        xy[:, 0], xy[:, 1], s=min(12, max(1.5, 40000 / len(xy))), c=plt.cm.tab20(sp.labels % 20), alpha=0.6, lw=0
    )
    lo, hi = map_bounds(xy)
    pad = 0.04 * (hi - lo)
    ax.set_xlim(lo[0] - pad[0], hi[0] + pad[0])
    ax.set_ylim(lo[1] - pad[1], hi[1] + pad[1])
    ax.set_aspect("equal")
    for c in sorted(sp.meta["clusters"], key=lambda c: -c["size"])[: a.labels]:
        cx, cy = np.median(xy[sp.labels == c["id"]], axis=0)
        ax.text(cx, cy, clip(c["label"], 28), color="white", fontsize=8, ha="center", alpha=0.85)
    briefs = [json.loads(f.read_text()) for f in sorted((sp.ws / "briefs").glob("b*.json"))]
    by_hole: dict[tuple, list[str]] = {}  # the same hole can be briefed more than once
    for b in briefs:
        if b["origin"]["kind"] == "gap":
            by_hole.setdefault((*b["origin"]["xy"], b["origin"]["radius_xy"]), []).append(b["id"])
    holes = [((x, y), r, ", ".join(ids)) for (x, y, r), ids in by_hole.items()] or [
        (h["xy"], h["radius_xy"], "") for h in find_holes(xy, a.holes)
    ]
    for (hx, hy), radius, label in holes:
        ax.add_patch(Circle((hx, hy), radius, fill=False, ec="#5ad1ff", lw=1, ls="--"))
        ax.text(hx, hy + radius, label, color="#5ad1ff", fontsize=8, ha="center", va="bottom")
    stacked: Counter = Counter()
    for r in best_ideas(sp, include_failed=False):
        # A new idea's neighbours are often scattered across the flat map, so their mean lands in an
        # arbitrary middle; the medoid sits where several of them actually are.
        P = xy[[x["id"] for x in r["nearest"]]]
        px, py = P[np.linalg.norm(P[:, None] - P[None], axis=-1).sum(1).argmin()]
        ax.plot(px, py, marker="*", ms=14, color="#ffb648", mec="black")
        k = stacked[(px, py)]
        stacked[(px, py)] += 1
        ax.annotate(
            clip(r["title"], 30), (px, py), xytext=(9, -13 * k), textcoords="offset points", color="#ffb648", fontsize=9
        )
    ax.set_axis_off()
    out = a.out or sp.ws / "map.png"
    fig.savefig(out, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"wrote {out}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("build", help="ingest, embed and map a corpus")
    s.add_argument("ws", help="workspace directory")
    s.add_argument("--input", required=True, help=".csv, .json or .jsonl corpus file")
    s.add_argument("--text", action="append", required=True, help="field(s) to embed, joined in order")
    s.add_argument("--title", help="field holding the item's name")
    s.add_argument("--tags", action="append", help="field(s) holding tags/genres/categories")
    s.add_argument("--pop", action="append", help="numeric field(s) summed as popularity/demand")
    s.add_argument("--model", default=DEFAULT_MODEL, help=f"fastembed model (default {DEFAULT_MODEL})")
    s.add_argument("--clusters", type=int, help="number of neighbourhoods (default ≈ sqrt(n/2))")
    s.add_argument("--min-words", type=int, default=8, help="drop items with shorter text (default 8)")
    s.set_defaults(fn=cmd_build)

    s = sub.add_parser("survey", help="print the landscape")
    s.add_argument("ws")
    s.add_argument("--top", type=int, default=12, help="rows per section (default 12)")
    s.set_defaults(fn=cmd_survey)

    s = sub.add_parser("neighbors", help="nearest and farthest items to a title or text:<...>")
    s.add_argument("ws")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=10, help="how many nearest items to list (default 10)")
    s.set_defaults(fn=cmd_neighbors)

    s = sub.add_parser("calibrate", help="sample items to paraphrase, or ingest paraphrases and mush")
    s.add_argument("ws")
    s.add_argument("--n", type=int, default=6, help="items to sample for paraphrasing (default 6)")
    s.add_argument("--paraphrases", help='JSONL of {"id": .., "text": ..} paraphrases')
    s.add_argument("--mush", help="text file of generic descriptions separated by blank lines")
    s.set_defaults(fn=cmd_calibrate)

    s = sub.add_parser("blend", help="blend seeds, push into empty space, write a brief")
    s.add_argument("ws")
    s.add_argument("--seeds", nargs="+", help='titles, "#<id>" or "text:<concept>"')
    s.add_argument("--cluster", type=int, action="append", help="sample seeds inside this neighbourhood (repeatable)")
    s.add_argument("--count", type=int, default=3, help="briefs per --cluster")
    s.add_argument("--per", type=int, default=3, help="seeds per sampled blend")
    s.add_argument("--leash", type=float, default=1.0, help="how far the push may leave the seeds' span")
    s.add_argument("--seed", type=int, default=None, help="random seed for sampling")
    s.set_defaults(fn=cmd_blend)

    s = sub.add_parser("gaps", help="find holes in the flattened map and brief each")
    s.add_argument("ws")
    s.add_argument("--top", type=int, default=12, help="how many holes to brief (default 12)")
    s.add_argument("--near", help='only holes related to this title, "#<id>" or "text:<area>"')
    s.add_argument("--leash", type=float, default=1.0, help="how far the push may leave the rim seeds' span")
    s.set_defaults(fn=cmd_gaps)

    s = sub.add_parser("brief", help="print a saved brief")
    s.add_argument("ws")
    s.add_argument("id")
    s.set_defaults(fn=cmd_brief)

    s = sub.add_parser("measure", help="embed a draft and judge its novelty")
    s.add_argument("ws")
    s.add_argument("--title", required=True, help="the idea's name; drafts of one idea share it")
    s.add_argument("--file", help="file holding the draft text")
    s.add_argument("--text", help="the draft text inline (instead of --file)")
    s.add_argument("--brief", help="brief id the draft was written from, for the landing check")
    s.add_argument("--why", default="", help="one line on what differs from the closest items")
    s.add_argument("--accept", type=float, default=DEFAULT_ACCEPT, help="share of the corpus to beat (default 0.75)")
    s.set_defaults(fn=cmd_measure)

    s = sub.add_parser("report", help="rank measured ideas as markdown")
    s.add_argument("ws")
    s.add_argument("--out", help="write the markdown here instead of printing it")
    s.add_argument("--all", action="store_true", help="include ideas that never passed")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("plot", help="render the map to PNG")
    s.add_argument("ws")
    s.add_argument("--out", help="PNG path (default <ws>/map.png)")
    s.add_argument("--holes", type=int, default=12, help="holes to draw when no gap briefs exist (default 12)")
    s.add_argument("--labels", type=int, default=20, help="label the largest N neighbourhoods (default 20)")
    s.set_defaults(fn=cmd_plot)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
