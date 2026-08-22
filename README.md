# Blaque Baux Block

**A block of derivative strategies, bundled into one book.**

Block is a member of the Blaque Baux family. The [core repo](https://github.com/blaquebaux/base)
is the **engine and blueprint** — a governed, systematic platform (Julia) with a venue-agnostic
execution controller and a Layer-3 live-money safety gate. Block points that engine in its own
direction and inherits the governance wholesale.

> **Not investment advice.** Educational/research software. Nothing here is validated. See [LICENSE](LICENSE).

```bash
git clone --recursive https://github.com/blaquebaux/block.git
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

## The derivatives reference — catalog, pricing, analytics

Block's second and larger half is the platform's **derivatives reference layer**: the definitive institutional
taxonomy (equity, FX, rates, credit, commodities, municipals, funding), made computable and held to the same
verify-before-claim discipline as the rest of Blaque Baux.

- **[`catalog/`](catalog/) — 120 strategy building blocks.** A machine-readable taxonomy
  ([`derivatives_catalog.json`](catalog/derivatives_catalog.json), [`schema.json`](catalog/schema.json)):
  parties, cash-flow legs, parameters, payoff, variants, and the documented **combination/hedging** plays for
  each. Every entry is a *building block, not standalone alpha* — the value is in composition. Status ladder
  `reference → spec → implemented → validated`.
- **[`pricing/`](pricing/) — reference pricers**, one per major class, keyed to the catalog `id` and each
  proven against its textbook identity (all pass): IRS (par swap = 0 value), FX forward (covered interest
  parity), Black-Scholes option (put-call parity), CDS (credit triangle).
- **[`analytics/`](analytics/) — the cross-cutting layer**: index calculation + the divisor (rebalance
  continuity), price-movement correlation → basket variance / diversification ratio / **implied correlation**,
  beta & sensitivity, dividends & corporate-action adjustments, and the index-vs-basket basis. 12 identities,
  all verified.
- **[`docs/derivatives_framework.md`](docs/derivatives_framework.md)** ties it together; two plays are on the
  record — a **collar guardrail** (SPY Sharpe 1.01→1.39, tail capped, at the cost of upside) and the
  **correlation-regime** finding (diversification collapses in stress, exactly when it's needed).

The through-line: every readout is a **guardrail, not a signal** — what a bespoke book actually owns and where
it's exposed. None of these blocks is a money-maker alone; the value is the comfort and control they lend.

## The variation program — modifying the catalog to death

Block's next phase: take each catalogued derivative and **vary it to death** — combine the carry of one with
the convexity of another, the derivative-of-a-derivative, ATM vs OTM, hedged vs naked — and suss out, with the
family's honest method (P&L, skew, the fat-tail toolkit, benchmark vs the nulls), *which added component is
paying the buyer versus paying the desk*. Finance firms earn a fee on every component bolted onto a bespoke
instrument; the research question is which components genuinely add return, cut risk, or are pure fee-in-a-suit.

**Variation #1 — straddles** ([`research/block_straddle_variations.py`](research/block_straddle_variations.py)):
a Black-Scholes P&L simulator on the real SPY path (implied vol swept, since VIX isn't on the feed), across
long/short straddle and OTM strangle. Findings: (1) **no edge without the vol-risk-premium** — at fair pricing
every variant is ~±0.2 Sharpe noise; the entire return is implied>realized. (2) **Long vol is a cost** (the
bleed profile), worst when you buy a fat post-spike premium that mean-reverts. (3) **The short strangle "wins"
in-sample (+0.92 Sharpe, 72% win-rate) — and that's the trap:** its catastrophic tail simply isn't in
2016–2026 monthly bars, but [brace](https://github.com/blaquebaux/brace)'s SVXY lived it (−95%, Feb-2018). The
straddle is a pure VRP instrument; the variants reshape the premium/tail tradeoff, not the bet — and the
best-looking one is the most dangerous. *Next: delta-hedged (isolate gamma/vega), regime-gated short, calendar/diagonal.*

## About Blaque Baux

**Blaque Baux** is a quantitative research initiative and a subsidiary of **[Carter Warrens](https://carterwarrens.com)**.
[**BlaqueBaux.com**](https://blaquebaux.com) is the home for the work; the code lives here on GitHub — open to
study, test, and build bespoke strategies on top of.

Anyone can point an AI at a market. The edge is **understanding what the data actually says — and turning it
into something you can act on.** We test relentlessly and put most of it *on the record as rejected, with the
reason*; what survives is built, governed, and validated before it is ever called real. That combination —
honest research, reproducible evidence, and execution you can trust — is why Carter Warrens leads on
**strategy and implementation**, not merely uses the tools everyone now has.

## The Blaque Baux family
This repo is one sleeve of the **Blaque Baux** family — a single governed engine steered in
many directions. The [core repo](https://github.com/blaquebaux/base) is the
base/blueprint and holds the [full family roster](https://github.com/blaquebaux/base#the-blaquebaux-family).

## Layout
```
engine/     the Blaque Baux platform (git submodule -> blaquebaux/base)
catalog/    120-block derivatives taxonomy (JSON + schema + index) — the backbone
pricing/    reference pricers (IRS / FX forward / Black-Scholes / CDS) + identity self-test
analytics/  index / correlation / beta / corporate-action layer + self-test
docs/       derivatives_framework.md — the seven considerations, computed and proven
research/   cross-asset linkage sketches + the collar & correlation-regime plays
live/       governed live drivers (once a sleeve graduates to paper A/B)
```

## License
[MIT](LICENSE). (c) 2026 Carter Warrens.
