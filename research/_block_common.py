#!/usr/bin/python3
# =============================================================================
# _block_common.py — shared helpers for the BLAQUE BAUX BLOCK sketches.
#
# Block asks whether the four derivative blocks — EQUITY / FX / RATES / COMMODITIES —
# are more INTERLOCKED than credited, and whether that interlock is tradeable. Each
# block is proxied by liquid US-listed ETFs. Two currency-hedged wrappers (DXJ Japan,
# HEDJ Europe) let us see LOCAL equity with the currency stripped out — essential for
# testing "a stronger currency hurts the home country's exporters," since a USD-priced
# foreign ETF already contains the currency.
# Keys come from env only (ALPACA_KEY_ID / ALPACA_SECRET_KEY) — never hardcoded.
# =============================================================================
import os, json, urllib.request, math
import numpy as np

_H = {"APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"],
      "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"]}

BLOCKS = {
    "EQUITY":      ["SPY", "EWJ", "EEM", "EWZ"],
    "FX":          ["UUP", "FXY", "FXE", "CEW"],   # dollar, yen, euro, EM-FX
    "RATES":       ["TLT", "IEF"],                  # long/intermediate Treasuries (price ~ inverse of rates)
    "COMMODITIES": ["DBC", "GLD", "USO", "DBA"],
}
HEDGED = ["DXJ", "HEDJ"]                            # local (currency-hedged) Japan / Europe equity
ALL = [s for g in BLOCKS.values() for s in g] + HEDGED


def _closes(sym, start="2016-01-01", end="2026-08-01"):
    u = (f"https://data.alpaca.markets/v2/stocks/bars?symbols={sym}&timeframe=1Day"
         f"&start={start}&end={end}&adjustment=all&feed=sip&limit=10000")
    b = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=_H), timeout=40)
                  ).get("bars", {}).get(sym, [])
    return {x["t"][:10]: x["c"] for x in b}


def load(extra=()):
    syms = list(dict.fromkeys(ALL + list(extra)))
    D = {s: _closes(s) for s in syms}
    ds = sorted(set.intersection(*[set(v) for v in D.values()]))
    M = np.array([[D[s][d] for s in syms] for d in ds], float)
    return _Bundle(syms, ds, M)


class _Bundle:
    def __init__(self, syms, ds, M):
        self.syms, self.ds, self.M = syms, ds, M
        self.i = {s: syms.index(s) for s in syms}
        self.R = M[1:] / M[:-1] - 1
        self.dd = ds[1:]
        self.T = len(self.R)

    def r(self, s):        return self.R[:, self.i[s]]
    def corr(self, a, b):  return float(np.corrcoef(self.r(a), self.r(b))[0, 1])

    def corr_window(self, a, b, lo, hi):
        m = [k for k, d in enumerate(self.dd) if lo <= d <= hi]
        return float(np.corrcoef(self.R[m, self.i[a]], self.R[m, self.i[b]])[0, 1])

    def eff_bets(self, names):
        C = np.corrcoef(self.R[:, [self.i[s] for s in names]].T)
        lam = np.linalg.eigvalsh(C); return (lam.sum() ** 2) / (lam ** 2).sum()

    def sharpe(self, x):
        x = x[np.isfinite(x)]
        return float(x.mean() / x.std() * math.sqrt(252)) if x.std() > 0 else float("nan")

    def leadlag(self, pred, tgt):
        x = self.r(pred)[:-1]; y = self.r(tgt)[1:]
        return float(np.corrcoef(x, y)[0, 1])

    def trend(self, names, look=126, cost=5.0):
        idx = [self.i[s] for s in names]; Rl = self.R[:, idx]; N = len(idx)
        wp = np.zeros(N); pnl = []; cst = cost / 1e4
        for t in range(look, self.T - 1):
            strg = np.mean([np.sign(np.prod(1 + Rl[t-h+1:t+1], 0) - 1) for h in (63, 126, 252) if t-h+1 >= 0], 0)
            vol = Rl[max(0, t-32):t+1].std(0) + 1e-9
            raw = strg / vol; g = np.abs(raw).sum(); w = raw / g if g > 0 else np.zeros(N)
            pnl.append(float(np.nansum(w * Rl[t+1])) - np.abs(w - wp).sum() * cst); wp = w
        return np.array(pnl)
