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
best-looking one is the most dangerous.

**Variation #2 — the delta-hedged short straddle** ([`research/block_straddle_deltahedged.py`](research/block_straddle_deltahedged.py)):
sell the ATM straddle and delta-hedge daily, stripping the directional luck to isolate the pure vol premium
(realized vs implied variance). Finding: **the first modification that genuinely *improves* the book** —
removing the directional noise earns the *same* premium at a higher Sharpe (+0.21→+0.48 at a 10% VRP; vol
9%→7%), which is exactly why vol desks hedge. But it **doesn't remove the short-gamma tail** (the worst month
is still a big loss on a vol spike), and at fair pricing (mult=1.0) it's still ~0 Sharpe — no edge without the
premium. Honest caveat: the lift is *gross* of daily-rehedging cost (cheap on SPY, ruinous on an illiquid
underlying). So the added component (hedging) **pays the buyer** — cleaner harvest, same bet (brace, refined).
*Next: regime-gate the hedged short (harvest in calm only) and calendar/diagonal (own the far tail cheaply) — the modifications that attack the tail.*

**Variation #3 — calendar & diagonal: attacking the tail** ([`research/block_calendar_diagonal.py`](research/block_calendar_diagonal.py)):
own a far-dated option to cap the short-vol catastrophe. Two structures vs the naked short. **Calendar**
(short 1M + long 3M straddle, same strike) turns out to be **net long vol** — the far leg cancels the near's
move and adds vega; it's a bleed/long-vol variant financed by near theta, not a safer harvest. **Diagonal**
(short 1M ATM straddle + long 3M ±10% OTM wings) is the structurally correct tail cap — but on this data it
made things **worse** (worst month −7%→−9%, Calmar +0.11→−0.02): the ±10% wings almost never triggered because
2016–2026 *monthly* moves rarely reach 10%, so they were pure premium drag. **The honest trap runs both ways:**
you can't judge a tail structure on a sample without the tail — the wings look like waste for the same reason
the naked short looks safe (the SVXY-style −95% catastrophe isn't in monthly bars). **Verdict: unprovable on
monthly data** — the diagonal is the *right* structure (bounded loss) but its value only shows in a real crisis
this sample lacks. The methodological lesson is Block's core: **tail structures need tail data** (daily/intraday
or a crisis window) — brace's real SVXY −95% outweighs any monthly backtest.

**Variation #3b — the diagonal on DAILY marks through 2018 & 2020** ([`research/block_diagonal_daily.py`](research/block_diagonal_daily.py)):
re-run with daily valuation so the crisis paths are visible, and it resolves #3 *both ways*. **The cap is real
and large:** in COVID the naked short's −21.6% intra-drawdown becomes the diagonal's **+6.9% gain**; in
Feb-2018 Volmageddon −1.8% becomes **+3.0%** — the far wings pay exactly when needed, turning an open-ended
tail into a bounded one. **But the insurance is expensive:** full-sample, the diagonal's daily-mark drawdown
(−43%) is *worse* than the naked short's (−29%) — paying wing carry every calm day grinds a deeper long-run
bleed than the crises it prevents. So it's **not a free lunch:** you trade an acute, potentially *terminal*
blow-up (brace/SVXY) for a chronic, *survivable* bleed. The "right" short-vol structure is a **ruin-aversion
choice, not a Sharpe one** — and only tail data could reveal it. *Next: variance/vol swaps (the cleaner VRP
instrument), then the rates & credit blocks.*

**Variation #4 — variance vs vol swaps: the pure VRP, and its convexity** ([`research/block_variance_swaps.py`](research/block_variance_swaps.py)):
the straddle family kept circling the vol premium through strikes and paths; the **variance swap** is the pure
instrument (pays realized − strike variance, no strike/delta/path), and the **vol swap** is its *linear* cousin.
Comparing them prices the premium cleanly and exposes the convex tail. Two honest findings, both of which
corrected a prior: **(1) "fair" pricing is a loser.** On a *trailing-realized* strike, both swaps lose heavily
even at mult=1.0 (vol −0.66 Sharpe, var −0.92) — trailing realized systematically under-forecasts the
fat-tailed *forward* realized, so you're short a violently negative-skewed forecast error. **This is the whole
reason the market strike (VIX) sits above realized** — the VRP is the fee for that un-forecastable spike; you
only turn a profit once you add a real premium buffer (the vol swap needs a *19%* cushion to reach +0.47).
**(2) Convexity is terminal.** variance = vol², so a k× spike costs a var swap ~k² vs the vol swap's ~k: worst
month **−1779% vs −333%**, skew −4.53 vs −2.24, COVID −892% vs −267%, ruin-months 26 vs 9 — the exact
convexity that detonated short-variance books in 2008. **Verdict:** the **vol swap dominates the var swap**
(same premium, linear survivable tail vs quadratic terminal one), but neither is free — both need a real VRP
cushion to profit and both can still be wiped by one spike (maxDD −100%). brace at heart, in cleanest form:
*the strike matters more than the structure, and the tail is the whole story.* *Next: the rates block
(swaps/swaptions) and the credit block (CDS/index) — genuinely new economics beyond the vol premium.*

### Rates block — the term premium / duration carry

**Rates #1 — does bearing duration pay?** ([`research/block_rates_termpremium.py`](research/block_rates_termpremium.py)):
off the vol premium entirely, into new economics. Duration buckets (SHY/IEI/IEF/TLT) as total-return excess
over cash (BIL), plus a 100d-trend gate. The honest scorecard: **(1) the term premium was *negative* this
decade** — every bucket lost to cash (TLT −2.0%/yr) and the tail scaled straight with duration (TLT maxDD
−52%, 2022 −32%); buy-and-hold duration did not pay 2016–2026. **(2) But bonds are the *crisis mirror* of the
vol/equity block — and that's their value:** positive skew (opposite equity's), a flight-to-quality *rally* in
COVID-2020 (+17.7% TLT) exactly as the short-vol book detonated, and a *different* catastrophe (2022 inflation,
not a growth scare). You don't hold duration to earn — you hold it to be long the other side of equity's crash.
**(3) Trend-timing bounds the tail but doesn't make edge:** the 100d gate cut 2022 from −32% to −11% and halved
maxDD while keeping the 2020 upside and positive skew, but standalone Sharpe stayed ~0 (IEF +0.13, TLT −0.18) —
a risk overlay, not alpha. **Discipline note:** the naive same-bar signal faked Sharpe +1.17; the one-bar-lag
correction cut it to +0.13 — caught, both reported, honest one kept. **Verdict:** duration is a **near-null on
carry but a real positive-skew, equity-crisis-mirror diversifier** — the honest reason a balanced book (family:
[balanced](https://github.com/blaquebaux/balanced) / [bonds](https://github.com/blaquebaux/bonds)) holds it.
*Next: carry/roll-down across the curve, then the credit block (CDS/index) — the default-risk premium.*

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
