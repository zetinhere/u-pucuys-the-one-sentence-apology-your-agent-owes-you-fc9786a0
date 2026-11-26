#!/usr/bin/env python3
"""Final round-robin among the group-stage top 6 plus the current entry (#8).

Reuses the proxy judge from tournament_gw.py (same brief, same scoring).
Resumable: writes tournament_final7.json incrementally.
Usage: python3 final7.py
"""
import json, os, sys, itertools

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tournament_gw as tg

BASE = os.path.dirname(os.path.abspath(__file__))
CANDS = [1, 2, 6, 8, 12, 17, 20]
OUT = os.path.join(BASE, "tournament_final7.json")
LOG = os.path.join(BASE, "tournament_final7.log")

def main():
    cands = tg.load_candidates()
    pairs = list(itertools.combinations(sorted(CANDS), 2))
    scores = {i: 0.0 for i in CANDS}
    games = []
    done = set()
    if os.path.exists(OUT):
        prev = json.load(open(OUT))
        games = prev["games"]
        for g in games:
            done.add((g["a"], g["b"]))
            scores[g["a"]] += g["pts_a"]
            scores[g["b"]] += g["pts_b"]
    todo = [p for p in pairs if p not in done]
    print(f"final7 pairs={len(pairs)} already={len(done)} todo={len(todo)}", flush=True)
    log = open(LOG, "a")
    for a, b in todo:
        g = tg.play(a, b, cands, scores)
        games.append(g)
        line = f"[{len(games)}/{len(pairs)}] #{a} vs #{b}: {g['pts_a']:.1f}-{g['pts_b']:.1f} (v:{g['va']}/{g['vb']} m:{g['ma']}/{g['mb']})"
        if g["va"] is None:
            line += f" ra:{g.get('ra','')}"
        if g["vb"] is None:
            line += f" rb:{g.get('rb','')}"
        print(line, flush=True)
        log.write(line + "\n"); log.flush()
        ranking = sorted(CANDS, key=lambda i: -scores[i])
        json.dump({"stage": "final7", "scores": scores, "ranking": ranking,
                   "games": games},
                  open(OUT, "w"), indent=2)
    log.close()
    ranking = sorted(CANDS, key=lambda i: -scores[i])
    print("FINAL7 RANKING:", [(i, round(scores[i], 2)) for i in ranking], flush=True)

if __name__ == "__main__":
    main()
