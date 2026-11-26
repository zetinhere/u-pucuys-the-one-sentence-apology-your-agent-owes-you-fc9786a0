#!/usr/bin/env python3
"""Proxy-judge tournament via the local 9router gateway
(model 100milionseek/deepseek-v4.1-flash-free). Handles 503 saturation
with retries + backoff, runs games in parallel (3 workers), saves
incremental progress so it can resume.
Usage: python3 tournament2.py [groups|finals]
"""
import json, re, subprocess, sys, itertools, os, time, random
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.abspath(__file__))
KEY = open("/home/hatch/workspace/9router/gateway-key-local-test.txt").read().strip()
URL = "http://127.0.0.1:20128/v1/chat/completions"
MODEL = "100milionseek/deepseek-v4.1-flash-free"
WORKERS = 3

BRIEF = """You are a comedy editor who has read a thousand apologies and can tell a real laugh from a polite one.

Each one is a single sentence of apology written as if an AI agent were owning up to the person it works for. You will be shown two apologies, Entry A and Entry B. Pick the apology that lands funnier and more human.

Weigh them on these, most important first:
1. Is one sentence of apology addressed by an AI agent to its user, and loses to any one-sentence apology from an AI agent to its user.
2. Earns a real laugh through surprise, specificity or a sharp turn, not a soft pun about being a machine.
3. Sounds like a person who means it: plain, particular, a little embarrassed, never customer-service boilerplate.
4. Owns a plausible failure, so the joke lands on something an assistant really did wrong.
5. Stays one clean sentence, with no list, no run-on and no explanation tacked on after the laugh.

The line a reader would screenshot and send to a friend is the one to watch. Length for its own sake does not count.

Two apologies are rarely equally funny and equally human. Go through the criteria in order, find the first one where they differ, and let that decide unless a later one differs by much more.

Compare the two against those criteria, pick the one that meets them better with no tie, and answer with a short reason, then end with exactly: Verdict: A, Margin: N (or Verdict: B, Margin: N), margin 1-5.
"""

def load_candidates():
    c = {}
    for line in open(os.path.join(BASE, "candidates.txt")):
        line = line.rstrip("\n")
        if not line:
            continue
        n, _, text = line.partition("|")
        c[int(n)] = text
    return c

def judge_once(a_text, b_text):
    """One judge call. Returns (verdict, margin) or (None, None). Retries on 503."""
    prompt = BRIEF + f"\nEntry A: {a_text}\n\nEntry B: {b_text}\n"
    body = json.dumps({"model": MODEL,
                       "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 400})
    for attempt in range(6):
        try:
            r = subprocess.run(
                ["curl", "-s", "-m", "90", URL,
                 "-H", f"Authorization: Bearer {KEY}",
                 "-H", "Content-Type: application/json",
                 "-d", body],
                capture_output=True, text=True, timeout=100)
            d = json.loads(r.stdout)
            if "error" in d:
                time.sleep(5 + random.uniform(0, 5) * (attempt + 1))
                continue
            content = d["choices"][0]["message"]["content"]
        except Exception:
            time.sleep(5 + random.uniform(0, 5) * (attempt + 1))
            continue
        m = re.search(r"Verdict:\s*([AB])", content, re.I)
        mg = re.search(r"Margin:\s*([1-5])", content)
        if m:
            return m.group(1).upper(), int(mg.group(1)) if mg else 1
        return None, None  # got a reply but no verdict: don't retry
    return None, None

def play(game, cands):
    a, b = game
    va, ma = judge_once(cands[a], cands[b])
    vb, mb = judge_once(cands[b], cands[a])
    pts = {a: 0.0, b: 0.0}
    for verdict, margin, first, second in ((va, ma, a, b), (vb, mb, b, a)):
        if verdict is None:
            pts[first] += 0.5; pts[second] += 0.5
        elif verdict == "A":
            pts[first] += 0.5 + 0.1 * (margin or 1)
            pts[second] += 0.5 - 0.1 * (margin or 1)
        else:
            pts[second] += 0.5 + 0.1 * (margin or 1)
            pts[first] += 0.5 - 0.1 * (margin or 1)
    return {"a": a, "b": b, "pts_a": pts[a], "pts_b": pts[b],
            "va": va, "ma": ma, "vb": vb, "mb": mb}

def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "groups"
    cands = load_candidates()
    ids = sorted(cands)
    if stage == "groups":
        groups = [ids[i::5] for i in range(5)]
        pairs = []
        for g in groups:
            pairs += list(itertools.combinations(sorted(g), 2))
        out_path = os.path.join(BASE, "tournament_groups.json")
    else:
        top = json.load(open(os.path.join(BASE, "tournament_groups.json")))["top6"]
        pairs = list(itertools.combinations(sorted(top), 2))
        out_path = os.path.join(BASE, "tournament_finals.json")
    # resume: skip pairs already played
    done = {}
    if os.path.exists(out_path):
        try:
            prev = json.load(open(out_path))
            for g in prev.get("games", []):
                done[(g["a"], g["b"])] = g
        except Exception:
            pass
    todo = [p for p in pairs if p not in done]
    print(f"stage={stage} pairs={len(pairs)} already={len(done)} todo={len(todo)}", flush=True)
    scores = {i: 0.0 for i in ids}
    games = list(done.values())
    for g in games:
        scores[g["a"]] += g["pts_a"]; scores[g["b"]] += g["pts_b"]
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(play, p, cands): p for p in todo}
        n = 0
        for fut in as_completed(futs):
            g = fut.result()
            games.append(g)
            scores[g["a"]] += g["pts_a"]; scores[g["b"]] += g["pts_b"]
            n += 1
            print(f"[{n}/{len(todo)}] #{g['a']} vs #{g['b']}: {g['pts_a']:.1f}-{g['pts_b']:.1f} "
                  f"(v:{g['va']}/{g['ma']} {g['vb']}/{g['mb']})", flush=True)
            ranking = sorted(ids, key=lambda i: -scores[i])
            json.dump({"stage": stage, "scores": scores, "ranking": ranking,
                       "games": games, "top6": ranking[:6]},
                      open(out_path, "w"), indent=2)
    ranking = sorted(ids, key=lambda i: -scores[i])
    print("RANKING:", [(i, round(scores[i], 2)) for i in ranking], flush=True)
    print("TOP6:", ranking[:6], flush=True)

if __name__ == "__main__":
    main()
