#!/usr/bin/env julia
# =============================================================================
# block/test/runtests.jl — gated test suite for the reference pricers
# (PRE-BL-02). Converts pricing_selftest.jl's `chk()` identities into @testsets
# and adds absolute reference values computed independently from the closed
# forms (second-implementation check). Exits non-zero on failure so CI gates on
# it. A QuantLib/Strata cross-check belongs in the grader image (BK-DD-01) and is
# tracked separately; these closed-form references make the gate real today.
# =============================================================================
using Test
include(joinpath(@__DIR__, "..", "pricing", "block_pricing.jl"))
using .BlockPricing

@testset "BLOCK reference pricers" begin

    @testset "Black-Scholes — identities" begin
        S, K, T, r, σ, q = 100.0, 105.0, 0.75, 0.045, 0.22, 0.015
        c = bs_option(; S, K, T, r, σ, q, kind=:call).price
        p = bs_option(; S, K, T, r, σ, q, kind=:put).price
        parity = S*exp(-q*T) - K*exp(-r*T)
        @test abs((c - p) - parity) < 1e-8               # put-call parity
        g = bs_option(; S, K, T, r, σ, q, kind=:call)
        @test g.gamma > 0 && g.vega > 0 && 0 < g.delta < 1
        # deep ITM call ≈ discounted forward intrinsic; deep OTM ≈ 0
        @test bs_option(; S=200.0, K, T, r, σ, q, kind=:call).price > 90
        @test bs_option(; S=10.0,  K, T, r, σ, q, kind=:call).price < 1e-3
    end

    @testset "Black-Scholes — reference values (ATM, r=q=0, σ=0.2, T=1)" begin
        # Closed form: d1=0.1, d2=-0.1; price=100(2Φ(0.1)-1), Φ(0.1)=0.5398278.
        o = bs_option(; S=100.0, K=100.0, T=1.0, r=0.0, σ=0.2, q=0.0, kind=:call)
        @test isapprox(o.price, 7.965567, atol=1e-4)
        @test isapprox(o.delta, 0.539828, atol=1e-5)     # Φ(0.1)
        @test isapprox(o.vega,  39.695255, atol=1e-3)    # 100·φ(0.1)
        @test isapprox(o.gamma, 0.019847, atol=1e-5)     # φ(0.1)/(100·0.2)
    end

    @testset "Interest-rate swap — par and monotonicity" begin
        times = collect(0.5:0.5:5.0)
        dfs   = exp.(-0.04 .* times)                      # flat 4% continuous
        Kstar = par_swap_rate(; times, discount_factors=dfs)
        @test abs(irs_value(; notional=1e7, fixed_rate=Kstar, times,
                              discount_factors=dfs)) < 1e-6          # par ⇒ zero value
        @test 0.039 < Kstar < 0.041                       # ≈ 4% on a flat 4% curve
        @test irs_value(; notional=1e7, fixed_rate=Kstar+0.01, times,
                          discount_factors=dfs) < 0        # payer loses above par
        @test irs_value(; notional=1e7, fixed_rate=Kstar-0.01, times,
                          discount_factors=dfs) > 0        # payer gains below par
    end

    @testset "FX forward — covered interest parity" begin
        F = fx_forward_rate(; spot=1.10, r_dom=0.045, r_for=0.028, T=1.0)
        @test isapprox(F, 1.10*exp((0.045 - 0.028)*1.0), atol=1e-10)
        @test isapprox(F, 1.118859, atol=1e-5)            # reference value
        vf = fx_forward_value(; spot=1.10, r_dom=0.045, r_for=0.028, T=1.0,
                               contracted_fwd=F, notional=1e6, side=:long)
        @test abs(vf) < 1e-6                              # zero value at the forward
    end

    @testset "CDS — par spread and credit triangle" begin
        ct = collect(0.25:0.25:5.0); cdf = exp.(-0.03 .* ct); h, R = 0.02, 0.4
        sstar = par_cds_spread(; times=ct, discount_factors=cdf, hazard=h, recovery=R)
        @test abs(cds_value(; notional=1e7, spread=sstar, times=ct,
                             discount_factors=cdf, hazard=h, recovery=R)) < 1e-6
        @test isapprox(sstar, h*(1 - R), atol=5e-4)       # triangle: s ≈ h·(1−R) = 120bp
        vup = cds_value(; notional=1e7, spread=sstar, times=ct, discount_factors=cdf,
                         hazard=0.04, recovery=R, side=:buyer)
        @test vup > 0                                     # protection buyer gains as hazard rises
    end

end
