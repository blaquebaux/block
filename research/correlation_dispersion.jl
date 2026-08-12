#!/usr/bin/env julia
# correlation_dispersion.jl — real-data demo of the index/basket analytics (analytics/index_analytics.jl):
# price-movement CORRELATION, IMPLIED correlation, the DIVERSIFICATION ratio, BETA, and BASKET-vs-INDEX — on a
# live tech basket vs its sector ETF (XLK). Surfaces the honest risk finding that matters for every basket/index
# derivative: correlation is REGIME-DEPENDENT — it spikes toward 1 in stress, so the diversification a basket
# deriv relies on EVAPORATES exactly when it's needed. Read-only SIP data; keys from env.
include(joinpath(@__DIR__, "..", "analytics", "index_analytics.jl")); using .IndexAnalytics
using HTTP, JSON3, Statistics, LinearAlgebra, Printf

const NAMES = ["AAPL","MSFT","NVDA","AVGO","ORCL","CRM","CSCO","AMD","ADBE","ACN"]  # top XLK constituents
const ETF = "XLK"

function closes(syms)
    k=get(ENV,"ALPACA_KEY_ID",""); s=get(ENV,"ALPACA_SECRET_KEY","")
    (isempty(k)||isempty(s)) && error("set ALPACA keys")
    out=Dict{String,Dict{String,Float64}}()
    for sym in syms
        url="https://data.alpaca.markets/v2/stocks/bars?symbols=$sym&timeframe=1Day&start=2016-01-01&end=2026-08-01&adjustment=all&feed=sip&limit=10000"
        r=HTTP.get(url; headers=["APCA-API-KEY-ID"=>k,"APCA-API-SECRET-KEY"=>s], readtimeout=40)
        b=JSON3.read(r.body).bars[Symbol(sym)]
        out[sym]=Dict(String(x.t)[1:10]=>Float64(x.c) for x in b)
    end
    out
end

D = closes(vcat(NAMES, ETF))
dates = sort(collect(intersect([Set(keys(v)) for v in values(D)]...)))
R = hcat([ (p=[D[s][d] for d in dates]; p[2:end]./p[1:end-1].-1) for s in NAMES ]...)   # T×N
etf = (p=[D[ETF][d] for d in dates]; p[2:end]./p[1:end-1].-1); dd = dates[2:end]
N = length(NAMES); w = fill(1/N, N)                                    # equal-weight basket (approx)
ann = sqrt(252)

avg_corr(Rw) = (C=cor(Rw); (sum(C)-N)/(N*(N-1)))                       # mean off-diagonal correlation
window(lo,hi) = findall(d-> lo<=d<=hi, dd)

println("="^78, "\nCORRELATION & DISPERSION — $ETF vs its top-$N basket (equal-weight), 2016-2026\n", "="^78)
vols = vec(std(R, dims=1)) .* ann
Σ = cov(R) .* 252
σb = basket_vol(w, Σ); ρ̄ = avg_corr(R)
ic = implied_correlation(σb, w, vols)
betas = [beta(R[:,i], etf) for i in 1:N]
@printf("\n  full sample:  avg pairwise corr %.2f   implied corr (basket) %.2f   diversification ratio %.2f\n",
        ρ̄, ic, diversification_ratio(w, vols, cor(R)))
@printf("  basket vol %.0f%%  vs weighted-avg member vol %.0f%%  (corr eats the gap)\n", 100σb, 100*dot(w,vols))
@printf("  basket beta to %s = %.2f   (member betas %.2f..%.2f)\n", ETF, basket_beta(w, betas), minimum(betas), maximum(betas))

println("\n  CORRELATION IS REGIME-DEPENDENT (the finding that matters for basket/index derivatives):")
for (lbl,lo,hi) in [("calm 2017",         "2017-01-01","2017-12-31"),
                    ("COVID crash 2020",  "2020-02-19","2020-04-30"),
                    ("2022 bear",         "2022-01-01","2022-10-31"),
                    ("calm 2024",         "2024-01-01","2024-12-31")]
    idx = window(lo,hi); isempty(idx) && continue
    @printf("    %-18s avg pairwise corr %.2f   diversification ratio %.2f\n",
            lbl, avg_corr(R[idx,:]), diversification_ratio(w, vec(std(R[idx,:],dims=1)).*ann, cor(R[idx,:])))
end
println("\n  READ: correlation spikes toward 1 in stress (COVID/2022) -> the diversification ratio collapses,")
println("  so a basket/index derivative's diversification is worth LEAST exactly when it's needed most. That")
println("  is the risk a dispersion trade is short and a correlation hedge is long — and why basket-vs-index")
println("  basis, beta, and implied correlation must be watched, not assumed. (Analytics identities: analytics/")
println("  analytics_selftest.jl; this is the live read on the price-movement-correlation consideration.)")
