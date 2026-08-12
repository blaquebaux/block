# ============================================================================
# corporate_actions.jl — DIVIDENDS & CORPORATE ACTIONS in derivative pricing (rounds out Block).
#   * discrete dividends -> forward price and option value (escrowed-dividend model)
#   * ordinary splits -> strike / contract-size adjustment (moneyness preserved)
#   * special (non-ordinary) dividends -> OCC-style strike reduction
#   * put-call parity WITH dividends (the identity the self-test checks)
# Builds on pricing/block_pricing.jl (bs_option). Dependency-free otherwise.
# ============================================================================
module CorporateActions
export pv_dividends, forward_with_dividends, option_with_dividends,
       split_adjust, special_dividend_adjust, parity_gap_with_dividends

const _HERE = @__DIR__
include(joinpath(_HERE, "..", "pricing", "block_pricing.jl"))
using .BlockPricing

"PV of a stream of discrete cash dividends: Σ dᵢ·e^{−r·tᵢ}."
pv_dividends(divs, times, r) = sum(d * exp(-r*t) for (d, t) in zip(divs, times); init=0.0)

"""
    forward_with_dividends(; spot, r, T, divs=Float64[], div_times=Float64[]) -> Float64

Forward on a dividend-paying underlying: F = (S − PV(divs))·e^{rT}. Discrete dividends LOWER the forward —
the holder of the forward forgoes the dividends the spot holder receives. (Equity forward / TRS, EQD blocks.)
"""
forward_with_dividends(; spot, r, T, divs=Float64[], div_times=Float64[]) =
    (spot - pv_dividends(divs, div_times, r)) * exp(r*T)

"""
    option_with_dividends(; S, K, T, r, σ, divs, div_times, kind=:call) -> NamedTuple

Escrowed-dividend model: price a European option on the dividend-adjusted spot S′ = S − PV(divs). This is the
standard adjustment that keeps option pricing consistent with the lowered forward. (Vanilla / structured EQD.)
"""
function option_with_dividends(; S, K, T, r, σ, divs=Float64[], div_times=Float64[], kind::Symbol=:call)
    Sadj = S - pv_dividends(divs, div_times, r)
    bs_option(; S=Sadj, K=K, T=T, r=r, σ=σ, q=0.0, kind=kind)
end

"""
    split_adjust(; strike, contracts, ratio) -> (; strike, contracts)

Ordinary split n:m (ratio = n/m; a 2:1 split → ratio 2). Strike ÷ ratio, contract size × ratio, so the
position's moneyness and total notional are unchanged. (Applies to every listed-option block.)
"""
split_adjust(; strike, contracts, ratio) = (strike = strike/ratio, contracts = contracts*ratio)

"""
    special_dividend_adjust(; strike, special_div) -> Float64

Non-ordinary (special) cash dividend: OCC reduces the strike by the special-dividend amount so option holders
are not disadvantaged by the one-off drop in the underlying. Ordinary dividends are NOT adjusted (they are
already priced into the forward); only special/extraordinary ones trigger a contract adjustment.
"""
special_dividend_adjust(; strike, special_div) = strike - special_div

"""
    parity_gap_with_dividends(; S, K, T, r, σ, divs, div_times) -> Float64

Put-call parity residual with dividends: (C − P) − [(S − PV(divs)) − K·e^{−rT}]. Must be ~0 — the identity the
dividend-aware pricer has to satisfy.
"""
function parity_gap_with_dividends(; S, K, T, r, σ, divs=Float64[], div_times=Float64[])
    c = option_with_dividends(; S,K,T,r,σ,divs,div_times, kind=:call).price
    p = option_with_dividends(; S,K,T,r,σ,divs,div_times, kind=:put).price
    (c - p) - ((S - pv_dividends(divs, div_times, r)) - K*exp(-r*T))
end

end # module
