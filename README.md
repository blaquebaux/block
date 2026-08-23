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

**Variation #5 — swaptions: the rate-vol premium and its two tails** ([`research/block_rates_swaption.py`](research/block_rates_swaption.py)):
the rates block of the catalog, modeled as options on duration (payer swaption ≈ put on TLT, receiver ≈ call).
Findings: **(1)** a real *rate* VRP — selling the rate straddle pays and scales with the premium (Sharpe +0.17
fair → **+0.89** at a 19% VRP). **(2)** But rates have **two** tails, not equity's one, and the violent one is
the side I didn't expect: the worst single-month tail is the **receiver / rates-*down*** side (short receiver
worst month −16%, skew −2.66 — the Mar-2020 flight-to-quality bond *spike*), while the payer / rates-up tail
(2022) is a slow **grind** (−17% cumulative, worst month only −8%). **(3)** A twist vs the equity arc: rates
*contain* their worst year (2022) in-sample, so the short-straddle Sharpe is more trustworthy than equity
short-vol's — but negative skew both ways keeps it insurance-writing, and the Bermudan early-exercise feature is
fee-in-a-suit for a seller. **Verdict:** the rate-vol premium is real and **double-tailed**; sell it sized for
*both* tails, never as clean carry.

**Variation #6 — CDS index tranches: the correlation trade, and 2008** ([`research/block_credit_tranches.py`](research/block_credit_tranches.py)):
the credit block's defining machine (tranche / first-to-default / Nth-to-default / synthetic CDO), modeled with
the market-standard one-factor **Gaussian copula**. Findings: **(1) tranching creates nothing** — the invariance
check is exact (Σ tranche loss = portfolio expected loss); it only *redistributes* the same loss by seniority,
so the structuring fee buys slicing, not edge — the purest fee-in-a-suit. **(2) The senior "AAA safety" is a
correlation bet:** at ρ=0.1 the super-senior tranche loses **0.0%** (bulletproof on paper), but as ρ→0.9 the
senior [7–15%] jumps **≈5×** and the super-senior to 1.8–3.9% — in 2008 ρ→1 and the "impossible" AAA losses
simply happened. **(3) The trade *is* the equity/senior split:** equity is *short* correlation (corr-delta
−55%), senior is *long* correlation risk — selling a senior tranche is **writing systemic insurance** (the
steamroller at portfolio level). **Verdict:** the catalog's most infamous instrument makes a senior claim look
safe by hiding a correlation tail inside a flattering metric — *the metric flatters, the tail decides*, in its
most consequential form. 2008 was the bill for selling systemic-correlation insurance and stamping it AAA.

**Variation #7 — CMS: the convexity fee, and where the margin hides** ([`research/block_rates_cms.py`](research/block_rates_cms.py)):
the CMS family of the catalog (constant-maturity swap, CMS spread option, range accrual). A CMS pays a long-tenor
swap rate on a short schedule, forcing a **convexity adjustment** (the fair CMS rate sits above the forward, by
Jensen). Findings: **(1) the adjustment is *real*, not fee-in-a-suit** — its sign is model-independent (Jensen),
and a 10y CMS genuinely carries ~25bp, a 30y ~60bp+. **(2) But the margin hides in the vol mark:** the *same* 10y
CMS is worth **9bp at σ=15% and 49bp at σ=35%** (the 30y swings ~97bp) — purely from the vol *assumption* the
buyer can't observe. The fee isn't a charge, it's a **mark**. **(3) The CMS spread option** (10y−2y steepener)
tells the same story on **correlation** — its value falls **51%** as the rate-rate ρ goes 0→0.9. **The unifying
law (with #6):** exotic value lives in an *unobservable* parameter (σ for CMS, ρ for the spread option and the
tranche), so the "fair price" flatters and the *assumption* decides — the metric-flatters/tail-decides law
applied to **pricing**. **Verdict:** CMS convexity is honestly-earned value, but it's the catalog's clearest case
of a fee that hides in an assumption rather than a line — the "innovation" is the desk's information edge on an
unobservable, not new economics. *Rule: when value depends on σ or ρ, ask for the σ or ρ, not just the price.*

