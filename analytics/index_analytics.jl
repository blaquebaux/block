# ============================================================================
# index_analytics.jl — the analytics that surround INDEX & BASKET derivatives (rounds out Block):
#   * index calculation methods (price- / cap- / equal-weighted) + the DIVISOR mechanism
#   * index rebalancing / reconstitution and its continuity (the divisor keeps the level unbroken)
#   * price-movement CORRELATION → basket variance, the diversification ratio, IMPLIED correlation
#   * BETA & sensitivity (single-name and basket)
#   * BASKET vs INDEX: the replication error / basis that index-arbitrage trades
# Dependency-free. See analytics_selftest.jl for the identities each function must satisfy.
# ============================================================================
module IndexAnalytics
export price_weighted, cap_weighted, equal_weighted_level, rebalance_divisor,
       basket_return, basket_variance, basket_vol, diversification_ratio, implied_correlation,
       beta, basket_beta, index_basket_basis

using Statistics, LinearAlgebra

# ---------- index calculation methods ----------
"Price-weighted index (Dow-style): Σ Pᵢ / divisor."
price_weighted(prices; divisor=1.0) = sum(prices) / divisor
"Cap-weighted index (S&P-style): Σ Pᵢ·sharesᵢ·floatᵢ / divisor."
cap_weighted(prices, shares; floats=ones(length(prices)), divisor=1.0) =
    sum(prices .* shares .* floats) / divisor
"Equal-weighted level: base · mean(Pᵢ/Pᵢ⁰). (In practice maintained by periodic rebalancing back to 1/N.)"
equal_weighted_level(prices, base_prices; base_level=100.0) = base_level * mean(prices ./ base_prices)

"""
    rebalance_divisor(new_market_value, index_level_before) -> Float64

The continuity-preserving divisor. On ANY composition change — a split, an add/delete, a share-count update —
the divisor is reset so the index level is UNBROKEN: level_after = new_market_value / new_divisor = level_before.
This is why a 2:1 split or a name swap doesn't jump the index — and why a derivative on the index is insulated
from mechanical rebalancing (its reference level is continuous), while a REPLICATING BASKET must actually trade.
"""
rebalance_divisor(new_market_value, index_level_before) = new_market_value / index_level_before

# ---------- correlation → basket risk ----------
basket_return(weights, returns) = dot(weights, returns)
"Basket variance wᵀΣw from a covariance matrix (or build Σ from vols+corr)."
basket_variance(weights, Σ) = dot(weights, Σ * weights)
basket_vol(weights, Σ) = sqrt(max(basket_variance(weights, Σ), 0.0))
cov_from(vols, corr) = Diagonal(vols) * corr * Diagonal(vols)

"""
    diversification_ratio(weights, vols, corr) -> Float64  (≥ 1)

(Σ wᵢσᵢ) / σ_basket. =1 when constituents are perfectly correlated; grows as correlation falls. The single
number that says how much a basket/index derivative diversifies vs its members.
"""
function diversification_ratio(weights, vols, corr)
    Σ = cov_from(vols, corr)
    wavg = dot(abs.(weights), vols)
    σb = basket_vol(weights, Σ)
    σb > 0 ? wavg/σb : NaN
end

"""
    implied_correlation(index_vol, weights, vols) -> Float64

The single AVERAGE correlation consistent with an index/basket vol and its constituent vols:
    σ_idx² = Σ wᵢ²σᵢ² + ρ · Σ_{i≠j} wᵢwⱼσᵢσⱼ   ⇒   ρ = (σ_idx² − Σ wᵢ²σᵢ²) / (Σ_{i≠j} wᵢwⱼσᵢσⱼ).
This is the number a dispersion / correlation trade is actually long or short (index vol vs the sum of the
single-name vols). ρ ∈ [~0,1] in practice; ρ→1 as the index vol approaches the weighted-average vol.
"""
function implied_correlation(index_vol, weights, vols)
    v = weights .* vols
    diag_term = sum(v .^ 2)                       # Σ wᵢ²σᵢ²
    cross = sum(v * v') - diag_term               # Σ_{i≠j} wᵢwⱼσᵢσⱼ
    cross <= 0 ? NaN : (index_vol^2 - diag_term) / cross
end

# ---------- beta & sensitivity ----------
"Beta of an asset to a benchmark: cov/var."
function beta(asset_returns, bench_returns)
    m = isfinite.(asset_returns) .& isfinite.(bench_returns)
    var(bench_returns[m]) > 0 ? cov(asset_returns[m], bench_returns[m]) / var(bench_returns[m]) : 0.0
end
"Basket beta = weighted sum of member betas (linear in beta)."
basket_beta(weights, betas) = dot(weights, betas)

# ---------- basket vs index: the replication basis ----------
"""
    index_basket_basis(index_level, constituent_prices, weights) -> Float64

The mispricing an index-arbitrage trade captures: index level minus the value of the replicating weighted
basket (both normalized to comparable units). Nonzero basis (net of costs, dividends, and the rebalancing
drift) is the arb. Basket vs index derivatives differ precisely here — a basket deriv references fixed
weights; an index deriv references a maintained index whose divisor/rebalancing makes this basis move.
"""
index_basket_basis(index_level, constituent_prices, weights) =
    index_level - dot(weights, constituent_prices)

end # module
