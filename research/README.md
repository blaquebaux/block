# Blaque Baux Block — research

First-pass Path-A research on the **interlocking of the four derivative blocks** — EQUITY, FX,
RATES, COMMODITIES — and whether that interlock is a strategy. Each block is proxied by liquid
US-listed ETFs; two currency-hedged wrappers (DXJ Japan, HEDJ Europe) expose *local* equity with
the currency stripped out. All sketches read Alpaca SIP daily bars (2016–2026), read-only, print results.

```bash
export $(grep -v '^#' ~/.config/blaquebaux/alpaca.env | xargs)   # or source it
python research/block_1_linkage_web.py       # how interlocked are the 4 blocks?
python research/block_2_linkages_tested.py    # do the two proposed linkages hold?
python research/block_3_tradeable.py          # is the interlock a strategy?
```

## Scorecard

| # | Question | Result | Verdict |
|---|----------|--------|---------|
| 1 | Are the 4 blocks one interlocked factor? | 8 cross-block proxies → **4.6/8 bets** (57% eff); dollar hub −0.13…−0.43 | ⚠️ interlocked but **more diversified than interlocked** |
| 2 | Currency → home equity (H1)? | strong yen vs *local* Japan **−0.47**; vs USD-Japan +0.01; strong $ vs EM −0.28 | ✅ real — local & export/EM only; wrapper cancels it |
| 2 | Rates → equity (H2)? | stock-bond corr −0.36 (2016–21) → **+0.11** (2022+) | ✅ real but **regime-dependent** (flips sign) |
| 3 | Is the interlock lead-lag alpha? | UUP→EEM −0.05, TLT→SPY +0.06 | ❌ no — priced instantly |
| 3 | What *is* tradeable? | cross-asset trend +0.43; **4-block hold +1.19 at 4.1/5 bets** | ✅ diversification + trend, not stat-arb |

## The synthesis

Your intuition is **right** — the blocks genuinely interlock — but the research reframes what that
means for a book:

- **The links are real but weak.** The dollar is a hub (UUP correlates −0.13 to −0.43 to every
  other block), yet eight cross-block proxies still carry **~4.6 of 8 independent factors** (57%
  efficient) — versus ~19% within a single equity block. The four blocks are **more diversified than
  interlocked**: the interlock is a shared macro *core* (dollar, risk-on/off, regime), not a collapse
  into one factor. Cross-asset-class is still the real diversifier (the spine's law).

- **H1 (currency → equity) holds — in local terms, for export/EM economies.** A stronger yen vs
  *local* Japanese equity (DXJ, hedged) is **−0.47**: exporters lose, exactly as you said. But vs the
  *USD-priced* wrapper (EWJ) it's **+0.01** — the currency translation cancels the exporter hit inside
  the very instrument you'd trade. It's strong for EM (strong $ vs EEM −0.28) and near-zero for the US
  (−0.13): the reserve issuer isn't the export story. Real, but local, asymmetric, and wrapper-hidden.

- **H2 (rates → equity) holds — in an inflation regime.** Stock-bond correlation is **−0.36** in
  2016–2021 (bonds hedge stocks — H2 reversed) and **+0.11** in 2022–2026 (rates up, both fall — H2
  holds). The linkage is real *and unstable*, flipping sign by regime (Bore's caution, cross-asset).

- **The interlock is not lead-lag alpha.** Yesterday's dollar/rate move has ~0 correlation to today's
  equity — priced instantly (the "correlation is a risk tool, not alpha" law). What survives is
  (a) cross-asset **trend** (+0.43, the robust way to trade sign-flipping relationships) and, far more,
  (b) simply **holding the four blocks** as a diversified book: **+1.19 Sharpe at 4.1/5 effective bets.**

**Verdict:** Block works — but as a **diversified cross-asset basket + risk framework**, not a stat-arb
of the interlocks. The linkages are genuine and worth mapping, but they're for **hedging and sizing**
(a strong dollar is a shared risk across EM/commodities/gold; the stock-bond hedge is regime-conditional),
while the *return* comes from owning the blocks and trend-following them. The interlock is a risk map;
diversification is the edge — the same conclusion Blurred and the multi-sleeve demo reach from the front door.

## Files
- `_block_common.py` — shared helpers + the four-block universe + hedged wrappers.
- `block_1_linkage_web.py` — how interlocked (effective factors, the dollar hub).
- `block_2_linkages_tested.py` — the two proposed linkages (currency→equity, rates→equity + regime flip).
- `block_3_tradeable.py` — lead-lag (priced in), cross-asset trend, and the diversified hold.