**Variation #8 — commodity structures: crack spread · Asian option · three-way collar** ([`research/block_commodity_structures.py`](research/block_commodity_structures.py)):
three commodity-block structures chosen to span the *honest range* — the program isn't only about traps.
**(1) Crack spread** (UGA gasoline − USO crude, the refiner margin) is a **real, diversifying exposure**: near-zero
equity correlation (+0.05) and — rare — *positive* skew (+1.25; the tail is on the upside, +95% in 2020 as crude
collapsed but products held). Not standalone alpha (Sharpe +0.34), but a genuinely uncorrelated positive-skew
sleeve. **(2) The Asian (average-rate) option is the modification that pays the *buyer*:** averaging cuts the
effective vol (terminal 21% → average 12%, ≈/√3), so it's **44% cheaper** — and the discount is *fair*, a better,
cheaper hedge for anyone with continuous/averaged exposure. Not every modification is desk margin. **(3) The
three-way collar is the trap:** "widen the zero-cost band" by re-selling a deep put, and below that strike you're
*long the crash again* — worst 3-mo **−61% vs the plain collar's −10%** (skew −2.16 vs −0.28); in 2020 oil it blew
through exactly where you thought you were protected. **The sharpened rule (with #6, #7):** a modification pays
the **buyer** when it genuinely *reduces* risk (Asian averaging) and the **desk** when it *hides* risk (the
three-way's re-sold tail, the tranche's correlation, the CMS's vol mark) — *read the payoff to the tail, not the
brochure*; and some structures are honest exposure, neither trick nor trap (the crack spread).

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

**Rates #2 — carry / roll-down: the curve *slope* as the signal** ([`research/block_rates_carry.py`](research/block_rates_carry.py)):
an upward-sloping curve pays you to hold duration (coupon + roll-down); an inverted one doesn't — so the right
signal is the *level of the slope*, not price trend. Slope reconstructed price-only from ETF distribution
yields (IEF yield − BIL cash yield). Findings: **(1) carry is a genuinely distinct signal** — it correlates
just −0.09 with the trend gate, agreeing only 43% of days (trend reads fast price momentum; carry reads the
slow curve state). **(2) Combining them is the best rates result yet:** trend-AND-carry on IEF lifts Sharpe
−0.14 → **+0.30**, maxDD −28% → **−9%**, skew +0.17 → **+0.64**, 2022 −16% → −4%, on just 30% of days (TLT the
same shape) — trend dodges the acute 2022 price crash, carry avoids the 2023 negative-carry inversion, each
covering the other's blind spot. **(3) Honest caveats:** the distribution-yield proxy *lags* (carry-alone rode
the full 2022 crash before registering the inversion in 2023), and even combined the excess return is thin
(~+1%/yr) on one big regime — the win is **risk** (bounded tail, positive skew), not carry harvested.
**Verdict:** carry is a real, distinct signal and **trend+carry is the honest best way to *hold* duration** —
but it's a risk overlay on a crisis-mirror diversifier, not a harvested premium: the curve doesn't pay you to
hold duration this decade, it tells you *when* duration is least dangerous. *Next: the credit block (CDS/index)
— the default-risk premium, the first genuinely earned premium to test since the VRP.*

### Credit block — the default-risk premium

**Credit #1 — real premium, or equity beta in a bond wrapper?** ([`research/block_credit_premium.py`](research/block_credit_premium.py)):
strip the rate risk with a duration-matched Treasury to isolate the pure spread (IG = LQD−IEF, HY = HYG−IEI),
then test the residual with the family toolkit (Jensen's alpha vs SPY + crisis correlation). Findings: **(1) a
gross spread premium exists** — duration-stripped, IG earns +1.6%/yr and HY +3.0%/yr, so credit does pay for
default risk. **(2) But it's equity beta in a wrapper, and *underpaid*:** beta to SPY +0.22 (IG) / +0.39 (HY),
and Jensen's alpha is *negative* (−1.4% / −2.3%) — after the equity risk you're taking, the premium doesn't
vanish, it goes negative (equity-like downside, sub-equity upside this decade). **(3) The crisis tell is
definitive:** on equity's worst 5% days the spread crashes *with* stocks (corr **+0.71** IG, **+0.86** HY) and
the skew is negative (IG **−1.77**) — zero diversification exactly when you need it. **The finding is the
contrast:** credit is the mirror-*opposite* of duration — duration is negative-carry / positive-skew /
crisis-*mirror*; credit is positive-carry / negative-skew / crisis-*correlated*. "Fixed income" is two opposite
factors bolted together, and **only the duration half actually diversifies an equity book.** **Verdict:** the
default-risk premium is not an independent earned premium here — it's underpaid equity beta wearing a bond's
illiquidity; for a cross-asset book, HY credit is not diversification (hold equity directly, or duration for a
real hedge). *Next: gate credit on a risk-on regime (does timing rescue it?), then FX / commodities carry.*

### FX block — the carry premium

**FX #1 — the carry premium: the classic earned return, and its crash tail** ([`research/block_fx_carry.py`](research/block_fx_carry.py)):
FX carry is the most-cited *independent* premium in macro — borrow the low-yielders, lend the high-yielders.
Tested two ways: the packaged DBV ETF (2016–23) and a self-constructed G10 basket ranking six CurrencyShares
ETFs by their own trailing distribution yield (long top-2 / short bottom-2, dollar-neutral). Findings: **(1)
construction validated** — the yield ranking is textbook (AUD/GBP/CAD high, CHF/JPY the funders). **(2) The
premium is real but thin** — +2.4%/yr constructed (Sharpe +0.32), +1.4% DBV. **(3) The steamroller is real** —
negative skew on both (−0.54 / −0.57) and it partly unwinds in risk-off (corr **+0.57** with equity on its
worst days). **(4) But it's the *least* costume of the earned premia:** vs credit, carry's equity beta is lower
(+0.22 vs +0.39), crisis-correlation milder (+0.57 vs +0.86), and Jensen's alpha is ~0 (−0.6% / −0.1%) rather
than deeply negative — carry keeps a genuine independence credit lacked. **Verdict:** of VRP / credit / carry,
FX carry is the closest thing to a real standalone premium — but it's thin, crash-prone, and its alpha is ~0,
not positive: you're paid roughly *fairly* for bearing an equity-correlated tail. The nickels are real; so is
the steamroller. *Next: regime-gate carry to dodge the unwinds, then commodities carry (backwardation / roll).*

**FX #2 — regime-gated carry: can timing dodge the steamroller?** ([`research/block_fx_carry_timed.py`](research/block_fx_carry_timed.py)):
carry's crashes *are* vol spikes, so gating exposure off in risk-off should dodge the unwind. The real test is
whether a gate *fixes the skew and cuts the crisis-correlation*, not just trims the mean. Four lag-safe gates
tested; the result is clean. **The equity-vol gate wins decisively** — crisis-corr **+0.57 → −0.01**, maxDD
−21% → −12%, skew −0.54 → −0.36 (the steamroller removed), while Sharpe *holds* (+0.32 → +0.31) and Jensen
alpha **flips positive (−0.6% → +0.6%)** — the first genuine positive independent alpha in the whole
earned-premium arc, and it came from *dodging the tail, not a fatter premium*. **The wrong gates fail, honestly
reported:** own-vol over-trims (Sharpe → +0.15), the dollar gate *worsens* skew (−1.00) and keeps crisis-corr
+0.39, momentum whipsaws (+0.09). **The lesson — match the gate to the failure mode:** carry fails in equity-vol
spikes, so an equity-vol filter is the right signal and price/dollar trend are not — "match the signal to the
sleeve," now proven at the gate level. **Caveat:** the winning alpha is small (+0.6%) on one decade and
un-costed for turnover — a real improvement, not a validated keeper. **Verdict:** timing turns FX carry from a
fairly-priced, crash-prone premium into a small positive-alpha, tail-*managed* one — the arc's first true (if
thin) edge, and exactly on the program's thesis, the edge is *risk management*, not the premium. *Next and last
asset block: commodities carry (backwardation / roll-yield) — completing Block's four-block cross-asset map.*

### Commodities block — roll yield, and the four-block synthesis

**Commodities #1 — roll yield / backwardation** ([`research/block_commodities_carry.py`](research/block_commodities_carry.py)):
the last asset block. Commodity carry is roll yield — read from front-vs-deferred ETF pairs (USO/USL oil,
UNG/UNL gas). Findings: **(1) the roll tax is the whole game** — WTI front bled +4.0%/yr to the 12-mo deferred,
and natgas front lost −12.1%/yr (an **+11.2%/yr** roll tax) almost purely to contango; the curve state *is* the
return. **(2) Carry-timing dodges the catastrophes** — holding the front only when backwardated turned oil-2020
from −68% to +11% and fixed skew (−0.82 → −0.13); the one direct harvest is shorting persistent contango
(natgas L/S +7.5%), but oil L/S was −1.8% when its curve flipped to backwardation — real but regime-dependent,
with brutal idiosyncratic tails (maxDD −60% to −95%, oil went negative in 2020). **(3) Independence is partial,
and gold is the prize** — broad commodities carry moderate equity beta (+0.32) but hedge inflation (2022 +18%);
**gold** is the standout: Sharpe **+0.70**, near-zero equity beta (**+0.08**), low crisis-corr — the most
independent, most diversifying single asset in the whole study.

### Municipal block — the "good credit"

**Municipal #1 — the muni spread** ([`research/block_muni_premium.py`](research/block_muni_premium.py)): the muni
spread (MUB−IEF, HYD−MUB) tested like credit #1. **Munis are the "good credit"** — about *half* the equity beta
of corporates (IG-muni β +0.11 vs +0.22; HY-muni +0.19 vs +0.39), because they default on politics/rates, not
earnings. But the pre-tax spread is thin (+0.9% / +0.7%) with negative Jensen alpha (−0.6% / −1.8%) and a
March-2020 *liquidity* tail (skew −1.15 / −1.52, crisis-corr +0.61). **The real premium is the tax code:** MUB's
3.5% yield is a 5.8% taxable-equivalent (top bracket) vs IEF's 4.2% — a **+1.6%/yr after-tax pickup** the pre-tax
return can't show. **Verdict:** for a taxable investor munis dominate corporate credit (lower beta + tax pickup),
but the edge is the exemption, not a harvestable spread — neither is a standalone premium.

### Funding block — pennies, then a gap

**Funding #1 — the front-end money-market premium** ([`research/block_funding_premium.py`](research/block_funding_premium.py)):
isolated with floating-rate pairs (FLOT−USFR, MINT−BIL) that strip duration entirely. **A real, independent,
steady carry** (+0.5…0.75%/yr at near-zero equity beta) — but **pure short-liquidity:** the most extreme negative
skew in the whole study (−9.3 to −23.6), where the worst *day* (−6.9%) erases ~a decade of carry and it gaps in a
freeze (Mar-2020, crisis-corr +0.62). **The Sharpe is an illusion** — FLOT−USFR's +0.15 becomes +0.61 once you
exclude March-2020 alone; one month *is* the risk. **Verdict:** fairly-priced liquidity-crisis insurance-selling
— thin pennies for a rare violent gap; it belongs in a book as *sized insurance-selling*, never as "high-Sharpe
carry." The flattering calm-Sharpe is the exact trap the whole arc keeps exposing: the metric flatters, the tail decides.

### The seven-block synthesis — the cross-asset map, complete

All seven catalog categories now tested with one honest toolkit (equity/vol · rates · credit · commodities · FX ·
**municipals** · **funding**). **Standalone "premia" mostly dissolve:** VRP is a crash tail dressed as income;
credit is underpaid equity beta in a wrapper; munis are better credit but the edge is *tax*, not spread; FX &
commodity carry are priced roughly *fairly* with violent tails; funding is insurance-selling whose Sharpe is an
illusion. **The durable edges are not premia** — they are **(1) diversification** (duration's crisis-mirror
positive skew, and gold's near-zero beta actually hedge an equity book) and **(2) risk-management / timing** (the
equity-vol gate that gave FX carry the arc's only positive alpha; curve-timing that dodges the commodity roll-tax).
And one signature recurs in every block — **the tail is the whole story, and headline metrics flatter it.** Block's
founding thesis holds: **the value of a cross-asset book is in combination and risk control, not in any single
harvested premium** — the edge is the portfolio, not the trade.

### The governed cross-asset keeper book (graduated to live)

The payoff: assemble **only** the validated keepers into one book and test whether the *combination* clears the
bar no single block did. Validation ([`research/crossasset_keeper_book.py`](research/crossasset_keeper_book.py)):
equal-weight three sleeves — **gold**, **gated duration** (IEF, trend AND curve-carry), **equity-vol-gated FX
carry** — that are near-uncorrelated (cross-corr +0.17 / −0.05 / −0.22). The book's Sharpe **+0.83 exceeds every
standalone sleeve** (gold +0.72), with low equity correlation (+0.15), a −10% max drawdown, and positive crisis
years (2020 +12.7%, 2022 ~flat). As a cash-funded overlay it lifts an equity core from Sharpe **+0.75 → +0.93**
(1×) and dominates 60/40 (+0.70). Honest caveats: the book is **gold-dominated** (duration & FX carry earn their
place as low/negative-correlation *ballast*, not return), it's a Sharpe/return *enhancer* not a drawdown hedge,
and it leans on one decade. But the thesis is **validated — the edge is the portfolio** — so it graduates to the
governed allocator: [`live/crossasset_allocator.py`](live/crossasset_allocator.py) emits today's target book
(as of the last settled close), and [`live/crossasset_live.jl`](live/crossasset_live.jl) routes it through the
engine's Layer-3 safety gate (preflight, idempotency, reconciliation, HWM, kill switch) — **no LLM in the order
path.** Dry-run PASSES the gate (5 names, gross 1.0x). *Next: open the rates/credit sections of the 120-catalog
variation program (swaptions, CDS index, tranche structures).*

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
