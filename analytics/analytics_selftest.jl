#!/usr/bin/env julia
# analytics_selftest.jl — identities the index/basket/correlation/beta and corporate-action analytics must
# satisfy. Run: julia analytics_selftest.jl
include(joinpath(@__DIR__, "index_analytics.jl"));   using .IndexAnalytics
include(joinpath(@__DIR__, "corporate_actions.jl")); using .CorporateActions
using Printf, LinearAlgebra

pass = Ref(true)
chk(n, ok, d="") = (pass[] &= ok; @printf("  [%s] %-50s %s\n", ok ? "PASS" : "FAIL", n, d))
println("="^76, "\nBLOCK ANALYTICS — index / correlation / beta / corporate-action identities\n", "="^76, "\n")

# 1) INDEX DIVISOR keeps the level continuous across a 2:1 split
prices = [100.0, 50.0, 200.0]
lvl0 = price_weighted(prices; divisor=3.0)                 # Dow-style, divisor 3
prices_split = [100.0, 50.0, 100.0]                        # last name splits 2:1 (price halves)
new_div = rebalance_divisor(sum(prices_split), lvl0)        # reset divisor to hold the level
lvl1 = price_weighted(prices_split; divisor=new_div)
chk("index divisor: level continuous across a split", abs(lvl1 - lvl0) < 1e-10, @sprintf("%.4f -> %.4f", lvl0, lvl1))

# 2) BASKET variance / diversification / implied correlation
w = [0.5, 0.5]; vols = [0.20, 0.20]
Σ1 = IndexAnalytics.cov_from(vols, [1.0 1.0; 1.0 1.0])     # perfectly correlated
chk("basket vol = member vol when ρ=1", abs(basket_vol(w, Σ1) - 0.20) < 1e-12, @sprintf("%.4f", basket_vol(w,Σ1)))
chk("diversification ratio = 1 when ρ=1", abs(diversification_ratio(w, vols, [1.0 1.0;1.0 1.0]) - 1.0) < 1e-10)
Σ0 = IndexAnalytics.cov_from(vols, [1.0 0.0; 0.0 1.0])     # uncorrelated
dr = diversification_ratio(w, vols, [1.0 0.0;0.0 1.0])
chk("diversification ratio > 1 when ρ=0", dr > 1.0, @sprintf("DR=%.3f (=√2)", dr))
# implied correlation inverts: feed the ρ=0.3 index vol, recover ~0.3
corr = [1.0 0.3; 0.3 1.0]; idxvol = basket_vol(w, IndexAnalytics.cov_from(vols, corr))
ic = implied_correlation(idxvol, w, vols)
chk("implied correlation inverts basket vol", abs(ic - 0.3) < 1e-9, @sprintf("recovered ρ=%.4f", ic))
chk("implied ρ = 1 when index vol = weighted-avg vol", abs(implied_correlation(0.20, w, vols) - 1.0) < 1e-9)

# 3) BETA & basket beta
using Random, Statistics; Random.seed!(1)
b = randn(500); a = 1.5 .* b .+ 0.3 .* randn(500)         # β≈1.5 by construction
chk("beta recovers the loading", abs(beta(a, b) - 1.5) < 0.1, @sprintf("β=%.2f", beta(a, b)))
chk("basket beta is weighted sum", abs(basket_beta([0.6,0.4], [1.2, 0.8]) - 1.04) < 1e-12)

# 4) CORPORATE ACTIONS
# discrete dividend lowers the forward
F0 = forward_with_dividends(; spot=100.0, r=0.05, T=1.0)
Fd = forward_with_dividends(; spot=100.0, r=0.05, T=1.0, divs=[2.0], div_times=[0.5])
chk("dividend lowers the forward", Fd < F0, @sprintf("F=%.3f -> %.3f", F0, Fd))
# put-call parity WITH dividends holds
gap = parity_gap_with_dividends(; S=100.0, K=105.0, T=1.0, r=0.05, σ=0.25, divs=[1.5,1.5], div_times=[0.25,0.75])
chk("put-call parity holds with dividends", abs(gap) < 1e-9, @sprintf("residual=%.2e", gap))
# split adjustment preserves moneyness & notional
sa = split_adjust(; strike=200.0, contracts=10.0, ratio=2.0)
chk("2:1 split: strike halves, contracts double", sa.strike==100.0 && sa.contracts==20.0, @sprintf("K=%.0f n=%.0f", sa.strike, sa.contracts))
chk("special dividend reduces the strike", special_dividend_adjust(; strike=100.0, special_div=5.0) == 95.0)

println("\n", pass[] ? "ALL ANALYTICS IDENTITIES HOLD ✓" : "SOME CHECKS FAILED ✗")
exit(pass[] ? 0 : 1)
