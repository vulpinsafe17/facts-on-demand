"""Film 1 full version (10:12): one entry per scene, keyed by the FIRST narration line it covers.
kind 'bg' = a 3D shot (rendered by render.py --plan full); 'card' / 'owl' = drawn in Remotion.
Times inside a shot are seconds from the scene start (the first line starts ~0.25 s in)."""
import math
from shots import C, push, orbit, keys, crowd, S, SHOTS as T   # T = the approved test-film shots, reused

PI = math.pi


def card(label):
    return dict(kind="card", label=label)


def owl(label="owl"):
    return dict(kind="owl", label=label)


def W(id, loc, rz=0.0, seed=0, kit="#c8282a", era="modern"):
    d = C(id, "woman", loc, rz, npc=seed)
    d["kit"], d["npc_era"] = kit, era
    return d


def mob(prefix, era, n, y0, seed, act="cheer", spread=4.0, rz=0.0, t0=0.2):
    xs = [(-spread / 2) + spread * i / max(1, n - 1) for i in range(n)]
    ys = [y0 + ((i * 37) % 5) * 0.35 for i in range(n)]
    return crowd(prefix, era, xs, y0, rz=rz, seed=seed, act=act, t0=t0, ys=ys)


_mob1, _mob1a = mob("m1", "medieval", 9, 4.5, 300, act="walk")
_mob1a = [(c["id"], "walk", 0.2, 4.5, (c["loc"][0] * 1.1, -1.5 + (k % 3) * 0.7), True) for k, c in enumerate(_mob1)]
_vic, _vica = mob("vc", "victorian", 7, 3.4, 320, act="cheer")
_ten, _tena = mob("tn", "winter", 8, 3.0, 340, act="cheer", spread=6)
_w20, _w20a = mob("cw", "victorian", 8, 9.0, 360, act="cheer", spread=9)
_uru, _urua = mob("ur", "cricket", 9, 4.0, 380, act="cheer", spread=7)

