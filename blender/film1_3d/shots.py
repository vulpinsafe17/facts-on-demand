"""Film 1 in 3D: one entry per picture scene (timeline.json index). Times are seconds from the scene start.
cast: C(id, who, loc, rz, era/king/expr/exprs/npc) | acts: (id, action, *args) | props: (kind, name, *args)
cam:  push(...) / orbit(...) / crane(...) — the camera never stands still (approved London-demo style)."""
import math

PI = math.pi


def C(id, who="main", loc=(0, 0, 0), rz=0.0, era=None, king=None, expr=None, exprs=None, npc=None, npc_era=None):
    return dict(id=id, who=who, loc=loc, rz=rz, era=era, king=king, expr=expr, exprs=exprs, npc=npc, npc_era=npc_era)


def push(p0, p1, t0, t1=None, lens=35):
    return dict(kind="push", p0=p0, p1=p1, t0=t0, t1=t1 or t0, lens=lens)


def orbit(c, r, h, a0, a1, lens=35, th=None):
    return dict(kind="orbit", c=c, r=r, h=h, a0=a0, a1=a1, lens=lens, th=th)


def keys(lst, lens=35):
    """[(sec, cam_pos, target), ...]"""
    return dict(kind="keys", k=lst, lens=lens)


def crowd(prefix, era, xs, y, rz=0.0, seed=0, act="cheer", t0=0.3, t1=None, ys=None):
    out_c, out_a = [], []
    for i, x in enumerate(xs):
        yy = ys[i] if ys else y + ((i * 37) % 5) * 0.25
        cid = f"{prefix}{i}"
        out_c.append(C(cid, "npc", (x, yy, 0), rz + ((i * 13) % 7 - 3) * 0.06, npc=seed + i, npc_era=era))
        if act:
            out_a.append((cid, act, t0 + (i % 3) * 0.15, t1 or 99))
    return out_c, out_a


def S(**kw):
    kw.setdefault("cast", []); kw.setdefault("acts", []); kw.setdefault("props", [])
    return kw


_cr22, _ca22 = crowd("vA", "medieval", [-3, -2, -1, 0, 1], -2, rz=PI / 2, seed=40, act=None)
_cr22b, _ca22b = crowd("vB", "medieval", [-3, -2, -1, 0, 1], 2, rz=-PI / 2, seed=50, act=None)
_cr24, _ca24 = crowd("mob", "medieval", [-1.2, -0.6, 0.0, 0.6, 1.2, -0.3, 0.3], 5.5, seed=60, act="cheer", t0=0.2)
_cr26, _ca26 = crowd("mer", "medieval", [-2.5, -1.4, 1.4, 2.5], 3.0, seed=70, act="ears", t0=0.4)
_cr27, _ca27 = crowd("cr", "medieval", [-2.2, -1.2, 1.2, 2.2], 1.6, rz=PI, seed=80, act=None)
_cr47, _ca47 = crowd("vp", "victorian", [-4, -3, -2, 2, 3, 4], 9, seed=90, act="cheer", t0=0.5)
_cr6, _ca6 = crowd("hc", "han", [-3, -2.2, -1.4, 1.4, 2.2, 3], -3.2, rz=PI, seed=100, act="cheer", t0=0.6)
_cr12, _ca12 = crowd("sc", "medieval", [-3, -2, 2, 3], 2.8, seed=110, act="cheer", t0=0.5)

