# Blaque Baux Block

**A block of derivative strategies, bundled into one book.**

Block is a member of the Blaque Baux family. The [core repo](https://github.com/Carter-Warrens/blaquebaux)
is the **engine and blueprint** — a governed, systematic platform (Julia) with a venue-agnostic
execution controller and a Layer-3 live-money safety gate. Block points that engine in its own
direction and inherits the governance wholesale.

> **Not investment advice.** Educational/research software. Nothing here is validated. See [LICENSE](LICENSE).

```bash
git clone --recursive https://github.com/Carter-Warrens/blaquebaux-block.git
julia --project=engine -e 'using Pkg; Pkg.instantiate()'   # one-time engine setup
```

## The thesis

A meta-sleeve spanning the **four derivative blocks — equity, FX, rates, commodities — combined into
one book.** The organizing question: those blocks are more *interlocked* than people credit (a stronger
currency hurts the home country's exporters; higher rates raise the cost of doing business and hit
equity), so a book that spans all four must map those linkages — to know whether it is genuinely
diversified or secretly one macro bet, and whether the interlocks are alpha or only risk.

## Research — first pass done

Full detail in [`research/README.md`](research/README.md). The scorecard:

| # | Question | Verdict |
|---|----------|---------|
| 1 | Are the 4 blocks one interlocked factor? | ⚠️ interlocked but **more diversified than interlocked** — 8 proxies → 4.6/8 bets; dollar is a weak hub |
| 2 | Currency → home equity (H1)? | ✅ real — strong yen vs *local* Japan **−0.47**; but wrapper cancels it (+0.01) and it's export/EM-only |
| 2 | Rates → equity (H2)? | ✅ real but **regime-dependent** — stock-bond corr −0.36 (2016–21) → **+0.11** (2022+) |
| 3 | Is the interlock tradeable? | ❌ not lead-lag alpha (priced in); ✅ cross-asset trend +0.43 and **4-block hold +1.19 at 4.1/5 bets** |

**The synthesis:** the intuition is right — the blocks genuinely interlock — but the research reframes
it. The links are real yet *weak* (the four blocks still carry ~4.6 of 8 independent factors, far more
than the ~19% within one equity block — they are more diversified than interlocked). H1 holds only in
*local* currency terms and is cancelled inside the USD wrappers you'd actually trade; H2 holds only in
an inflation regime and flips sign in a growth-scare one. And the interlocks are priced instantly (no
lead-lag edge). What earns its keep is **owning the four blocks as a diversified book (+1.19 Sharpe,
4.1/5 bets) and trend-following them** — the linkages are for hedging and sizing, not stat-arb.

## Status
**Research: first pass complete — a diversified cross-asset basket + risk framework, not linkage stat-arb**
(`research/`). The interlock is a risk map; diversification is the edge. No live driver; nothing validated
to the spine's bar.

## The Blaque Baux family
This repo is one sleeve of the **Blaque Baux** family — a single governed engine steered in
many directions. The [core repo](https://github.com/Carter-Warrens/blaquebaux) is the
base/blueprint and holds the [full family roster](https://github.com/Carter-Warrens/blaquebaux#the-blaque-baux-family).

## Layout
```
engine/     the Blaque Baux platform (git submodule -> Carter-Warrens/blaquebaux)
research/   three Path-A sketches (linkage web, linkages tested, tradeability) + scorecard
live/       governed live drivers (once a sleeve graduates to paper A/B)
```

## License
[MIT](LICENSE). (c) 2026 Carter Warrens.
