#!/bin/bash
# run_crossasset_daily.sh — the governed CROSS-ASSET keeper book (Block, seven-block synthesis). Two steps:
# (1) the Python allocator emits today's validated target book; (2) the Julia governed driver routes it through
# the Layer-3 safety gate. DRY-RUN by default; graduates to PAPER once ~/.config/blaquebaux/alpaca_crossasset.env exists.
set -uo pipefail
REPO="/Users/malcolmx/blaquebaux-block"; ENGINE="$REPO/engine"; JULIA="/Users/malcolmx/.juliaup/bin/julia"
DATAENV="$HOME/.config/blaquebaux/alpaca.env"; SLEEVEENV="$HOME/.config/blaquebaux/alpaca_crossasset.env"
LOGDIR="$REPO/logs"; mkdir -p "$LOGDIR"; LOG="$LOGDIR/crossasset_$(TZ=America/New_York date +%Y%m%d).log"
exec >> "$LOG" 2>&1
echo "======== $(TZ=America/New_York date '+%F %T %Z') crossasset keeper-book run ========"
export BB_LEDGER_PATH="$REPO/alpaca_ledger_crossasset.sqlite" BB_AUDIT_PATH="$REPO/alpaca_audit_crossasset.jsonl"
export BB_HWM_PATH="$HOME/.config/blaquebaux/equity_hwm_crossasset.txt" BB_EQUITY_PATH="$HOME/.config/blaquebaux/equity_last_crossasset.txt"
export BB_ALLOC_TARGET="$REPO/crossasset_target.txt"
if [ -f "$SLEEVEENV" ]; then set -a; source "$SLEEVEENV"; set +a
else [ -f "$DATAENV" ] && { set -a; source "$DATAENV"; set +a; }; export BB_DRYRUN=1; fi
if [ -z "${ALPACA_KEY_ID:-}" ] || [ -z "${ALPACA_SECRET_KEY:-}" ]; then echo "no ALPACA keys — skipping"; exit 0; fi
MODE=$([ "${BB_DRYRUN:-}" = "1" ] && echo dryrun || echo paper); echo "mode=$MODE"
if [ "$MODE" = "paper" ]; then
  CLOCK=$(curl -s --max-time 15 -H "APCA-API-KEY-ID: $ALPACA_KEY_ID" -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY" https://paper-api.alpaca.markets/v2/clock)
  IS_OPEN=$(echo "$CLOCK" | grep -Eo '"is_open":(true|false)' | grep -Eo 'true|false' | head -1)
  NEXT_OPEN=$(echo "$CLOCK" | grep -o '"next_open":"[^"]*"' | grep -Eo '[0-9]{4}-[0-9]{2}-[0-9]{2}' | head -1)
  ET_TODAY=$(TZ=America/New_York date +%F)
  if { [ -n "$IS_OPEN" ] || [ -n "$NEXT_OPEN" ]; } && [ "$IS_OPEN" != "true" ] && [ "$NEXT_OPEN" != "$ET_TODAY" ]; then echo "not a trading day — skipping"; exit 0; fi
  ORDERS_TODAY=$(curl -s --max-time 15 -H "APCA-API-KEY-ID: $ALPACA_KEY_ID" -H "APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY" "https://paper-api.alpaca.markets/v2/orders?status=all&limit=10&after=${ET_TODAY}T00:00:00Z" | grep -o '"id"' | wc -l | tr -d ' ')
  [ "${ORDERS_TODAY:-0}" -gt 0 ] && { echo "already placed today — skipping (catch-up no-op)"; exit 0; }
fi
cd "$REPO" || exit 1
echo "--- step 1: allocator (emit target) ---"; /usr/bin/python3 "$REPO/live/crossasset_allocator.py" || { echo "allocator failed"; exit 1; }
echo "--- step 2: governed driver (route target) ---"; "$JULIA" --project="$ENGINE" "$REPO/live/crossasset_live.jl"; RC=$?
echo "======== done rc=$RC $(TZ=America/New_York date '+%T %Z') ========"; exit $RC