SHOTS = {
    # ---------------- chapter 0: the hook
    0: S(set="med-throne-hall", cast=[C("king", "king", (0, 6.6, 1.0), 0, king="edward", exprs=[(1, "angry")])],
         acts=[("king", "holdup", 0.6, 1), ("king", "talk", 1.6, 3.6)],
         props=[("scroll", "decree", "king", "hand1")],
         cam=push((0, -6, 2.2), (0, 2.4, 2.2), (0, 6.6, 1.9), (0, 6.6, 2.1), lens=40)),
    1: S(set="decree-table", cast=[], props=[("cujuball_drop", "ball", (0.0, 1.0, 3.0), (0.05, 1.0, "top+0.55"), 1.2)],
         cam=orbit((0, 1.0, 1.1), 2.6, 1.7, -0.5, 0.35, lens=45)),
    2: S(set="modern-stadium", cast=[], cam=keys([(0, (-70, -90, 60), (0, 0, 0)), (4.43, (-30, -55, 28), (0, 0, 0))], lens=28)),
    3: S(set="scholar-study",
         cast=[C("m", "main", (-1.2, 0.3, 0), 0.35, era="greek", exprs=[(1, "angry")]), C("t", "two", (1.2, 0.3, 0), -0.35, era="victorian", exprs=[(1, "grumpy"), (60, "angry")]),
               C("h1", "npc", (-0.4, 2.6, 0), 0.0, npc=1, npc_era="han"), C("h2", "npc", (0.5, 2.6, 0), 0.0, npc=2, npc_era="heian")],
         acts=[("m", "point", 0.3, 1.2, 1), ("t", "talk", 0.4, 2.2), ("t", "point", 2.2, 1.0, -1), ("h1", "shrug", 1.0), ("h2", "talk", 1.4, 3.2), ("m", "angry", 2.0, 4.0)],
         cam=push((0, -4.5, 1.6), (0.4, -3.2, 1.5), (0, 0.8, 1.1), (0, 0.8, 1.15), lens=35)),
    # ---------------- chapter 1: China
    5: S(set="han-city-dusk", cast=[], cam=keys([(0, (-14, -25, 9), (0, 40, 8)), (4.48, (4, -10, 4), (0, 45, 9))], lens=32)),
    6: S(set="han-palace-court",
         cast=[C("m", "main", (-1.0, 0, 0), 0.4, era="han"), C("t", "two", (1.0, 0.4, 0), -0.5, era="han", exprs=[(1, "surprised")])] + _cr6,
         acts=[("m", "kick", 1.0), ("t", "jump", 1.9), ("t", "kick", 2.1, 0), ("m", "cheer", 2.8, 4.0)] + _ca6,
         props=[("cujuball_path", "ball", [(0, (-0.8, -0.3, 0.13)), (1.0, (-0.8, -0.3, 0.13)), (1.6, (0.2, 0.2, 1.8)), (2.1, (0.9, 0.35, 0.9)),
                                           (2.8, (0.0, 4.0, 2.4)), (3.6, (-0.5, 8, 0.13))])],
         cam=push((-3.5, -5.5, 2.0), (2.5, -4.0, 1.6), (0, 0.5, 1.0), (0, 1.5, 1.0), lens=32)),
    8: S(set="han-palace-court", cast=[C("t", "two", (0.4, 0.3, 0), -0.2, era="han", exprs=[(1, "neutral")])],
         acts=[("t", "holdup", 0.4, 1), ("t", "talk", 1.0, 3.2), ("t", "shrug", 3.4, 1.2)],
         props=[("cujuball_hand", "ball", "t", "hand1")],
         cam=push((1.5, -2.4, 1.7), (0.6, -1.4, 1.6), (0.5, 0.2, 1.4), (0.45, 0.2, 1.45), lens=45)),
    9: S(set="han-palace-court", cast=[], props=[("pedestal", "ped", (0, 0, 0)), ("cujuball_spin", "ball", (0, 0, 1.25))],
         cam=orbit((0, 0, 1.2), 2.2, 1.5, -0.6, 0.6, lens=50)),
    10: S(set="han-palace-court", cast=[C("k", "king", (0, 27.6, 2.4), 0, king="gaozu", exprs=[(1, "smug")]), C("m", "main", (-1.2, 6, 0), 0.6, era="han"),
                                       C("t", "two", (1.2, 6, 0), -0.6, era="han")],
          acts=[("k", "point", 0.6, 1.5, 1), ("k", "talk", 2.2, 4.6), ("m", "kick", 1.6), ("t", "cheer", 2.4, 4.0)],
          props=[("cujuball_path", "ball", [(0, (-1.0, 5.7, 0.13)), (1.6, (-1.0, 5.7, 0.13)), (2.4, (0.2, 12, 2.5)), (3.2, (0.0, 19, 1.3))])],
          cam=keys([(0, (0, 18, 4.5), (0, 27.6, 3.4)), (2.0, (2.0, 20, 4.0), (0, 27.6, 3.3)), (5.33, (3.5, -2, 3.0), (0, 8, 1.0))], lens=35)),
    11: S(set="han-training-field", cast=[C("m", "main", (-1.4, 0, 0), 0.3, era="han"), C("t", "two", (1.4, 0.6, 0), -0.3, era="han", exprs=[(1, "angry")]),
                                         C("s1", "npc", (-3.0, 2.0, 0), 0.4, npc=120, npc_era="han"), C("s2", "npc", (3.0, 2.2, 0), -0.4, npc=121, npc_era="han")],
          acts=[("m", "walk", 0.0, 1.2, (-0.6, 0.2)), ("m", "kick", 1.3), ("t", "jump", 2.0), ("s1", "cheer", 2.2, 3.6), ("s2", "point", 1.6, 1.2, -1)],
          props=[("cujuball_path", "ball", [(0, (-0.4, 0.1, 0.13)), (1.3, (-0.4, 0.1, 0.13)), (1.9, (0.8, 0.5, 1.6)), (2.4, (1.5, 0.7, 1.9)), (3.65, (4, 8, 0.13))])],
          cam=push((-2.5, -5.5, 1.5), (1.5, -4.5, 1.8), (0, 0.5, 1), (0.6, 0.8, 1.1), lens=32)),
    12: S(set="song-street", cast=[C("m", "main", (0, 0, 0), 0, era="song", exprs=[(1, "happy")])] + _cr12,
          acts=[("m", "kick", 0.6, 1), ("m", "kick", 1.6, 0), ("m", "kick", 2.6, 1), ("m", "jump", 3.4), ("m", "bow", 4.2, 0.6)] + _ca12,
          props=[("cujuball_path", "ball", [(0, (0.1, -0.35, 0.13)), (0.6, (0.1, -0.35, 0.13)), (1.1, (0, -0.4, 1.6)), (1.6, (-0.1, -0.35, 0.35)),
                                            (2.1, (0, -0.4, 1.7)), (2.6, (0.1, -0.35, 0.35)), (3.3, (0, -0.3, 2.3)), (3.8, (0, -0.3, 2.6)), (4.4, (0.2, -0.5, 0.13))])],
          cam=orbit((0, 0, 1.2), 4.2, 1.4, -0.7, 0.5, lens=35)),
    13: S(set="song-street", cast=[C("m", "main", (0, 0.2, 0), 0, era="song", exprs=[(1, "smug")])],
          acts=[("m", "write", 0.4, 2.6), ("m", "holdup", 2.8, 1)],
          props=[("table", "tbl", (0, -0.3, 0), 1.2, 0.6, 0.7), ("scroll_open", "scr", (0, -0.3, 0.75))],
          cam=push((1.2, -3.0, 1.6), (0.3, -2.0, 1.5), (0, 0, 1.2), (0, 0, 1.3), lens=40)),
    14: S(set="han-palace-court", cast=[C("k", "king", (0, 3.0, 0), 0, king="hongwu", exprs=[(1, "angry")])],
          acts=[("k", "point", 0.8, 2.0, 1, -0.3), ("k", "angry", 3.2, 5.5)],
          props=[("cujuball_still", "ball", (0.3, -1.0, 0.13))],
          cam=keys([(0, (0.8, -3.0, 0.5), (0.3, -1.0, 0.2)), (2.0, (0.6, -2.2, 1.0), (0.2, 1.0, 1.4)), (5.7, (0, -0.5, 1.9), (0, 3.0, 1.9))], lens=35)),
    # ---------------- chapter 2: Greece + Japan
    18: S(set="greek-field", cast=[C("m", "main", (-1.6, 0, 0), PI / 2, era="greek"), C("t", "two", (1.6, 0.4, 0), -PI / 2, era="greek", exprs=[(1, "neutral")])],
          acts=[("m", "throw", 0.8), ("t", "throw", 2.6), ("m", "throw", 4.4), ("t", "talk", 3.2, 5.4, False)],
          props=[("leatherball_path", "ball", [(0, (-1.3, -0.1, 1.0)), (0.8, (-1.3, -0.1, 1.2)), (1.6, (0, 0.2, 2.6)), (2.3, (1.4, 0.4, 1.1)), (2.6, (1.3, 0.4, 1.2)),
                                               (3.4, (0, 0.2, 2.6)), (4.1, (-1.4, -0.1, 1.1)), (4.4, (-1.3, -0.1, 1.2)), (5.2, (0, 0.2, 2.6)), (6.0, (1.4, 0.4, 1.1))])],
          cam=keys([(0, (-6, -5, 1.6), (0, 0.2, 1.2)), (6.0, (5, -5, 1.8), (0, 0.2, 1.2))], lens=30)),
    19: S(set="greek-field", cast=[C("m", "main", (0, 0, 0), PI / 2, era="greek", exprs=[(1, "surprised")]), C("t", "two", (2.1, 0.2, 0), -PI / 2, era="greek", exprs=[(1, "angry")]),
                                   C("g1", "npc", (2.0, -0.9, 0), -2.2, npc=130, npc_era="greek")],
          acts=[("m", "walk", 0.0, 1.0, (0.9, 0)), ("t", "jump", 0.9, 0.3), ("g1", "walk", 0.4, 1.1, (1.1, -0.3)), ("m", "shrug", 1.6, 1.0)],
          props=[("leatherball_carry", "ball", "m", "hand1")],
          cam=push((-1.5, -3.6, 1.4), (-0.5, -2.8, 1.3), (0.8, 0, 1.0), (1.0, 0, 1.0), lens=35)),
    20: S(set="heian-garden", cast=[C("m", "main", (-1.2, 2.2, 0), 0.6, era="heian", exprs=[(1, "happy")]), C("t", "two", (1.2, 2.6, 0), -0.6, era="heian", exprs=[(1, "neutral")]),
                                    C("n1", "npc", (0, 4.4, 0), PI, npc=140, npc_era="heian")],
          acts=[("m", "kick", 0.6), ("t", "kick", 2.0, 0), ("n1", "kick", 3.4), ("m", "kick", 4.8)],
          props=[("cujuball_path", "ball", [(0, (-1.0, 1.8, 0.13)), (0.6, (-1.0, 1.8, 0.2)), (1.3, (0, 2.6, 3.2)), (2.0, (1.0, 2.3, 0.25)), (2.7, (0.4, 3.6, 3.2)),
                                            (3.4, (0, 4.1, 0.25)), (4.1, (-0.6, 3.0, 3.2)), (4.8, (-1.0, 1.9, 0.25)), (5.98, (0, 2.8, 3.4))])],
          cam=orbit((0, 3, 1.2), 7, 2.6, -0.4, 0.4, lens=32)),
    21: S(set="heian-garden", cast=[C("m", "main", (-0.8, 2.4, 0), PI / 2 - 0.6, era="heian", exprs=[(1, "happy")]), C("t", "two", (0.8, 2.4, 0), -PI / 2 + 0.6, era="heian")],
          acts=[("m", "bow", 0.8, 1.0), ("t", "bow", 1.0, 1.0), ("m", "bow", 3.4, 0.8), ("t", "bow", 3.6, 0.8)],
          props=[("cujuball_still", "ball", (0, 2.0, 0.13))],
          cam=push((0, -3.6, 1.4), (0, -1.9, 1.5), (0, 2.2, 0.8), (0, 2.4, 1.2), lens=35)),
    # ---------------- chapter 3: medieval England
    22: S(set="med-muddy-field", cast=[C("m", "main", (-4, 0, 0), PI / 2, exprs=[(1, "angry")]), C("t", "two", (4, 0.3, 0), -PI / 2, exprs=[(1, "angry")])] + _cr22 + _cr22b,
          acts=[("m", "walk", 0.2, 4.0, (-0.8, 0.0), True), ("t", "walk", 0.2, 4.0, (0.8, 0.3), True)] +
               [(c["id"], "walk", 0.3, 4.2, (c["loc"][0] + (3 if c["id"].startswith("vA") else -3) * 1.2, c["loc"][1]), True) for c in _cr22 + _cr22b],
          props=[("leatherball_still", "ball", (0, 0.1, 0.13))],
          cam=keys([(0, (0, -14, 7), (0, 0, 0.5)), (5.28, (0, -7, 2.5), (0, 0.5, 1.0))], lens=30)),
    23: S(set="med-london-street", cast=[C("m", "main", (-0.4, 2.0, 0), 0.4, exprs=[(1, "happy")]), C("t", "two", (0.6, 2.4, 0), -0.4, exprs=[(1, "angry")])] + _cr24,
          acts=[("m", "kick", 0.8), ("t", "angry", 1.4, 3.2), ("m", "cheer", 2.6, 4.4)] + _ca24,
          props=[("leatherball_path", "ball", [(0, (-0.3, 1.6, 0.13)), (0.8, (-0.3, 1.6, 0.13)), (1.4, (0.4, 3.5, 2.2)), (2.0, (0.2, 5.4, 2.6)), (2.6, (-0.4, 5.6, 1.2)),
                                               (3.4, (0.6, 4.6, 2.0)), (4.79, (0, 6, 0.13))])],
          cam=keys([(0, (0.8, -4.6, 2.2), (-0.2, 2.0, 0.6)), (1.0, (0.7, -4.8, 2.4), (-0.1, 2.4, 0.8)), (1.9, (0.3, -5.2, 3.0), (0.2, 5, 2.2)),
                    (3.0, (-1.5, -2.6, 1.8), (0, 3, 1.2)), (4.79, (1.2, -1.8, 1.5), (0.3, 4, 1.4))], lens=35)),   # kick at 0.8 s in the picture (shot check)
    24: S(set="med-london-street", cast=[C("t", "two", (-1.2, 1.4, 0), 0.5, exprs=[(1, "surprised")])] + _cr24,
          acts=[("t", "shrug", 1.2, 1.2)] + _ca24,
          props=[("cart", "cart", (1.4, 2.0, 0), 1.0), ("chickens", "chick", (1.8, 0.8, 0), 0.6), ("leatherball_path", "ball", [(0, (0, 5, 2)), (1.5, (1.2, 2.6, 2.4)), (2.4, (2.6, 1.4, 0.13))])],
          cam=push((-2.5, -4.0, 1.7), (0.5, -3.2, 1.5), (0.2, 1.8, 1.0), (1.0, 1.6, 0.9), lens=32)),
    25: S(set="med-london-street", cast=[C("m", "main", (0.0, 0.4, 0), 0, exprs=[(1, "angry")])] + _cr26, acts=[("m", "ears", 0.3, 5.4)] + _ca26,
          props=[("leatherball_path", "ball", [(0, (-3, 8, 0.13)), (2.0, (0, 9, 2.5)), (3.5, (3, 10, 0.13))])],
          cam=push((0, -3.8, 1.6), (0, -2.6, 1.5), (0, 1.5, 1.2), (0, 1.0, 1.3), lens=35)),
    26: S(set="med-london-street", cast=[C("t", "two", (0, 0.6, 0), 0, exprs=[(1, "grumpy")])] + _cr27,
          acts=[("t", "holdup", 0.3, 1), ("t", "talk", 0.8, 3.6, False)],
          props=[("scroll_open_hand", "procl", "t", "hand1")],
          cam=push((1.2, -3.8, 1.8), (0.3, -2.6, 1.6), (0, 0.6, 1.4), (0, 0.6, 1.4), lens=35)),
    27: S(set="med-london-street", cast=[C("t", "two", (-1.0, 0.2, 0), 0, exprs=[(1, "grumpy")]), C("m", "main", (1.6, 4.0, 0), 0.3, exprs=[(1, "happy")])] + _cr24,
          acts=[("t", "holdup", 0.1, 1), ("t", "talk", 0.3, 2.6, False), ("m", "kick", 1.2)] + _ca24,
          props=[("scroll_open_hand", "procl", "t", "hand1"), ("leatherball_path", "ball", [(0, (1.8, 3.6, 0.13)), (1.2, (1.8, 3.6, 0.13)), (2.0, (0.4, 7, 2.4)), (2.88, (-0.5, 9, 0.13))])],
          cam=push((-2.2, -3.2, 1.6), (-1.6, -3.6, 1.7), (0, 1.5, 1.3), (0.6, 2.5, 1.3), lens=32)),
    28: S(set="med-throne-hall", cast=[C("king", "king", (0, 6.6, 1.0), 0, king="edward", exprs=[(1, "angry")])],
          acts=[("king", "point", 0.3, 2.0, 1, 0.1)],
          cam=push((0.5, 3.5, 2.0), (0.2, 4.4, 2.1), (0, 6.6, 2.0), (0, 6.6, 2.1), lens=40)),
    29: S(set="med-archery-field", cast=[C("m", "main", (-1.5, 0, 0), 0.0, exprs=[(1, "neutral")]), C("a1", "npc", (-3.0, 0.2, 0), 0.0, npc=150), C("a2", "npc", (1.0, 0.1, 0), 0.0, npc=151)],
          acts=[("m", "point", 2.6, 1.6, 1, 0.0), ("a1", "holdup", 0.5, -1), ("a2", "holdup", 1.2, -1)],
          props=[("longbow", "bow1", "a1", "hand0"), ("longbow", "bow2", "a2", "hand0"), ("arrows", "arr", [(0.8, (-3.0, 0.2, 1.3), (-2.0, 14, 1.2)), (1.5, (1.0, 0.1, 1.3), (2.0, 14, 1.2))]),
                 ("leatherball_still", "ball", (0.6, -1.6, 0.13))],
          cam=keys([(0, (2.0, -5.0, 1.6), (0, 4, 1.2)), (3.0, (1.0, -4.2, 1.2), (0.6, -1.6, 0.3)), (5.63, (0.8, -3.6, 0.8), (0.6, -1.6, 0.2))], lens=35)),
    31: S(set="decree-table", cast=[], props=[("leatherball_drop", "ball", (0, 1.0, 2.6), (0.0, 1.0, "top+0.62"), 0.5)],
          cam=orbit((0, 1.0, 1.3), 2.4, 1.5, 0.4, -0.3, lens=45)),
    # ---------------- chapter 4: schools
    32: S(set="school-field-1840s", cast=[C("m", "main", (-2.0, 0, 0), 0.3, era="school", exprs=[(1, "happy")]), C("t", "two", (2.2, 0.5, 0), -0.3, era="school"),
                                          C("b1", "npc", (-3.2, 1.2, 0), 0.5, npc=160, npc_era="school"), C("b2", "npc", (3.4, 1.6, 0), -0.5, npc=161, npc_era="cricket")],
          acts=[("m", "kick", 1.0), ("t", "throw", 1.8), ("b1", "cheer", 2.4, 4.0), ("b2", "kick", 2.8)],
          props=[("leatherball_path", "ball", [(0, (-1.8, -0.3, 0.13)), (1.0, (-1.8, -0.3, 0.13)), (2.0, (-3, 3, 1.4)), (3.0, (-4, 6, 0.13))])],
          cam=push((0, -7, 2.2), (0, -5.5, 1.8), (0, 1, 1), (0, 1, 1), lens=30)),
    33: S(set="school-field-1840s", cast=[C("t", "two", (0, 0, 0), 0, era="school", exprs=[(1, "surprised")])],
          acts=[("t", "jump", 0.6, 0.7), ("t", "holdup", 0.5, 1), ("t", "holdup", 0.5, -1)],
          props=[("leatherball_path", "ball", [(0, (-3, 2, 2.5)), (0.9, (0.2, -0.1, 2.0)), (2.46, (0.2, -0.1, 1.9))])],
          cam=push((0, -3.4, 0.6), (0.3, -3.0, 0.8), (0, 0, 1.4), (0, 0, 1.6), lens=30)),
    34: S(set="school-field-1840s", cast=[C("m", "main", (-0.6, 0, 0), PI / 2 - 0.5, era="school", exprs=[(1, "angry")]), C("t", "two", (0.6, 0, 0), -PI / 2 + 0.5, era="school", exprs=[(1, "grumpy"), (55, "surprised")])],
          acts=[("m", "kick", 1.6), ("t", "jump", 1.9, 0.25), ("t", "angry", 2.6, 5.0)],
          cam=orbit((0, -0.2, 0.9), 3.4, 1.1, -0.25, 0.25, lens=35)),
    35: S(set="cambridge-room", cast=[C("m", "main", (-0.7, 2.1, 0), 0.1, era="victorian", exprs=[(1, "neutral")]), C("t", "two", (0.7, 2.1, 0), -0.1, era="victorian")],
          acts=[("m", "write", 0.5, 5.5), ("t", "talk", 1.2, 3.6)],
          cam=push((0, -2.0, 1.9), (0.3, -0.8, 1.7), (0, 1.5, 1.1), (0, 1.6, 1.1), lens=35)),
    36: S(set="frosty-field", cast=[C("m", "main", (-1.4, 0, 0), 0.4, era="winter"), C("t", "two", (1.4, 0.4, 0), -0.4, era="winter", exprs=[(1, "grumpy")])],
          acts=[("m", "kick", 1.0), ("t", "kick", 2.6, 0), ("m", "kick", 4.2), ("t", "shrug", 5.0, 0.8)],
          props=[("leatherball_path", "ball", [(0, (-1.2, -0.3, 0.13)), (1.0, (-1.2, -0.3, 0.13)), (2.6, (1.2, 0.1, 0.13)), (4.2, (-1.1, -0.2, 0.13)), (6.16, (2, 5, 0.13))]),
                 ("breath", "br", ["m", "t"])],
          cam=push((0, -6, 1.6), (1.0, -5, 1.4), (0, 0, 1), (0, 0.2, 1), lens=32)),
    37: S(set="frosty-field", cast=[C("m", "main", (-1.5, 0, 0), 0, era="winter", exprs=[(1, "happy")]), C("t", "two", (-0.5, 0.1, 0), 0, era="winter"),
                                    C("p1", "npc", (0.5, 0, 0), 0, npc=170, npc_era="winter"), C("p2", "npc", (1.5, 0.1, 0), 0, npc=171, npc_era="winter"),
                                    C("p3", "npc", (-1.0, 0.9, 0), 0, npc=172, npc_era="winter"), C("p4", "npc", (1.0, 0.9, 0), 0, npc=173, npc_era="winter")],
          acts=[("m", "point", 5.5, 1.2, 1, 0.5)],
          props=[("leatherball_still", "ball", (0, -0.6, 0.13))],
          cam=push((0, -7, 1.4), (0, -4.2, 1.3), (0, 0.3, 1.1), (0, 0.3, 1.1), lens=35)),
    # ---------------- chapter 5: 1863
    38: S(set="victorian-street-night", cast=[C("m", "main", (-2.5, -1, 0), 0, era="victorian")],
          acts=[("m", "walk", 0.4, 4.8, (2.2, 4.8))],
          cam=keys([(0, (-1.5, -8, 2.4), (0, 6, 2.2)), (5.8, (1.0, -3.0, 1.8), (3, 6, 1.6))], lens=30)),
    39: S(set="solicitor-office", cast=[C("m", "main", (0, 2.1, 0), 0, era="victorian", exprs=[(1, "neutral"), (110, "happy")])],
          acts=[("m", "write", 0.3, 3.4), ("m", "point", 3.8, 1.6, 1, 0.8), ("m", "talk", 4.2, 6.6)],
          cam=push((1.2, -1.5, 1.8), (0.5, -0.6, 1.7), (0, 1.6, 1.2), (0, 1.8, 1.4), lens=35)),
    40: S(set="tavern-interior", cast=[C("m", "main", (-1.2, 2.6, 0), 0.3, era="victorian"), C("t", "two", (1.2, 2.6, 0), -0.3, era="victorian", exprs=[(1, "grumpy")]),
                                       C("g1", "npc", (0, 2.8, 0), 0, npc=180, npc_era="victorian"), C("g2", "npc", (-2.2, 1.6, 0), PI / 2 + 0.6, npc=181, npc_era="victorian")],
          acts=[("m", "talk", 0.4, 2.8), ("g1", "talk", 3.0, 4.8), ("t", "shrug", 5.0, 1.0), ("g2", "point", 1.4, 1.2, 1)],
          cam=orbit((0, 1.8, 1.2), 3.6, 1.6, -0.5, 0.4, lens=32)),
    41: S(set="tavern-interior", cast=[C("m", "main", (-0.6, 0.4, 0), PI / 2 - 0.5, era="victorian", exprs=[(1, "angry")]), C("t", "two", (0.6, 0.4, 0), -PI / 2 + 0.5, era="victorian", exprs=[(1, "angry")])],
          acts=[("t", "point", 0.4, 1.2, -1, -0.9), ("t", "kick", 1.9, 0), ("m", "angry", 0.6, 4.6), ("t", "talk", 2.6, 4.6)],
          cam=orbit((0, 0.4, 1.1), 2.8, 1.3, -0.3, 0.3, lens=35)),
    42: S(set="tavern-interior", cast=[C("t", "two", (-2.0, 3.0, 0), PI, era="victorian", exprs=[(1, "angry")])],
          acts=[("t", "walk", 0.4, 3.0, (-3.6, 5.3))],
          props=[("door_open", "door", (-3.6, 5.85), 2.6)],
          cam=push((0, -1.0, 1.6), (-1.0, 0.2, 1.6), (-2.6, 4.0, 1.2), (-3.4, 5.2, 1.4), lens=32)),
    44: S(set="victorian-street-night", cast=[C("m", "main", (4.6, 6.0, 0), -PI / 2, era="victorian", exprs=[(1, "happy")]), C("t", "two", (5.0, 7.2, 0), -PI / 2, era="victorian"),
                                              C("g1", "npc", (5.2, 4.8, 0), -PI / 2, npc=190, npc_era="victorian")],
          acts=[("m", "walk", 0.2, 3.0, (1.6, 3.0)), ("t", "walk", 0.4, 3.2, (2.0, 4.6)), ("g1", "walk", 0.5, 3.2, (2.4, 1.8))],
          cam=push((-2.0, -4.0, 1.8), (-1.2, -2.6, 1.6), (3.0, 4.5, 1.2), (2.0, 3.6, 1.2), lens=30)),
    # ---------------- chapter 6: the world
    47: S(set="cricket-ground-1872", cast=[C("m", "main", (-1.2, 6, 0), PI / 2, era="victorian"), C("t", "two", (1.2, 6.3, 0), -PI / 2, era="cricket", exprs=[(1, "surprised")])] + _cr47,
          acts=[("m", "walk", 0.2, 2.0, (-0.4, 6)), ("m", "kick", 2.2), ("t", "jump", 2.8)] + _ca47,
          props=[("leatherball_path", "ball", [(0, (-0.3, 5.7, 0.13)), (2.2, (-0.3, 5.7, 0.13)), (3.0, (1.0, 6.4, 1.8)), (3.6, (2.4, 7, 0.13)), (6.76, (6, 9, 0.13))])],
          cam=keys([(0, (-20, -18, 14), (0, 6, 1)), (3.0, (-4, -2, 2.5), (0, 6, 1)), (6.76, (3, -1, 2), (0.5, 6.2, 1.1))], lens=32)),
    51: S(set="montevideo-1930", cast=[C("m", "main", (-1.0, 0, 0), 0.3, era="cricket", exprs=[(1, "happy")]), C("t", "two", (1.0, 0.3, 0), -0.3, era="cricket", exprs=[(1, "happy")])],
          acts=[("m", "cheer", 0.6, 4.6), ("t", "cheer", 0.9, 4.8)],
          cam=keys([(0, (-40, -60, 30), (0, 10, 5)), (2.2, (-5, -7, 2.4), (0, 0, 1.2)), (5.26, (2.5, -3.8, 1.5), (0, 0, 1.3))], lens=30)),
    # ---------------- chapter 7: ending
    52: S(set="med-london-street", cast=[C("m", "main", (-0.6, 1.0, 0), 0.2, exprs=[(1, "happy")]), C("t", "two", (0.6, 1.2, 0), -0.2, exprs=[(1, "happy")])] + _cr24,
          acts=[("m", "cheer", 0.4, 3.8), ("t", "cheer", 0.6, 4.0)] + _ca24,
          cam=keys([(0, (0, -2.5, 1.5), (0, 1, 1.4)), (4.28, (0.5, -9, 7), (0, 10, 2))], lens=32)),
    53: S(segments=[  # quick cuts through every era
        S(set="han-training-field", dur=2.05, cast=[C("m", "main", (0, 0, 0), 0.3, era="han", exprs=[(1, "happy")])], acts=[("m", "kick", 0.6)],
          props=[("cujuball_path", "ball", [(0, (0.2, -0.3, 0.13)), (0.6, (0.2, -0.3, 0.13)), (1.4, (1.4, 3, 1.8)), (2.05, (2, 5, 0.13))])],
          cam=push((-1.5, -3.6, 1.2), (-0.8, -3.0, 1.3), (0, 0, 1), (0.4, 0.5, 1), lens=32)),
        S(set="greek-field", dur=2.05, cast=[C("t", "two", (0, 0, 0), 0, era="greek", exprs=[(1, "happy")])], acts=[("t", "throw", 0.6)],
          props=[("leatherball_path", "ball", [(0, (0.3, 0, 1.2)), (0.6, (0.3, 0, 1.2)), (2.05, (2, 6, 3))])],
          cam=push((1.5, -3.6, 1.2), (0.8, -3.0, 1.3), (0, 0, 1.1), (0, 0, 1.2), lens=32)),
        S(set="heian-garden", dur=2.05, cast=[C("m", "main", (0, 2.4, 0), 0, era="heian", exprs=[(1, "happy")])], acts=[("m", "kick", 0.5)],
          props=[("cujuball_path", "ball", [(0, (0.1, 2.0, 0.2)), (0.5, (0.1, 2.0, 0.2)), (1.3, (0, 2.2, 3.0)), (2.05, (0.1, 2.0, 0.6))])],
          cam=push((0, -1.5, 1.0), (0, -0.8, 1.2), (0, 2.4, 1.2), (0, 2.4, 1.6), lens=32)),
        S(set="med-london-street", dur=2.05, cast=[C("t", "two", (0, 1.0, 0), 0.2, exprs=[(1, "happy")])] + _cr24[:4], acts=[("t", "cheer", 0.3, 1.9)] + _ca24[:4],
          cam=push((0.5, -2.6, 1.4), (0, -2.0, 1.5), (0, 1.5, 1.3), (0, 1.5, 1.4), lens=32)),
        S(set="victorian-street-night", dur=2.05, cast=[C("m", "main", (0, 0, 0), 0, era="victorian", exprs=[(1, "happy")])], acts=[("m", "cheer", 0.3, 1.8)],
          cam=push((0, -3.0, 1.4), (0, -2.4, 1.5), (0, 0, 1.2), (0, 0, 1.3), lens=32)),
    ]),
    54: S(set="modern-stadium", cast=[C("m", "main", (-1.2, 0, 0), 0.2, era="modern", exprs=[(1, "happy")]), C("t", "two", (1.2, 0.3, 0), -0.2, era="modern", exprs=[(1, "happy")]),
                                      C("k", "king", (0, 1.6, 0), 0, king="edward", exprs=[(1, "happy")])],
          acts=[("m", "kick", 0.6), ("t", "cheer", 1.6, 4.2), ("k", "cheer", 1.8, 4.4, False), ("m", "cheer", 2.0, 4.4)],
          props=[("leatherball_path", "ball", [(0, (-1.0, -0.3, 0.13)), (0.6, (-1.0, -0.3, 0.13)), (1.6, (0, 8, 2.5)), (2.4, (0, 14, 1.2))])],
          cam=keys([(0, (0, -4.5, 1.4), (0, 0.4, 1.2)), (4.73, (0, -40, 30), (0, 0, 1))], lens=32)),
}
