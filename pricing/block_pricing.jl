# ============================================================================
# block_pricing.jl — reference pricing/payoff layer for the Block derivatives catalog.
#
# One clean, dependency-free implementation per major asset class, keyed to the catalog `id` (catalog/
# derivatives_catalog.json). This is the "Code" half of the deck's "Diagram / Code" model, proven end-to-end
# on four representative blocks. NOT a production quant library — reference pricers with the textbook sanity
# identities they must satisfy (see pricing_selftest.jl):
#   irs_vanilla   -> irs_value / par_swap_rate        (par swap has zero value)
#   fx_outright_forward -> fx_forward_rate / fx_forward_value  (covered interest parity)
#   fx_vanilla / eqd option -> bs_option (+ greeks)    (put-call parity)
#   cds_single    -> cds_value / par_cds_spread        (credit triangle: par ≈ hazard·(1-recovery))
# Self-contained (own normal CDF/PDF) so it runs with no packages. Times in years; rates continuously compounded.
# ============================================================================
module BlockPricing
export bs_option, irs_value, par_swap_rate, fx_forward_rate, fx_forward_value,
       cds_value, par_cds_spread, norm_cdf

# --- normal CDF/PDF (Abramowitz-Stegun 7.1.26, ~1e-7) — no deps ---
norm_pdf(x) = exp(-x^2/2)/sqrt(2π)
function norm_cdf(x)
    z = x/sqrt(2); t = 1/(1 + 0.3275911*abs(z))
    y = 1 - (((((1.061405429t - 1.453152027)t) + 1.421413741)t - 0.284496736)t + 0.254829592)t*exp(-z^2)
    0.5*(1 + sign(z)*y)
end

# --- fx_vanilla / equity option — Black-Scholes-Merton with greeks ---
"""
    bs_option(; S, K, T, r, σ, q=0.0, kind=:call) -> (; price, delta, gamma, vega, theta, d1, d2)

Black-Scholes-Merton price + greeks. `q` = dividend/foreign-rate carry. Catalog: `fx_vanilla`, equity options.
"""
function bs_option(; S, K, T, r, σ, q=0.0, kind::Symbol=:call)
    if T <= 0 || σ <= 0
        intrinsic = kind === :call ? max(S-K, 0.0) : max(K-S, 0.0)
        return (; price=intrinsic, delta=NaN, gamma=NaN, vega=0.0, theta=0.0, d1=NaN, d2=NaN)
    end
    sT = σ*sqrt(T)
    d1 = (log(S/K) + (r - q + σ^2/2)*T)/sT; d2 = d1 - sT
    if kind === :call
        price = S*exp(-q*T)*norm_cdf(d1) - K*exp(-r*T)*norm_cdf(d2)
        delta = exp(-q*T)*norm_cdf(d1)
        theta = (-S*exp(-q*T)*norm_pdf(d1)*σ/(2sqrt(T)) - r*K*exp(-r*T)*norm_cdf(d2) + q*S*exp(-q*T)*norm_cdf(d1))
    else
        price = K*exp(-r*T)*norm_cdf(-d2) - S*exp(-q*T)*norm_cdf(-d1)
        delta = -exp(-q*T)*norm_cdf(-d1)
        theta = (-S*exp(-q*T)*norm_pdf(d1)*σ/(2sqrt(T)) + r*K*exp(-r*T)*norm_cdf(-d2) - q*S*exp(-q*T)*norm_cdf(-d1))
    end
    gamma = exp(-q*T)*norm_pdf(d1)/(S*sT)
    vega  = S*exp(-q*T)*norm_pdf(d1)*sqrt(T)          # per 1.00 (100%) vol
    (; price, delta, gamma, vega, theta, d1, d2)
end

# --- irs_vanilla — interest-rate swap from a discount curve ---
"""
    irs_value(; notional, fixed_rate, times, discount_factors, side=:payer) -> Float64

Value of a vanilla IRS. `times` = cumulative payment times (yrs, t₀=0 implied), `discount_factors` = DF at each.
Float leg valued from DFs (DF₀=1). Catalog: `irs_vanilla`. par_swap_rate gives the fixed rate that zeroes it.
"""
function irs_value(; notional, fixed_rate, times, discount_factors, side::Symbol=:payer)
    accr = diff(vcat(0.0, collect(times)))
    annuity = sum(accr .* discount_factors)                 # Σ τᵢ·DFᵢ
    float_pv = 1.0 - discount_factors[end]                  # DF₀ − DFₙ, DF₀=1
    val = notional * (float_pv - fixed_rate*annuity)        # to the fixed-rate PAYER
    side === :payer ? val : -val
end
par_swap_rate(; times, discount_factors) =
    (1.0 - discount_factors[end]) / sum(diff(vcat(0.0, collect(times))) .* discount_factors)

# --- fx_outright_forward — covered interest parity ---
"""
    fx_forward_rate(; spot, r_dom, r_for, T) -> Float64      # F = S·e^{(r_dom−r_for)T}
    fx_forward_value(; spot, r_dom, r_for, T, contracted_fwd, notional, side=:long) -> Float64

Catalog: `fx_outright_forward`. Value is the PV of (F − contracted) × notional.
"""
fx_forward_rate(; spot, r_dom, r_for, T) = spot * exp((r_dom - r_for)*T)
function fx_forward_value(; spot, r_dom, r_for, T, contracted_fwd, notional, side::Symbol=:long)
    F = fx_forward_rate(; spot, r_dom, r_for, T)
    v = notional * (F - contracted_fwd) * exp(-r_dom*T)
    side === :long ? v : -v
end

# --- cds_single — reduced-form CDS with a constant hazard rate ---
"""
    cds_value(; notional, spread, times, discount_factors, hazard, recovery=0.4, side=:buyer) -> Float64
    par_cds_spread(; times, discount_factors, hazard, recovery=0.4) -> Float64

Reduced-form CDS: survival Q(t)=e^{−h·t}. Value to the protection BUYER = protection leg − premium leg.
Catalog: `cds_single`. Credit triangle: par spread ≈ hazard·(1−recovery) for small h.
"""
function cds_value(; notional, spread, times, discount_factors, hazard, recovery=0.4, side::Symbol=:buyer)
    tv = collect(times); accr = diff(vcat(0.0, tv))
    Q  = exp.(-hazard .* tv); Q0 = vcat(1.0, Q[1:end-1])
    premium_pv    = spread    * sum(accr .* discount_factors .* Q)            # premium leg
    protection_pv = (1-recovery) * sum(discount_factors .* (Q0 .- Q))         # protection leg
    v = notional * (protection_pv - premium_pv)
    side === :buyer ? v : -v
end
function par_cds_spread(; times, discount_factors, hazard, recovery=0.4)
    tv = collect(times); accr = diff(vcat(0.0, tv))
    Q  = exp.(-hazard .* tv); Q0 = vcat(1.0, Q[1:end-1])
    (1-recovery)*sum(discount_factors .* (Q0 .- Q)) / sum(accr .* discount_factors .* Q)
end

end # module
