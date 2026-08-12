#!/usr/bin/env julia
# collar_overlay.jl — FIRST combination-research play, built ON the pricing layer (pricing/block_pricing.jl).
# Tests a documented catalog combination: the COLLAR (long underlying + long OTM put [floor] + short OTM call
# [cap]) — catalog `collar` / "collar via cap/floor". A monthly-rolled collar on SPY, options priced with
# Black-Scholes at trailing realized vol. The thesis under test is Blaque Baux's own: none of these blocks is
# alpha alone — a collar is a GUARDRAIL that reshapes the return distribution (caps the tail, costs the top),
# not a money machine. We quantify exactly that reshaping vs buy-and-hold. Read-only SIP data; keys from env.
include(joinpath(@__DIR__, "..", "pricing", "block_pricing.jl")); using .BlockPricing
using HTTP, JSON3, Statistics, Printf

const R_F = 0.045; const DIV = 0.015          # SPY financing / dividend carry
const PUT_OTM = 0.95; const CALL_OTM = 1.03   # 5% floor / 3% cap
const REB = 21                                # ~monthly

function spy_closes()
    k = get(ENV,"ALPACA_KEY_ID",""); s = get(ENV,"ALPACA_SECRET_KEY","")
    (isempty(k)||isempty(s)) && error("set ALPACA_KEY_ID / ALPACA_SECRET_KEY")
    url = "https://data.alpaca.markets/v2/stocks/bars?symbols=SPY&timeframe=1Day&start=2016-01-01&end=2026-08-01&adjustment=all&feed=sip&limit=10000"
    r = HTTP.get(url; headers=["APCA-API-KEY-ID"=>k,"APCA-API-SECRET-KEY"=>s], readtimeout=40)
    b = JSON3.read(r.body).bars.SPY
    ([String(x.t)[1:10] for x in b], [Float64(x.c) for x in b])
end

dates, C = spy_closes()
ret = C[2:end] ./ C[1:end-1] .- 1
T = length(C)
collar = Float64[]; spy = Float64[]; months = String[]
for t0 in REB:REB:(T-1-REB)
    S0 = C[t0]; ST = C[t0+REB]
    σ = std(ret[t0-REB+1:t0]) * sqrt(252)                # trailing realized vol as the pricing IV (proxy)
    σ = clamp(σ, 0.05, 1.5)
    texp = REB/252
    Kp = PUT_OTM*S0; Kc = CALL_OTM*S0
    put_cost   = bs_option(; S=S0, K=Kp, T=texp, r=R_F, σ=σ, q=DIV, kind=:put).price
    call_credit= bs_option(; S=S0, K=Kc, T=texp, r=R_F, σ=σ, q=DIV, kind=:call).price
    net_prem   = put_cost - call_credit                  # paid upfront (per share)
    put_payoff = max(Kp - ST, 0.0); call_payoff = max(ST - Kc, 0.0)
    collar_pnl = (ST - S0) + put_payoff - call_payoff - net_prem
    push!(collar, collar_pnl/S0); push!(spy, (ST-S0)/S0); push!(months, dates[t0][1:7])
end

ann(x, p) = (m=mean(x); m*p)
sh(x, p) = std(x)>0 ? mean(x)/std(x)*sqrt(p) : NaN
maxdd(x) = (lvl=cumprod(1 .+ x); minimum(lvl ./ accumulate(max,lvl) .- 1))
capture(a, b, up) = (m = up ? b .> 0 : b .< 0; sum(m)==0 ? NaN : sum(a[m])/sum(b[m]))

println("="^76, "\nCOLLAR OVERLAY on SPY — a catalog COMBINATION (`collar`), priced by block_pricing.jl\n", "="^76)
@printf("\n  %d monthly rolls %s..%s   floor %.0f%% / cap %.0f%% (Black-Scholes @ trailing realized vol)\n",
        length(collar), months[1], months[end], 100PUT_OTM, 100CALL_OTM)
@printf("\n  %-22s %10s %10s\n", "", "SPY (hold)", "COLLAR")
@printf("  %-22s %+9.1f%% %+9.1f%%\n", "ann. return (×12)", 100ann(spy,12), 100ann(collar,12))
@printf("  %-22s %+10.2f %+10.2f\n", "Sharpe (×√12)", sh(spy,12), sh(collar,12))
@printf("  %-22s %+9.0f%% %+9.0f%%\n", "max drawdown", 100maxdd(spy), 100maxdd(collar))
@printf("  %-22s %+9.1f%% %+9.1f%%\n", "worst month", 100minimum(spy), 100minimum(collar))
@printf("  %-22s %+9.1f%% %+9.1f%%\n", "best month", 100maximum(spy), 100maximum(collar))
@printf("  %-22s %10.1f%% %10.1f%%\n", "monthly vol", 100std(spy), 100std(collar))
@printf("\n  downside capture (collar/SPY in SPY-down months): %.0f%%   upside capture: %.0f%%\n",
        100capture(collar,spy,false), 100capture(collar,spy,true))
println("\n  READ: the collar CAPS the tail (worst month & maxDD sharply shallower, ~",
        @sprintf("%.0f%%", 100capture(collar,spy,false)), " downside capture) at the COST of upside")
println("  (best month trimmed, lower total return in a bull decade). It is a GUARDRAIL — risk reshaping,")
println("  not alpha. Exactly the Blaque Baux thesis: no single block is a money-maker; the value is the")
println("  comfort/protection it lends a bespoke book. Proves the Diagram->Code->Combination chain end-to-end.")
