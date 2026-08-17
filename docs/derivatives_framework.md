# Block — Derivatives Analytical Framework

The analytical layer that surrounds the [catalog](../catalog/): the cross-cutting considerations every
derivative in Block is subject to, with the math, the code that computes it, and the identity that proves the
code. This is what rounds Block out from a *list of instruments* into a *system for reasoning about them*.

Everything here is dependency-free Julia with a self-test. Nothing is asserted that isn't verified:
[`pricing/pricing_selftest.jl`](../pricing/pricing_selftest.jl) and
[`analytics/analytics_selftest.jl`](../analytics/analytics_selftest.jl) — **all identities hold**.

---

## 1. Derivative pricing → [`pricing/block_pricing.jl`](../pricing/block_pricing.jl)

One reference pricer per major class, keyed to the catalog `id`, each proven against a textbook identity:

| Block | Function | Identity (self-test) |
|---|---|---|
| `irs_vanilla` | `irs_value`, `par_swap_rate` | par swap has **zero value** |
| `fx_outright_forward` | `fx_forward_rate`, `fx_forward_value` | **covered interest parity** |
| `fx_vanilla` / equity | `bs_option` (+ Δ Γ ν Θ) | **put-call parity** (exact) |
| `cds_single` | `cds_value`, `par_cds_spread` | **credit triangle** par ≈ h·(1−R) |

The `status` ladder (`reference → spec → implemented → validated`) tracks how far each of the 120 blocks has come; a block reaches `implemented` only once its pricer passes its identity.

## 2. Price-movement correlation → [`analytics/index_analytics.jl`](../analytics/index_analytics.jl)

Correlation is the hinge of every basket/index derivative. Basket variance is `wᵀΣw`; the **diversification
ratio** `(Σwᵢσᵢ)/σ_basket ≥ 1` says how much a basket diversifies its members; **implied correlation** inverts
the basket vol to the single average ρ a dispersion trade is long/short:

```
σ_idx² = Σ wᵢ²σᵢ²  +  ρ · Σ_{i≠j} wᵢwⱼσᵢσⱼ     ⇒     ρ = (σ_idx² − Σ wᵢ²σᵢ²) / Σ_{i≠j} wᵢwⱼσᵢσⱼ
```

**The finding that governs risk** ([`research/correlation_dispersion.jl`](../research/correlation_dispersion.jl),
XLK vs its top-10): ρ is **regime-dependent** — calm ≈ 0.30, COVID ≈ 0.83, 2022 ≈ 0.69. Diversification
collapses (ratio 1.60 → 1.09) exactly in stress. A basket/index derivative's diversification is worth *least*
when it's needed most — the risk a dispersion trade is short and a correlation hedge is long.

## 3. Index calculation method → `price_weighted` / `cap_weighted` / `equal_weighted_level`

- **Price-weighted** (Dow): `Σ Pᵢ / divisor`. High-priced names dominate.
- **Cap-weighted** (S&P): `Σ Pᵢ·sharesᵢ·floatᵢ / divisor`. Float-adjusted.
- **Equal-weighted**: `base · mean(Pᵢ/Pᵢ⁰)`, maintained by periodic rebalancing back to 1/N.

The choice changes the beta, the concentration, and the rebalance cadence — and therefore what a derivative on
the index actually references.

## 4. Index rebalancing & derivative impact → `rebalance_divisor`

The **divisor** is reset on every composition change (split, add/delete, share update) so the level is
UNBROKEN: `level_after = new_market_value / new_divisor = level_before` (self-test: continuous across a 2:1
split). Consequence for derivatives: a derivative on the *index* is insulated from mechanical rebalancing (its
reference level is continuous), while a **replicating basket must actually trade** the reconstitution — which
is the source of the index-rebalance / reconstitution effect (and of index-arbitrage flow around roll dates).

## 5. Dividends & corporate actions → [`analytics/corporate_actions.jl`](../analytics/corporate_actions.jl)

- **Discrete dividends** lower the forward: `F = (S − PV(divs))·e^{rT}`; options priced on `S′ = S − PV(divs)`
  (escrowed-dividend model). Put-call parity holds *with* dividends (self-test residual ~1e-15).
- **Ordinary splits** (n:m): strike ÷ ratio, contract size × ratio — moneyness and notional unchanged.
- **Special/extraordinary dividends**: OCC-style strike reduction by the special amount. Ordinary dividends are
  *not* contract-adjusted (already in the forward); only special ones trigger an adjustment.

## 6. Beta & sensitivity → `beta`, `basket_beta`, `bs_option` greeks

Single-name `beta = cov/var`; `basket_beta = Σ wᵢβᵢ` (linear). Option sensitivities Δ Γ ν Θ come from
`bs_option`. Together they let a bespoke book know its net directional (beta), convexity (gamma), and vol
(vega) exposure — the guardrail readouts, not a signal.

## 7. Basket vs index derivatives → `index_basket_basis`, hedging & arbitrage

A **basket** derivative references fixed weights; an **index** derivative references a *maintained* index whose
divisor and rebalancing make the two drift apart. `index_basket_basis = index_level − wᵀ·prices` is the
mispricing **index arbitrage** captures (net of costs, dividends, and rebalancing drift).

**Hedging / arbitrage** is where the blocks stop being vocabulary and start being research. The catalog's
`combinations` field names the plays; each is tested before it's claimed:

| Play | Kind | Status |
|---|---|---|
| collar (long put / short call) | risk guardrail | ✅ tested — [`research/collar_overlay.jl`](../research/collar_overlay.jl): SPY Sharpe 1.01→1.39, tail −18% vs −24%, at the cost of upside |
| dispersion (index vol vs single-name vol) | correlation | framework in place (implied correlation); trade TBD |
| index arbitrage (index vs basket) | basis | `index_basket_basis` in place; needs holdings data |
| CDS-vs-bond, swap-spread | basis | next basis plays to test |

---

## The through-line

Every piece above is a **guardrail readout, not a signal**: correlation regime, divisor continuity, dividend
drag, beta/greeks, the index-basket basis. None of them *is* alpha. They tell a bespoke book what it actually
owns and where it is exposed — the comfort and control that let someone build better returns in a dynamic
market. That is the Blaque Baux thesis, made computable for derivatives, and held to the same
verify-before-claim discipline as the rest of the platform.
