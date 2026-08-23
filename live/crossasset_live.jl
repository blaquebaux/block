#!/usr/bin/env julia
# ============================================================================
# crossasset_live.jl — BLAQUE BAUX BLOCK governed CROSS-ASSET keeper-book driver (validated, live).
#
# The graduation of the seven-block cross-asset study: the validated KEEPER BOOK (gold + gated duration + equity-
# vol-gated FX carry), routed through the Layer-3 safety gate. crossasset_allocator.py emits today's target book
# to crossasset_target.txt; THIS driver reads it, converts to shares at live prices, and routes it through the
# engine's governed order path (preflight, idempotency, reconciliation, HWM, kill switch) — exactly like every
# other sleeve. No LLM in the order path; both the allocator and the rail are reproducible code. The edge is the
# PORTFOLIO, not the trade (seven-block synthesis): three individually-modest keepers, combined and risk-gated.
#
# Run the allocator first (emits the target), then this driver:
#   python3 live/crossasset_allocator.py && julia --project=engine live/crossasset_live.jl
# Dry-run by default via the wrapper. Real money requires BB_LIVE_CONFIRM. Kill switch: ~/.config/blaquebaux/HALT.
# ============================================================================
using Dates, Printf, Statistics
const REPO   = normpath(joinpath(@__DIR__, ".."))
const ENGINE = joinpath(REPO, "engine")
include(joinpath(ENGINE, "src/module_7_execution/module_7_execution.jl"))
include(joinpath(ENGINE, "src/module_10_feedback/module_10_feedback.jl"))
include(joinpath(ENGINE, "src/module_13_portfolio/module_13_portfolio.jl"))
include(joinpath(ENGINE, "src/module_1_data/equity_panel.jl"))
include(joinpath(ENGINE, "src/module_1_data/alpaca_panel.jl"))
include(joinpath(ENGINE, "src/module_8_governance/safety_gate.jl"))
using .ExecutionLayer, .FeedbackLayer, .PortfolioOptModule, .EquityPanel, .AlpacaPanel, .SafetyGate
include(joinpath(ENGINE, "scripts/live_execution.jl"))

const LIVE_SENTINEL = "I_UNDERSTAND_THIS_IS_REAL_MONEY"
_readf(p) = isfile(p) ? (v = tryparse(Float64, strip(read(p, String))); v === nothing ? NaN : v) : NaN
_writef(p, x) = (mkpath(dirname(p)); write(p, string(x)))

"Read the allocator's target book (symbol weight per line; # header carries asof/mode/regime/gross)."
function read_target(path)
    isfile(path) || error("no target at $path — run crossasset_allocator.py first")
    w = Dict{String,Float64}(); meta = Dict{String,String}()
    for ln in eachline(path)
        s = strip(ln); isempty(s) && continue
        if startswith(s, "#")
            for kv in split(s); occursin("=", kv) && (p = split(kv, "="); meta[p[1]] = p[2]); end
            continue
        end
        parts = split(s); length(parts) == 2 && (v = tryparse(Float64, parts[2]); v !== nothing && (w[parts[1]] = v))
    end
    asof = get(meta, "asof", ""); (w, meta, tryparse(Date, asof))
end

