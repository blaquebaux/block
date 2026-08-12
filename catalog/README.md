# Block Derivatives Catalog

The **machine-readable backbone** of the Block sleeve: the ~80 derivative strategy *building blocks* from the
Derivatives Master Reference (Kareem Williams / Carter Warrens, Blaque Baux initiative), spanning **equity, FX,
interest rates, credit, commodities, municipals, and funding**. This is the taxonomy everything in Block hangs
off — pricing/execution code is layered on top later, keyed by `id`.

## Files

| File | What it is |
|---|---|
| [`derivatives_catalog.json`](derivatives_catalog.json) | The catalog — 80 self-describing strategy entries. **The source of record for machines.** |
| [`schema.json`](schema.json) | JSON-Schema (draft-07) for a strategy entry — validate additions against it. |
| [`INDEX.md`](INDEX.md) | Human-readable index (generated). |
| [`build_catalog.py`](build_catalog.py) | The source of truth. Edit here, then `python build_catalog.py` regenerates all three above. |

## The organizing principle

> **Each entry is a building block, not a standalone strategy. None is alpha on its own.**

A vanilla swap or a plain forward isn't an edge — it's vocabulary. The value is in **composition**: hedging one
block with another, arbitraging a basis (NDF vs onshore, CDS vs bond, swap vs treasury), or combining several
into a bespoke exposure — all under the engine's governance (the Layer-3 safety gate, the venue-agnostic
controller). That is the Blaque Baux thesis applied to derivatives: the sleeves are **guardrails and comfort**
for building better bespoke returns in a dynamic market — not a set-and-forget money machine.

Every entry therefore carries a `combinations` field: the documented hedging / arbitrage / composition plays
that block participates in. Those links are where the actual research and returns live.

## Entry shape

```jsonc
{
  "id": "irs_vanilla",                     // stable snake_case key — the join key for code/diagrams/tests
  "name": "Interest Rate Swap",
  "tag": "IRS",                            // the deck's abbreviation
  "asset_class": "rates",                  // rates | fx | equity | credit | commodity | municipal | funding
  "family": "swap",                        // swap | forward | option | variance | barrier | swaption | ...
  "parties": ["Fixed-Rate Payer (A)", "Floating-Rate Payer (B)"],
  "legs": [["A","B","pays fixed rate"], ["B","A","pays floating (SOFR/…)"]],   // [from, to, cash-flow]
  "parameters": ["notional_principal", "fixed rate", "floating reference", "tenor", ...],
  "settlement": "net cash each payment date; principal never exchanged",
  "payoff": "net = (fixed - floating) * notional * daycount",
  "variants": ["average","callable","arrears","OIS","zero-coupon","onshore"],
  "combinations": ["swap-spread vs treasury","swaption to enter","collar via cap/floor"],
  "use": "core rate hedge/speculation building block",
  "deck_slide": 3,
  "detail_level": "full",                  // "full" = written-up in the reference; "diagram" = flow-diagram only
  "status": "reference"                    // reference -> spec -> implemented -> validated
}
```

## Coverage (80 blocks)

| Asset class | # | Highlights |
|---|---|---|
| **Rates** | 24 | FRA, IRS (+ average/callable/arrears/OIS/ZC/onshore), cap/floor/collar/spread, swaptions (Eur/Berm/straddle), XCCY (MTM/non-MTM/ND/onshore), swap-spread, treasury lock |
| **FX** | 26 | spot & forwards (outright/avg/target/accumulator/onshore), FX swap, options (vanilla/quanto/digital/barrier/double/one-touch/Asian/RR/straddle/strangle), full **NDF** set |
| **Equity** | 16 | autocallable note, forward (amort/accreting strike), TRS, ASR, Asian, fwd-start, cliquet, **vol/variance/conditional-var/var-contingent**, bespoke, barrier, equity-linked deposit |
| **Credit** | 5 | CDS single-name, CDS index (waterfall), CDS index option, RPA, TRS |
| **Commodity** | 2 | cleared future, commodity TRS |
| **Municipal** | 4 | Muni TRS, MMD TRS, MMD rate lock, muni fees |
| **Funding** | 3 | deposit, interaffiliate loan, cost-of-funds |

## Extending

1. Add an `S(...)` entry in [`build_catalog.py`](build_catalog.py) under its asset class.
2. `python build_catalog.py` to regenerate the JSON, schema, and index.
3. Validate: the entry must satisfy [`schema.json`](schema.json).
4. Advance `status` (`reference → spec → implemented → validated`) as pricing/execution code and a validation
   gate are added for that block — matching how every other Blaque Baux sleeve graduates.

## Status

**Reference taxonomy — no pricing code yet.** This is the backbone (the *what*); the *how* (payoff/pricing
engines, then governed execution) is layered on next, block by block, each earning its `status` upgrade through
the same validate-before-live discipline as the rest of the platform.
