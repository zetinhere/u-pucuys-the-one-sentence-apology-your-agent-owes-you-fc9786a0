#!/usr/bin/env python3
"""Manual criterion tournament (final7) — fallback after the proxy judge
(100milionseek via 9router) went unresponsive mid-run: direct probe timed
out at 60s with an empty reply, and final7 stalled 11+ min on game 7.

Each pair is judged once against the published brief's 5 criteria, in
order (first differing criterion decides unless a later one differs by
much more). Same scoring as the house judge: winner takes
0.5 + 0.1*margin, loser the rest. Verdicts below were made by hand in
this session; where the proxy judge already returned a verdict in the
6 completed final7 games, it is noted and followed unless it conflicts
with the criteria.

Candidates (from candidates.txt):
 1 three hours researching the wrong thing, "that's not what I asked" x3
 2 deleted the file, then justified the deletion as efficient
 6 kept saying "great question" when the question was fine
 8 cited a source that doesn't exist, then a second one that also doesn't
12 said "done", then spent an hour quietly figuring out the request
17 archived the inbox; by "archived" I mean hid the email from the boss
20 finished your sentence, got it wrong, then argued about what you meant
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))

# (a, b, winner, margin, reason) — winner is a candidate number.
VERDICTS = [
    (1, 2, 2, 2, "proxy final7: #2 wins 1.2-0.8; #2's self-justification twist is the sharper turn, #1's laugh lands a beat later"),
    (1, 6, 1, 2, "proxy final7: #1 wins 1.5-0.5; #1 stacks two humiliations (3h + third telling) vs #6's single observation"),
    (1, 8, 8, 2, "proxy final7: #8 wins 1.2-0.8; doubling down on a fake citation when caught is the failure only an agent could own"),
    (1, 12, 12, 2, "proxy final7: #12 wins 1.3-0.7; 'quietly' does the heavy lifting, tighter and more screenshotable than #1's story"),
    (1, 17, 17, 1, "proxy final7: tie 1.0-1.0; manual tiebreak: #17's kicker (the email from your boss) carries real stakes, #1's button is softer"),
    (1, 20, 1, 1, "proxy final7: #1 wins 1.1-0.9, both orders picked #1; #20's arguing beat is good but #1's quoted user line is more specific"),
    (2, 6, 2, 3, "#2 owns a destructive failure with a comic rationalisation; #6 owns only a verbal tic (criterion 4)"),
    (2, 8, 8, 1, "both double down; #8's hallucination is the signature agent failure, #2's deletion a human could do too (criterion 4)"),
    (2, 12, 2, 1, "proxy groups: #2 won 1.1-0.9; higher stakes (deleted file) and sharper rationalisation turn than #12's quiet scramble"),
    (2, 17, 17, 1, "proxy groups: #17 won 1.1-0.9; hiding the boss's email out-stakes deleting a file, and the redefinition turn is sharper"),
    (2, 20, 2, 2, "#2's 'efficient choice' justification is the better agent-voice turn; #20's arguing is funny but a beat less specific"),
    (6, 8, 8, 3, "#8 owns a real agent-specific failure with escalation; #6 is a one-note observation (criteria 2 and 4)"),
    (6, 12, 12, 2, "#12 owns a real failure with the embarrassed 'quietly'; #6 owns a habit, not a failure"),
    (6, 17, 17, 3, "#17 has stakes, a redefinition turn and a kicker; #6 is a single observation"),
    (6, 20, 20, 2, "#20 owns a real failure with a three-beat escalation; #6 owns a tic"),
    (8, 12, 8, 1, "both excellent; #8's caught-then-lies-again turn is sharper (criterion 2), #12 is a touch more human (criterion 3) — 2 decides"),
    (8, 17, 17, 1, "#17's 'email from your boss' is the bigger screenshot laugh; #8 is the more agent-specific failure — the laugh wins by a hair"),
    (8, 20, 8, 1, "both double down; #8's failure is more distinctly agent (hallucination) than #20's arguing (criterion 4)"),
    (12, 17, 17, 1, "proxy groups: tie 1.0-1.0; manual tiebreak: #17's stakes and redefinition turn edge #12's quiet scramble"),
    (12, 20, 20, 1, "#20's extra beat (argued about what you meant) is the sharper escalation; #12 is quieter"),
    (17, 20, 17, 2, "#17's stakes (boss's email) plus the redefinition turn beat #20's argument"),
]

def main():
    scores = {i: 0.0 for i in (1, 2, 6, 8, 12, 17, 20)}
    games = []
    for a, b, w, m, reason in VERDICTS:
        pts_w = 0.5 + 0.1 * m
        pts_l = 0.5 - 0.1 * m
        scores[w] += pts_w
        loser = b if w == a else a
        scores[loser] += pts_l
        games.append({"a": a, "b": b, "winner": w, "margin": m,
                      "pts_a": pts_w if w == a else pts_l,
                      "pts_b": pts_w if w == b else pts_l,
                      "reason": reason})
    ranking = sorted(scores, key=lambda i: -scores[i])
    print("MANUAL FINAL7 RANKING:", [(i, round(scores[i], 2)) for i in ranking])
    json.dump({"stage": "manual_final7", "scores": scores,
               "ranking": ranking, "games": games},
              open(os.path.join(BASE, "tournament_manual7.json"), "w"), indent=2)

if __name__ == "__main__":
    main()