function main(; capital = nothing, pool = "us",
              limits::SafetyLimits = SafetyLimits(; max_gross_leverage = 2.0),
              target_path = get(ENV, "BB_ALLOC_TARGET", joinpath(REPO, "crossasset_target.txt")),
              db_path     = get(ENV, "BB_LEDGER_PATH", joinpath(REPO, "alpaca_ledger_crossasset.sqlite")),
              audit_path  = get(ENV, "BB_AUDIT_PATH",  joinpath(REPO, "alpaca_audit_crossasset.jsonl")),
              hwm_path    = get(ENV, "BB_HWM_PATH",    joinpath(homedir(), ".config", "blaquebaux", "equity_hwm_crossasset.txt")),
              equity_path = get(ENV, "BB_EQUITY_PATH", joinpath(homedir(), ".config", "blaquebaux", "equity_last_crossasset.txt")))
    (get(ENV, "ALPACA_KEY_ID", "") == "" || get(ENV, "ALPACA_SECRET_KEY", "") == "") &&
        error("Set ALPACA_KEY_ID and ALPACA_SECRET_KEY (read-only bars are needed even in dry-run).")
    weights, meta, tasof = read_target(target_path)
    isempty(weights) && error("empty target book")
    syms = collect(keys(weights)); dryrun = get(ENV, "BB_DRYRUN", "") in ("1", "true", "yes")
    gross = sum(abs, values(weights))
    panel = panel_at(AlpacaPanelProvider(syms; lookback = 60, feed = "sip"), Dates.today() - Day(2))
    (tasof !== nothing && abs((panel.asof - tasof).value) > 5) &&
        error("target asof $(tasof) misaligned with data asof $(panel.asof) — re-run the allocator")
    prices = Dict(s => panel.prices[findfirst(==(s), panel.symbols)] for s in syms)
    fresh = (Dates.today() - panel.asof) <= Day(30)   # env artifact: data lags the clock; real ops runs daily & fresh

    if dryrun
        cap = capital === nothing ? 100_000.0 : capital
        targets = Dict(s => round(Float64, weights[s]*cap/prices[s]) for s in syms)
        @info "CROSS-ASSET keeper-book dry run" asof=panel.asof mode=get(meta,"mode","?") regime=get(meta,"regime","?") gross=round(gross,digits=2)
        println("\n  governed keeper-book target ($(length(syms)) names, gross $(round(gross,digits=2))x):")
        for (s,w) in sort(collect(weights), by = x -> -abs(x[2]))
            @printf("    %-5s %+6.1f%%  -> %d sh @ \$%.2f\n", s, 100w, Int(get(targets,s,0.0)), get(prices,s,NaN))
        end
        ok, reasons = preflight(; account_status="ACTIVE", equity=100_000.0, hwm=100_000.0, last_equity=100_000.0,
            buying_power=200_000.0, data_fresh=fresh, targets=targets, prices=prices, limits=limits)
        println("\n  DRY RUN — no venue, no orders. Gate: ", ok ? "PASS" : "ABORT: " * join(reasons, "; "))
        return ok ? :dryrun_ok : :dryrun_gate_abort
    end

    live = get(ENV, "BB_LIVE_CONFIRM", "") == LIVE_SENTINEL; paper = !live
    mode = live ? "*** LIVE REAL MONEY ***" : "paper"
    @info "crossasset_live starting" mode alloc=get(meta,"mode","?") regime=get(meta,"regime","?")
    live && alert("CROSS-ASSET keeper-book LIVE REAL-MONEY mode engaged"; level = :critical)
    venue = AlpacaVenue(AlpacaConfig(; paper = paper))
    built = build_live_controller(; venue = venue, ledger_config = LedgerConfig(; db_path = db_path), audit_path = audit_path)
    ctrl, ledger = built.ctrl, built.ledger
    try
        connect!(venue) || (alert("ABORT [$mode]: connect failed (crossasset)"; level = :critical); return :connect_failed)
        acct = account_info(venue)
        acct === nothing && (alert("ABORT [$mode]: no account (crossasset)"; level = :critical); return :no_account)
        cap = capital === nothing ? acct.equity : capital
        hwm = max(load_hwm(hwm_path), acct.equity); last_eq = _readf(equity_path)
        targets = Dict(s => round(Float64, weights[s]*cap/prices[s]) for s in syms)
        ok, reasons = preflight(; account_status=acct.status, trading_blocked=acct.trading_blocked, account_blocked=acct.account_blocked,
            equity=acct.equity, hwm=hwm, last_equity=last_eq, buying_power=acct.buying_power, data_fresh=fresh, targets=targets, prices=prices, limits=limits)
        save_hwm(hwm, hwm_path); _writef(equity_path, acct.equity)
        if !ok
            msg = "SAFETY ABORT [$mode] (crossasset): " * join(reasons, "; "); @error msg
            halt!(ctrl, "safety gate"); alert(msg; level = :critical); return :aborted
        end
        reset_daily!(ctrl); set_pool_budget!(ctrl, pool, limits.max_gross_leverage * acct.equity)
        set_pool_loss_limit!(ctrl, pool, limits.max_daily_loss); set_pool_staleness!(ctrl, pool, Day(5)); feed_staleness!(ctrl, pool; stale = !fresh)
        isfinite(last_eq) && update_pnl!(ctrl, pool, acct.equity - last_eq)
        ncanc = cancel_all_open!(venue); ncanc > 0 && sleep(2)
        for (sym, qty) in positions(venue, ctrl.account); apply_fill!(ctrl, sym, qty); end
        res = execute_rebalance!(ctrl, ledger; targets = targets, prices = prices, signal_id = "crossasset",
            regime = "keeperbook-$(get(meta,"regime","?"))-grossx$(round(gross,digits=2))",
            solve_id = Dates.format(panel.asof, "yyyymmdd"), pool_id = pool, settle_secs = 20)
        !res.reconciled && (alert("RECONCILE FAILED [$mode] (crossasset) — halting"; level = :critical); halt!(ctrl, "reconcile mismatch"))
        summary = "[$mode] crossasset keeper-book (gross $(round(gross,digits=2))x); orders=$(length(res.acks)) fills=$(length(res.fills)) reconciled=$(res.reconciled) equity=$(round(Int, acct.equity))"
        @info "crossasset_live complete" summary; alert(summary; level = :info)
        return res.reconciled ? :ok : :reconcile_failed
    finally
        disconnect!(venue); close_ledger(ledger)
    end
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