SCENES = [
    # ---------------- 0 hook
    (0, T[0]),
    (1, T[1]),
    (3, T[2]),
    (4, T[3]),
    (5, S(set="med-muddy-field",
          cast=[C("m", "main", (-1.6, 0, 0), 0.3, era="han", exprs=[(1, "angry")]), C("t", "two", (1.6, 0.2, 0), -0.3, era="victorian", exprs=[(1, "angry")]),
                C("u", "npc", (0, 0.9, 0), 0.0, npc=7, npc_era="medieval")],
          acts=[("m", "point", 0.3, 1.2, 1), ("t", "point", 1.6, 1.2, -1), ("u", "point", 3.2, 1.4, 1, -0.6), ("u", "talk", 3.0, 5.0)],
          cam=push((0, -6.0, 1.7), (0, -4.6, 1.6), (0, 0.4, 1.1), (0, 0.5, 1.2), lens=32))),
    (6, owl()),
    # ---------------- 1 China
    (8, T[5]),
    (9, S(set="han-palace-court", cast=[C("m", "main", (0, 0, 0), 0, era="han", exprs=[(1, "happy")])] + T[6]["cast"][2:],
          acts=[("m", "kick", 0.6, 1), ("m", "kick", 1.5, 0), ("m", "kick", 2.4, 1)] + T[6]["acts"][4:],
          props=[("cujuball_path", "ball", [(0, (0.1, -0.35, 0.13)), (0.6, (0.1, -0.35, 0.13)), (1.05, (0, -0.4, 1.6)), (1.5, (-0.1, -0.35, 0.35)),
                                            (1.95, (0, -0.4, 1.7)), (2.4, (0.1, -0.35, 0.35)), (3.0, (0, -0.3, 2.2)), (3.7, (0.1, -0.35, 0.13))])],
          cam=orbit((0, 0, 1.1), 4.4, 1.3, -0.5, 0.4, lens=35))),
    (10, card('蹴鞠  =  "kick ball"')),
    (11, T[9]),
    (13, T[10]),
    (15, T[11]),
    (16, T[12]),
    (18, S(set="han-palace-court", cast=[C("k", "king", (0, 3.2, 0), 0, king="huizong", exprs=[(1, "surprised"), (90, "happy")]),
                                          C("m", "main", (0, 0.6, 0), PI, era="song", exprs=[(1, "happy")])],
           acts=[("m", "kick", 0.6, 1), ("m", "kick", 1.4, 0), ("m", "kick", 2.2, 1), ("k", "cheer", 3.0, 5.0, False)],
           props=[("cujuball_path", "ball", [(0, (0.1, 0.9, 0.13)), (0.6, (0.1, 0.9, 0.13)), (1.0, (0, 0.9, 1.6)), (1.4, (-0.1, 0.9, 0.35)),
                                             (1.8, (0, 0.9, 1.7)), (2.2, (0.1, 0.9, 0.35)), (2.8, (0, 0.9, 2.3)), (3.5, (0.1, 0.9, 0.13))])],
           cam=push((2.2, -2.0, 1.6), (1.2, -1.2, 1.6), (0, 2.0, 1.3), (0, 2.6, 1.6), lens=35))),
    (19, S(set="han-palace-court", cast=[C("k", "king", (0.8, 2.0, 0), -0.4, king="huizong", exprs=[(1, "smug")]),
                                          C("m", "main", (-0.8, 1.6, 0), 0.5, era="han", exprs=[(1, "surprised"), (70, "happy")])],
           acts=[("k", "point", 0.5, 1.4, -1), ("k", "talk", 2.0, 4.6), ("m", "bow", 1.4, 0.8), ("m", "cheer", 3.4, 5.4)],
           cam=push((0, -2.8, 1.7), (0.4, -2.0, 1.6), (0, 1.8, 1.3), (0, 1.8, 1.4), lens=35))),
    (20, S(set="song-street", cast=[C("m", "main", (0, 0, 0), 0, era="han", exprs=[(1, "smug")])],
           acts=[("m", "kick", 0.4, 1), ("m", "kick", 1.1, 0), ("m", "kick", 1.8, 1), ("m", "kick", 2.5, 0)],
           props=[("cujuball_path", "ball", [(0, (0.1, -0.35, 0.13)), (0.4, (0.1, -0.35, 0.13)), (0.75, (0, -0.4, 1.3)), (1.1, (-0.1, -0.35, 0.35)),
                                             (1.45, (0, -0.4, 1.3)), (1.8, (0.1, -0.35, 0.35)), (2.15, (0, -0.4, 1.3)), (2.5, (-0.1, -0.35, 0.35)), (3.4, (0, -0.3, 2.0))])],
           cam=push((0, -2.4, 1.2), (0, -1.8, 1.3), (0, 0, 1.0), (0, 0, 1.3), lens=38))),
    (21, T[14]),
    (23, S(set="han-palace-court", cast=[C("k", "king", (0, 3.0, 0), 0, king="hongwu", exprs=[(1, "angry")]), C("s", "npc", (1.6, 1.2, 0), -0.7, npc=400, npc_era="han")],
           acts=[("k", "point", 0.4, 2.2, 1, 0.0), ("s", "shrug", 1.2, 1.4)],
           props=[("cujuball_still", "ball", (1.2, 0.6, 0.13))],
           cam=push((0.6, -1.6, 1.8), (0.3, -0.8, 1.9), (0, 3.0, 1.8), (0, 3.0, 1.9), lens=38))),
    (24, card("RED CARD")),
    (25, owl()),
    (27, card("CHINA  ·  ?  ·  ENGLAND")),
    # ---------------- 2 the ancient world
    (29, T[18]),
    (31, T[19]),
    (32, S(set="greek-field", cast=[C("r1", "npc", (-1.4, 0, 0), PI / 2, npc=410, npc_era="greek"), C("r2", "npc", (1.4, 0.3, 0), -PI / 2, npc=411, npc_era="greek"),
                                     C("r3", "npc", (0.2, 1.6, 0), PI, npc=412, npc_era="greek")],
           acts=[("r1", "throw", 0.8), ("r2", "holdup", 1.6, -1), ("r2", "throw", 2.8), ("r3", "jump", 3.4), ("r3", "cheer", 4.0, 6.0)],
           props=[("leatherball_path", "ball", [(0, (-1.2, -0.1, 1.1)), (0.8, (-1.2, -0.1, 1.2)), (1.6, (1.2, 0.3, 1.5)), (2.8, (1.2, 0.3, 1.5)), (3.5, (0.2, 1.5, 2.2)), (4.2, (0.2, 1.4, 1.4))])],
           cam=orbit((0, 0.4, 1.1), 5.0, 1.6, -0.4, 0.3, lens=32))),
    (33, T[20]),
    (35, T[21]),
    (36, S(set="heian-garden", cast=[C(f"k{i}", "npc", (math.sin(i * 1.26) * 1.6, 3 + math.cos(i * 1.26) * 1.6, 0), PI - i * 1.26, npc=420 + i, npc_era="heian") for i in range(5)],
           acts=[(f"k{i}", "kick", 0.6 + i * 0.9, i % 2) for i in range(5)],
           props=[("cujuball_path", "ball", [(0, (0, 3, 0.4)), (0.6, (0.4, 1.6, 0.3)), (1.1, (0.6, 2.6, 3.0)), (1.5, (1.4, 3.4, 0.3)), (2.0, (0.5, 3.6, 3.0)),
                                             (2.4, (0.6, 4.4, 0.3)), (2.9, (-0.2, 4.0, 3.0)), (3.3, (-1.4, 3.6, 0.3)), (3.8, (-0.6, 3.0, 3.0)), (4.2, (-0.9, 1.8, 0.3)), (5.0, (0, 3, 3.2))])],
           cam=keys([(0, (0, -6, 4.5), (0, 3, 0.8)), (4.6, (3, -4, 2.2), (0, 3, 1.2))], lens=30))),
    (37, S(set="ballcourt", cast=[C(f"p{i}", "npc", (-1.0 + i * 0.7, 2 + (i % 2) * 2.0, 0), 0 if i % 2 else PI, npc=430 + i, npc_era="greek") for i in range(4)],
           acts=[("p0", "jump", 1.2, 0.3), ("p3", "jump", 2.6, 0.3), ("p1", "cheer", 4.0, 7.0), ("p2", "point", 3.4, 1.2, 1, 0.6)],
           props=[("leatherball_path", "ball", [(0, (-1, 2.2, 0.6)), (1.2, (-1.0, 2.2, 0.7)), (2.0, (0.6, 3.4, 1.8)), (2.6, (1.1, 4.0, 0.7)), (3.6, (0.3, 2.8, 2.2)), (4.4, (5.4, 4, 4.0))])],
           cam=keys([(0, (0, -12, 6), (0, 6, 2)), (3.0, (2.5, -3, 2.0), (0, 3, 1.2)), (8.5, (-2.5, -2.5, 1.6), (0, 3, 1.2))], lens=30))),
    (39, S(set="ballcourt", cast=[C("p", "npc", (0, 1.0, 0), 0, npc=431, npc_era="greek")], acts=[("p", "shrug", 0.4, 1.2), ("p", "angry", 2.2, 4.0)],
           props=[("leatherball_still", "ball", (0.6, 0.4, 0.13))],
           cam=push((0.8, -2.6, 1.3), (0.4, -1.8, 1.3), (0, 1.0, 1.0), (0, 1.0, 1.2), lens=38))),
    # ---------------- 3 medieval England
    (40, T[22]),
    (42, T[23]),
    (44, T[24]),
    (45, T[52]),
    (46, S(set="med-muddy-field", cast=_mob1 + [C("m", "main", (0, 2.2, 0), PI, exprs=[(1, "happy")])], acts=_mob1a + [("m", "walk", 0.3, 4.8, (0, -1.0), True)],
           props=[("leatherball_path", "ball", [(0, (0, 1.6, 0.13)), (4.8, (0, -1.4, 0.13))])],
           cam=keys([(0, (6, -6, 3.5), (0, 2, 0.8)), (5.5, (3, -6, 2.0), (0, 0, 1.0))], lens=30))),
    (47, T[25]),
    (49, T[26]),
    (50, T[27]),
    (51, T[29]),
    (52, S(set="med-throne-hall", cast=[C("king", "king", (0, 6.6, 1.0), 0, king="james", exprs=[(1, "angry")])],
           acts=[("king", "holdup", 0.4, 1), ("king", "talk", 1.0, 6.6)],
           props=[("scroll_open_hand", "procl", "king", "hand1")],
           cam=push((0, -2.0, 2.2), (0, 2.0, 2.1), (0, 6.6, 2.0), (0, 6.6, 2.1), lens=40))),
    (53, S(set="med-archery-field", cast=[C("g", "npc", (0, 0, 0), 0.6, npc=440, npc_era="medieval", exprs=[(1, "surprised")]),
                                          C("king", "king", (1.8, 0.6, 0), -0.6, king="james", exprs=[(1, "angry")])],
           acts=[("g", "throw", 0.8), ("king", "point", 1.4, 1.6, -1), ("king", "angry", 3.0, 4.2)],
           props=[("golfclub", "club", "g", "hand1"), ("leatherball_path", "ball", [(0, (0.2, -0.3, 0.05)), (0.8, (0.2, -0.3, 0.05)), (2.0, (-3, 12, 3)), (3.4, (-5, 20, 0.05))])],
           cam=push((-1.5, -4.2, 1.5), (-0.5, -3.4, 1.5), (0.6, 0.3, 1.1), (0.9, 0.4, 1.2), lens=35))),
    (54, S(set="med-throne-hall", cast=[C("king", "king", (0, 6.6, 1.0), 0, king="henry", exprs=[(1, "happy")])],
           acts=[("king", "holdup", 0.6, 1), ("king", "talk", 2.0, 5.5)],
           props=[("boot", "boot", "king", "hand1")],
           cam=push((0.8, 2.4, 2.2), (0.3, 3.8, 2.1), (0, 6.6, 2.1), (0, 6.6, 2.1), lens=40))),
    (56, S(set="med-throne-hall", cast=[C("king", "king", (0, 6.6, 1.0), 0, king="henry", exprs=[(1, "smug")])],
           acts=[("king", "point", 0.3, 2.0, 1, 0.1), ("king", "talk", 3.0, 5.2)],
           props=[("boot", "boot", "king", "hand0")],
           cam=push((0, 3.2, 2.0), (0.3, 4.4, 2.1), (0, 6.6, 2.0), (0, 6.6, 2.1), lens=40))),
    (57, card('"you base football player"\n— King Lear')),
    (58, T[31]),
    # ---------------- 4 schools + first clubs
    (60, T[32]),
    (62, S(set="school-field-1840s", cast=[C("t", "two", (-1.0, 0.4, 0), 0.4, era="school", exprs=[(1, "happy")]), C("m", "main", (1.2, 0.2, 0), -0.4, era="school")],
           acts=[("t", "holdup", 0.6, 1), ("t", "holdup", 0.6, -1), ("m", "walk", 2.6, 4.4, (3.2, 3.0), True)],
           props=[("leatherball_path", "ball", [(0, (-3, 3, 2.5)), (0.9, (-1.0, 0.1, 1.5)), (2.6, (-1.0, 0.1, 1.5))]), ("leatherball_carry", "ball2", "m", "hand1")],
           cam=push((0, -5.0, 1.7), (0.8, -4.2, 1.6), (0, 0.4, 1.1), (0.8, 1.0, 1.1), lens=32))),
    (63, T[34]),
    (64, S(set="school-field-1840s", cast=[C("m", "main", (-0.7, 0, 0), PI / 2 - 0.5, era="school", exprs=[(1, "angry")]),
                                           C("t", "two", (0.7, 0, 0), -PI / 2 + 0.5, era="cricket", exprs=[(1, "angry")])],
           acts=[("m", "talk", 0.3, 2.6), ("t", "talk", 2.8, 5.0), ("m", "point", 0.8, 1.0, 1), ("t", "point", 3.0, 1.0, -1)],
           props=[("leatherball_still", "ball", (0, -0.6, 0.12))],
           cam=orbit((0, 0, 1.0), 3.2, 1.2, -0.3, 0.3, lens=35))),
    (65, S(set="school-field-1840s", cast=[C("b", "npc", (-2.0, 0, 0), PI / 2, npc=450, npc_era="school", exprs=[(1, "happy")]),
                                           C("o1", "npc", (1.0, 1.0, 0), -2.0, npc=451, npc_era="school", exprs=[(1, "surprised")])],
           acts=[("b", "walk", 1.2, 4.6, (4.0, 1.5), True), ("o1", "shrug", 2.0, 1.4)],
           props=[("leatherball_carry", "ball", "b", "hand1")],
           cam=keys([(0, (-2.5, -4.0, 1.6), (-2.0, 0, 1.0)), (5.6, (2.0, -4.0, 1.6), (3.0, 1.2, 1.0))], lens=32))),
    (66, S(set="scholar-study", cast=[C("h1", "npc", (-0.8, 0.4, 0), 0.3, npc=460, npc_era="victorian"), C("h2", "npc", (0.8, 0.4, 0), -0.3, npc=461, npc_era="school")],
           acts=[("h1", "shrug", 0.6, 1.4), ("h2", "talk", 1.4, 4.4)],
           cam=push((0, -3.6, 1.6), (0, -2.8, 1.5), (0, 0.8, 1.2), (0, 0.8, 1.2), lens=35))),
    (67, T[35]),
    (69, S(set="frosty-field", cast=[C("m", "main", (-1.2, 0, 0), 0.3, era="cricket", exprs=[(1, "grumpy")]), C("t", "two", (1.2, 0.3, 0), -0.3, era="cricket", exprs=[(1, "grumpy")])],
           acts=[("m", "shrug", 1.0, 1.2), ("t", "talk", 2.6, 5.4)],
           cam=push((0, -5.0, 1.5), (0.6, -4.0, 1.4), (0, 0.3, 1.1), (0, 0.3, 1.1), lens=32))),
    (70, T[37]),
    (71, S(set="frosty-field", cast=[C("m", "main", (-1.0, 0, 0), PI / 2 - 0.3, era="winter"), C("h", "npc", (1.0, 0.2, 0), -PI / 2 + 0.3, npc=470, npc_era="winter")] + _ten,
           acts=[("m", "kick", 1.4), ("h", "jump", 2.0), ("h", "kick", 3.6, 0)] + _tena,
           props=[("leatherball_path", "ball", [(0, (-0.8, -0.2, 0.12)), (1.4, (-0.8, -0.2, 0.12)), (2.2, (0.9, 0.1, 0.12)), (3.6, (0.9, 0.1, 0.12)), (4.6, (-2.5, 1.0, 0.12))])],
           cam=orbit((0, 0.5, 1.0), 6.0, 1.8, -0.5, 0.4, lens=30))),
    (72, S(set="frosty-field", cast=[C("m", "main", (0, 0, 0), 0, era="cricket", exprs=[(1, "smug")])], acts=[("m", "shrug", 0.6, 1.6), ("m", "talk", 2.6, 5.0)],
           cam=push((0, -2.6, 1.3), (0, -2.0, 1.4), (0, 0, 1.2), (0, 0, 1.3), lens=38))),
    # ---------------- 5 1863
    (73, T[38]),
    (74, T[39]),
    (75, S(set="solicitor-office", cast=[C("m", "main", (0, 2.1, 0), 0, era="victorian", exprs=[(1, "happy")])], acts=[("m", "holdup", 0.3, 1), ("m", "talk", 0.8, 3.0)],
           props=[("scroll_open_hand", "letter", "m", "hand1")],
           cam=push((0.6, -1.0, 1.8), (0.2, -0.4, 1.7), (0, 1.8, 1.5), (0, 1.8, 1.5), lens=38))),
    (76, T[44]),
    (77, S(set="tavern-interior", cast=T[40]["cast"], acts=[("m", "cheer", 0.4, 2.6, False), ("t", "cheer", 0.6, 2.6, False), ("g1", "cheer", 0.5, 2.6, False), ("g2", "point", 0.8, 1.2, 1)],
           cam=orbit((0, 1.8, 1.2), 3.8, 1.6, 0.4, -0.2, lens=32))),
    (78, T[40]),
    (80, T[41]),
    (82, S(set="tavern-interior", cast=T[40]["cast"], acts=[("m", "holdup", 0.6, 1), ("m", "talk", 1.0, 5.0), ("g1", "cheer", 4.0, 8.6, False), ("t", "shrug", 6.0, 1.0)],
           props=[("scroll_open_hand", "laws", "m", "hand1")],
           cam=push((0, -0.6, 1.9), (0, 0.4, 1.8), (-1.0, 2.6, 1.5), (-0.6, 2.6, 1.6), lens=35))),
    (83, T[42]),
    (84, card("FOOTBALL   |   RUGBY")),
    (85, S(set="frosty-field", cast=[C("m", "main", (-1.0, 0, 0), 0.4, era="victorian", exprs=[(1, "grumpy")]), C("t", "two", (1.0, 0.3, 0), -0.4, era="victorian", exprs=[(1, "grumpy")])],
           acts=[("m", "shrug", 1.0, 1.2), ("t", "shrug", 3.0, 1.2)],
           props=[("leatherball_still", "ball", (0, -0.5, 0.12))],
           cam=push((0, -5.0, 1.4), (0, -3.8, 1.4), (0, 0.2, 1.0), (0, 0.2, 1.1), lens=32))),
    # ---------------- 6 football goes big
    (86, S(set="cricket-ground-1872", cast=[C("m", "main", (0, 6, 0), 0, era="cricket", exprs=[(1, "happy")])] + _vic,
           acts=[("m", "holdup", 0.6, 1), ("m", "cheer", 4.0, 9.0, False)] + _vica,
           props=[("trophy", "cup", "m", "hand1")],
           cam=keys([(0, (0, -4, 1.8), (0, 6, 1.6)), (10.5, (2.0, 2.0, 1.6), (0, 6, 1.7))], lens=35))),
    (88, T[47]),
    (90, card("0  –  0")),
    (91, S(set="school-field-1840s", cast=[C("m", "main", (-1.5, 2.0, 0), 0.4, era="victorian")], acts=[("m", "point", 1.4, 2.0, 1, 0.7)],
           props=[("goal", "g", (0, 6, 0), "bar")],
           cam=push((0, -3.0, 1.6), (0, -1.0, 1.8), (0, 6, 1.6), (0, 6, 1.9), lens=32))),
    (93, S(set="school-field-1840s", cast=[C("m", "main", (0, 1.0, 0), PI, era="victorian", exprs=[(1, "happy")])], acts=[("m", "kick", 1.2), ("m", "cheer", 2.6, 6.0)],
           props=[("goal", "g", (0, 6, 0), "net"), ("leatherball_path", "ball", [(0, (0.1, 0.6, 0.12)), (1.2, (0.1, 0.6, 0.12)), (2.0, (0.5, 7.2, 1.2)), (2.3, (0.5, 7.3, 0.12))])],
           cam=keys([(0, (1.8, -2.4, 1.4), (0, 3, 1.0)), (6.5, (-1.5, -1.2, 1.5), (0, 6, 1.0))], lens=32))),
    (94, S(set="school-field-1840s", cast=[C("t", "two", (0, 5.7, 0), 0, era="cricket", exprs=[(1, "surprised")]), C("m", "main", (0.2, -2.0, 0), PI, era="victorian", exprs=[(1, "smug")])],
           acts=[("m", "walk", 0.2, 1.4, (0.1, -0.6)), ("m", "kick", 2.0), ("t", "jump", 2.3, 0.4)],
           props=[("goal", "g", (0, 6, 0), "net"), ("leatherball_path", "ball", [(0, (0, -0.1, 0.12)), (2.0, (0, -0.1, 0.12)), (2.5, (-1.8, 6.4, 1.6)), (2.8, (-1.8, 7.2, 0.12))])],
           cam=keys([(0, (0.8, -4.2, 1.5), (0, 3, 1.0)), (8.0, (1.6, 3.0, 1.4), (0, 6, 1.2))], lens=32))),
    (96, S(set="montevideo-1930", cast=[C("m", "main", (-1.0, 0, 0), 0.3, era="cricket"), C("t", "two", (1.0, 0.3, 0), -0.3, era="cricket", exprs=[(1, "happy")])],
           acts=[("m", "kick", 1.0), ("t", "cheer", 2.0, 5.0)],
           props=[("leatherball_path", "ball", [(0, (-0.8, -0.3, 0.12)), (1.0, (-0.8, -0.3, 0.12)), (2.4, (4, 10, 2)), (3.4, (6, 16, 0.12))])],
           cam=keys([(0, (-30, -40, 22), (0, 0, 2)), (5.8, (-4, -6, 2.2), (0, 0, 1.2))], lens=30))),
    (97, S(set="montevideo-1930", cast=[W(f"w{i}", (-2.4 + i * 1.2, 0.3 * (i % 2), 0), (0.4 if i < 2 else -0.4), seed=500 + i, kit="#2a5ac8" if i % 2 else "#c8282a", era="1920") for i in range(5)],
           acts=[("w0", "kick", 1.0), ("w2", "jump", 1.6), ("w2", "kick", 1.9, 0), ("w4", "cheer", 3.0, 9.0), ("w1", "cheer", 3.2, 9.0), ("w3", "cheer", 3.4, 9.0)],
           props=[("leatherball_path", "ball", [(0, (-2.2, -0.2, 0.12)), (1.0, (-2.2, -0.2, 0.12)), (1.9, (0, 0.2, 1.2)), (2.6, (3, 6, 0.12))])],
           cam=keys([(0, (-8, -10, 5), (0, 0, 1)), (4.0, (-2.0, -5.0, 1.8), (0, 0, 1.1)), (11.0, (3.0, -4.6, 1.6), (0, 0, 1.1))], lens=30))),
    (99, S(set="solicitor-office", cast=[C("o", "npc", (0, 2.1, 0), 0, npc=520, npc_era="victorian", exprs=[(1, "grumpy")]), W("w", (1.6, 0.6, 0), -0.8, seed=501, kit="#c8282a", era="1920")],
           acts=[("o", "write", 0.4, 3.0), ("o", "holdup", 3.6, 1), ("o", "talk", 4.0, 8.4)],
           props=[("scroll_open_hand", "ban", "o", "hand1")],
           cam=push((0.8, -1.2, 1.8), (0.2, -0.4, 1.7), (0, 1.8, 1.4), (0, 1.8, 1.5), lens=36))),
    (101, S(set="modern-stadium", cast=[W(f"w{i}", (-1.8 + i * 0.9, 0.2 * (i % 2), 0), 0, seed=530 + i, kit="#ef7a1d") for i in range(5)],
            acts=[(f"w{i}", "cheer", 0.3 + i * 0.1, 3.2) for i in range(5)],
            cam=keys([(0, (0, -4.6, 1.4), (0, 0.3, 1.2)), (3.6, (0, -7.0, 2.6), (0, 0.3, 1.2))], lens=32))),
    # ---------------- 7 the world
    (102, card("SAILORS  ·  ENGINEERS\nTEACHERS  ·  STUDENTS")),
    (103, S(set="solicitor-office", cast=[C(f"d{i}", "npc", (-1.6 + i * 0.8, 2.2 + (i % 2) * 0.3, 0), 0.1 * (2 - i), npc=540 + i, npc_era="victorian") for i in range(5)],
            acts=[(f"d{i}", "cheer", 1.2 + i * 0.1, 4.0, False) for i in range(5)],
            cam=push((0, -1.8, 1.8), (0, -0.8, 1.7), (0, 2.0, 1.3), (0, 2.0, 1.4), lens=32))),
    (104, card("FIFA  1904\n7 founding nations")),
    (105, card("ENGLAND  JOINS:  1905")),
    (106, T[51]),
    (107, S(set="montevideo-1930", cast=[C("m", "main", (0, -0.6, 0), PI, era="cricket", exprs=[(1, "happy")])], acts=[("m", "kick", 1.0), ("m", "cheer", 2.0, 4.4)],
            props=[("goal", "g", (0, 6, 0), "net"), ("leatherball_path", "ball", [(0, (0.1, -0.9, 0.12)), (1.0, (0.1, -0.9, 0.12)), (1.8, (1.4, 6.6, 1.4)), (2.1, (1.4, 7.2, 0.12))])],
            cam=keys([(0, (1.2, -3.4, 1.3), (0, 2, 1.0)), (4.6, (-1.4, -2.4, 1.5), (0, 5, 1.2))], lens=32))),
    (108, S(set="montevideo-1930", cast=[C("t", "two", (0, 0, 0), 0, era="cricket", exprs=[(1, "sad")])], acts=[("t", "shrug", 0.6, 1.6)],
            cam=push((0, -2.4, 1.3), (0, -1.9, 1.4), (0, 0, 1.2), (0, 0, 1.3), lens=38))),
    (109, S(set="montevideo-1930", cast=[C("m", "main", (-0.8, 0, 0), 0.2, era="cricket", exprs=[(1, "happy")]), C("t", "two", (0.8, 0.2, 0), -0.2, era="cricket", exprs=[(1, "happy")])] + _uru,
            acts=[("m", "cheer", 0.3, 5.6), ("t", "cheer", 0.5, 5.6)] + _urua,
            cam=keys([(0, (0, -3.0, 1.5), (0, 1, 1.4)), (6.2, (0, -12, 8), (0, 5, 2))], lens=32))),
    # ---------------- 8 ending
    (110, owl()),
    (112, S(segments=[dict(sg, dur=2.3) for sg in T[53]["segments"]] + [
        S(set="school-field-1840s", dur=2.3, cast=[C("t", "two", (0, 0, 0), 0, era="school", exprs=[(1, "angry")])], acts=[("t", "kick", 0.6, 0)],
          cam=push((0.8, -2.8, 1.3), (0.3, -2.2, 1.4), (0, 0, 1.1), (0, 0, 1.2), lens=34)),
        S(set="tavern-interior", dur=2.3, cast=T[40]["cast"], acts=[("m", "cheer", 0.3, 2.0, False), ("g1", "cheer", 0.4, 2.0, False)],
          cam=push((0, -0.4, 1.8), (0, 0.3, 1.7), (0, 2.6, 1.4), (0, 2.6, 1.5), lens=32)),
        S(set="modern-stadium", dur=2.3, cast=[C("m", "main", (0, 0, 0), 0, era="modern", exprs=[(1, "happy")])], acts=[("m", "cheer", 0.3, 2.0)],
          cam=push((0, -3.0, 1.4), (0, -2.4, 1.5), (0, 0, 1.2), (0, 0, 1.3), lens=32)),
    ])),
    (115, S(set="modern-stadium", cast=[], cam=keys([(0, (-30, -50, 26), (0, 0, 0)), (7.1, (30, -50, 26), (0, 0, 0))], lens=26))),
    (116, T[54]),
    (117, owl()),
]


def _norm(sh):
    if "kind" not in sh:
        sh = dict(sh)
        sh["kind"] = "bg"
    return sh


SCENE_LIST = [(i, first, _norm(sh)) for i, (first, sh) in enumerate(SCENES)]
SHOTS = {i: sh for i, first, sh in SCENE_LIST if sh["kind"] == "bg"}
