# Block Derivatives Catalog — Index

*Generated from `build_catalog.py` — 80 strategy building blocks. Machine-readable source: [`derivatives_catalog.json`](derivatives_catalog.json), schema: [`schema.json`](schema.json).*

> Each entry is a **building block, not a standalone strategy**. None is alpha alone — the value is in **composition** (hedging / arbitrage / combination) under the engine's governance.

## Rates — Interest-rate & cross-currency derivatives  (24)

| id | strategy | tag | family | key legs |
|---|---|---|---|---|
| `fra` | Forward Rate Agreement | FRA | forward-rate | Seller→Buyer: pays PV of (R_actual - R_fixed) if rates rose ; Buyer→Seller: pays if rates  |
| `irs_vanilla` | Interest Rate Swap | IRS | swap | A→B: pays fixed rate ; B→A: pays floating (SOFR/SONIA/€STR) |
| `irs_average` | Average Rate Swap | IRS Average | swap | Fixed→Float: pays fixed rate ; Float→Fixed: pays average floating rate over period |
| `irs_swap_spread` | Swap Spread (BGS) | IRS BGS | spread | Payer→Receiver: pays IRS rate + spread ; Receiver→Payer: pays Treasury rate |
| `irs_callable` | Callable Swap | IRS Callable | swap+option | Fixed→Float: pays fixed ; Float→Fixed: pays floating ; Fixed→-: right to terminate early |
| `irs_arrears` | Swap in Arrears | IRS in arrears | swap | Fixed→Float: pays fixed ; Float→Fixed: pays floating set in arrears |
| `irs_ois` | OIS Swap | IRS OIS | swap | Fixed→Float: pays fixed ; Float→Fixed: pays compounded overnight rate |
| `irs_ois_onshore` | Onshore OIS Swap | IRS OIS Onshore | swap | Fixed→Float: pays local-currency fixed ; Float→Fixed: pays local O/N compounded |
| `treasury_lock` | Treasury Lock | Treasury Lock | forward | Buyer/Seller→-: pays based on future Treasury price/yield |
| `irs_zero_coupon` | Zero Coupon Swap | IRS ZC | swap | Fixed→Float: pays fixed lump sum at maturity ; Float→Fixed: pays floating periodically |
| `irs_onshore` | Onshore IRS | IRS Onshore | swap | Fixed→Float: pays local-currency fixed ; Float→Fixed: pays local-currency floating |
| `cap_floor` | Cap / Floor | Cap/Floor | option | Buyer→Seller: pays premium ; Seller→Buyer: pays if reference > cap strike (or < floor stri |
| `collar` | Collar | Collar | option-combo | Buyer→-: long cap + short floor (premium often ~0) |
| `cap_floor_straddle` | Cap/Floor Straddle | Cap/Floor Straddle | option-combo | Buyer→-: long cap + long floor, same strike & dates |
| `cap_floor_spread` | Cap/Floor Spread | Cap/Floor Spread | option-combo | Investor→-: long cap at strike1 + short cap at strike2 |
| `irs_swaption` | Swaption | IRS Cap Floor | swaption | Buyer→Seller: pays premium ; Seller→Buyer: grants right to enter an IRS |
| `swaption_european` | European Swaption | European Swaption | swaption | Buyer→Seller: pays premium ; Seller→Buyer: right to enter IRS on ONE fixed date |
| `swaption_bermudan` | Bermudan Swaption | Bermudan Swaption | swaption | Buyer→Seller: pays premium ; Seller→Buyer: right to enter IRS on MULTIPLE fixed dates |
| `swaption_straddle` | Straddle Swaption | Straddle Swaption | swaption | Buyer→Seller: pays premium ; Seller→Buyer: right to enter IRS as fixed payer OR receiver |
| `xccy_mtm` | Mark-to-Market Cross-Currency Swap | Xccy MTM | xccy-swap | A→B: Currency A leg + MTM reset ; B→A: Currency B leg + MTM reset |
| `xccy_non_mtm` | Non-MTM Cross-Currency Swap | Xccy non MTM | xccy-swap | A→B: Currency A fixed rate ; B→A: Currency B fixed rate |
| `xccy_swap_spread` | Cross-Currency Swap Spread (BGS) | Xccy Swap BGS | xccy-spread | Payer→Receiver: pays XCCY rate + spread ; Receiver→Payer: pays local IRS rate |
| `xccy_non_mtm_onshore` | Onshore Non-MTM Cross-Currency Swap | Xccy non MTM Onshore | xccy-swap | A→B: Local currency A fixed rate ; B→A: Local currency B fixed rate |
| `xccy_nd` | Non-Deliverable Cross-Currency Swap | Xccy ND | xccy-swap | A→B: USD floating ; B→A: NDF fixing vs strike, settled in USD |

## Fx — Foreign-exchange derivatives (deliverable, onshore, and non-deliverable)  (26)

| id | strategy | tag | family | key legs |
|---|---|---|---|---|
| `fx_spot` | Spot Transaction | Spot | spot | Buyer→Seller: pays Currency A (spot date) ; Seller→Buyer: delivers Currency B (spot date) |
| `fx_spot_onshore` | Spot Transaction Onshore | Spot Onshore | spot | Buyer→Seller: local currency T+1/T+2 ; Seller→Buyer: delivers FX T+1/T+2 |
| `fx_outright_forward` | Outright Forward | Outright | forward | Long→Short: pays agreed forward price ; Short→Long: delivers underlying asset |
| `fx_outright_onshore` | Outright Forward Onshore | Outright Onshore | forward | Buyer→Seller: local currency, agreed future date ; Seller→Buyer: delivers FX, agreed futur |
| `fx_avg_rate_forward` | Average Rate Forward | Avg Rate Fwd FXD | forward | Buyer→Seller: pays average rate vs agreed forward rate |
| `fx_target_forward` | Target Forward | Target Forward FXD | structured-forward | Client→Bank: FX at better rate if spot stays in range ; Bank→Client: FX at worse rate if s |
| `fx_forward_accumulator` | Forward Accumulator | Fwd Accumulator FXD | structured-forward | Client→Bank: buys FX daily when spot is below barrier |
| `fx_swap` | FX Swap | FX Swap | swap | A→B: Currency A spot then forward date ; B→A: Currency B spot then forward date |
| `fx_swap_onshore` | FX Swap Onshore | FX Swap Onshore | swap | A→B: local currency near leg / far leg ; B→A: FX near leg / far leg |
| `fx_time_option` | Time Option (Optional Delivery Forward) | Time Option | forward+option | Holder→Writer: chooses delivery date within window ; Writer→Holder: delivers FX on selecte |
| `fx_risk_reversal` | Risk Reversal | Risk Rev FXD | option-combo | Investor→-: long call + short put (or vice versa) |
| `fx_straddle` | Straddle | Straddle FXD | option-combo | Investor→-: long call + long put, same strike & expiry |
| `fx_strangle` | Strangle | Strangle FXD | option-combo | Investor→-: long OTM call + long OTM put |
| `fx_one_touch` | One-Touch / No-Touch | Touch FXD | binary-barrier | Buyer→Seller: pays premium ; Seller→Buyer: pays fixed amount if spot touches / does NOT to |
| `fx_simple_barrier` | Simple Barrier Option | Simple Barrier FXD | barrier-option | Buyer→Seller: pays premium ; Seller→Buyer: pays out if barrier condition is met |
| `fx_double_barrier` | Double Barrier Option | Double Barrier FXD | barrier-option | Buyer→Seller: pays premium ; Seller→Buyer: pays out if EITHER barrier is triggered |
| `fx_avg_rate_option` | Average Rate Option (Asian) | Asian FXD | asian-option | Buyer→Seller: pays premium ; Seller→Buyer: pays based on average rate vs strike |
| `fx_digital` | Digital Option | Digital Option FXD | binary | Buyer→Seller: pays premium ; Seller→Buyer: pays fixed amount if spot is in/out-of-the-mone |
| `fx_vanilla` | Vanilla Option | Vanilla Option FXD | option | Buyer→Seller: pays premium ; Seller→Buyer: pays intrinsic value if exercised |
| `fx_quanto` | Quanto Option | Quanto Option FXD | option | Buyer→Seller: pays premium ; Seller→Buyer: pays in DOMESTIC currency based on FX move |
| `fx_nd_option` | Non-Deliverable Option | ND Option FXD | option | Buyer→Seller: pays premium ; Seller→Buyer: cash settles difference in NDF rate vs strike |
| `fx_nd_option_onshore` | Non-Deliverable Option Onshore | ND Opt FXD Onshore | option | Buyer→Seller: pays premium ; Seller→Buyer: cash settles in local currency |
| `ndf` | Non-Deliverable Forward | NDF | forward | Long→Short: pays notional * agreed NDF rate ; Short→Long: pays notional * settlement (fixi |
| `ndf_onshore` | Non-Deliverable Forward Onshore | NDF Onshore | forward | Long→Short: local currency at agreed NDF rate ; Short→Long: local currency at settlement r |
| `ndf_fx_swap` | NDF FX Swap | NDF FX Swap | swap | A→B: NDF near leg ; B→A: NDF far leg |
| `ndf_fx_swap_onshore` | NDF FX Swap Onshore | NDF FX Swap Onshore | swap | A→B: local currency NDF near leg ; B→A: local currency NDF far leg |

## Equity — Equity derivatives (forwards, structured notes, options, variance/vol)  (16)

| id | strategy | tag | family | key legs |
|---|---|---|---|---|
| `eqd_autocall` | Autocallable Equity Note | Autocall EQD | structured-note | Investor→Issuer: pays notional ; Issuer→Investor: coupons if reference at/above barrier ;  |
| `eqd_forward` | Equity Forward | Forward EQD | forward | Long→Short: pays agreed forward price ; Short→Long: delivers underlying shares or cash equ |
| `eqd_trs` | Total Return Swap (Equity) | TRS EQD | swap | Payer (e.g. hedge fund)→Receiver: pays floating (SOFR+spread) ; Receiver (e.g. investor)→P |
| `eqd_amort_strike_fwd` | Amortizing Strike Forward | Amort Strike Fwd EQD | forward | Long→Short: pays pre-determined amortizing strike price ; Short→Long: delivers underlying  |
| `eqd_asian` | Asian Option (Equity) | Asian Option EQD | asian-option | Buyer→Seller: pays premium ; Seller→Buyer: pays based on difference between average price  |
| `eqd_asr` | Accelerated Share Repurchase | ASR EQD | buyback | Corp→Bank: pays upfront for initial shares ; Bank→Corp: delivers initial share tranche ; C |
| `eqd_fwd_start_option` | Forward Start Option | Fwd Start Option EQD | option | Buyer→Seller: pays premium ; Seller→Buyer: option strike set at-the-money on a future star |
| `eqd_accr_strike_fwd` | Accreting Strike Forward | Accr Strike Fwd EQD | forward | Long→Short: pays pre-determined accreting strike price ; Short→Long: delivers underlying s |
| `eqd_cliquet` | Cliquet Option | Cliquet EQD | option | Buyer→Seller: pays premium ; Seller→Buyer: pays sum of capped periodic returns |
| `eqd_var_contingent` | Variance Contingent Swap | Var Contingent EQD | variance | Buyer→Seller: pays fixed leg ; Seller→Buyer: pays realized variance IF barrier is breached |
| `eqd_volatility_swap` | Volatility Swap | Volatility EQD | variance | Buyer→Seller: pays fixed vol (notional * strike vol) ; Seller→Buyer: pays realized vol (no |
| `eqd_variance_swap` | Variance Swap | Variance Swap EQD | variance | Buyer→Seller: pays fixed variance (notional * strike var) ; Seller→Buyer: pays realized va |
| `eqd_conditional_var` | Conditional Variance Swap | Cond Var Swap EQD | variance | Buyer→Seller: pays fixed variance ; Seller→Buyer: pays realized variance ONLY if option ex |
| `eqd_bespoke_option` | Bespoke Option | Bespoke Option EQD | option | Buyer→Seller: pays premium ; Seller→Buyer: pays based on custom payoff formula |
| `eqd_barrier` | Barrier Option (Equity) | Barrier Option EQD | barrier-option | Buyer→Seller: pays premium ; Seller→Buyer: pays out if barrier is triggered |
| `eqd_deposit_strategy` | Deposit-Based Strategy | Depo Strategy EQD | structured-deposit | Investor→Bank: deposits cash ; Bank→Investor: pays interest + equity-linked return |

## Credit — Credit derivatives (CDS, index, options, TRS)  (5)

| id | strategy | tag | family | key legs |
|---|---|---|---|---|
| `cds_single` | Credit Default Swap (Single-Name) | CDS Single | credit-swap | Buyer→Seller: periodic premium = spread * notional * daycount ; Seller→Buyer: on credit ev |
| `cds_index` | Credit Default Swap (Index) | CDS Index | credit-swap | Buyer→Seller: fixed running coupon (e.g. 100bps) + upfront adjustment ; Seller→Buyer: per- |
| `cds_index_option` | CDS Index Option | CDS Index Option | credit-option | Buyer→Seller: pays premium ; Seller→Buyer: right to buy/sell index protection at a strike  |
| `rpa` | Rate Participation Agreement | RPA | structured-rate | Buyer→Seller: pays premium/fee ; Seller→Buyer: participation in a reference rate move |
| `trs` | Total Return Swap (generic) | TRS | swap | Payer→Receiver: pays financing (floating + spread) ; Receiver→Payer: pays total return of  |

## Commodity — Commodity derivatives  (2)

| id | strategy | tag | family | key legs |
|---|---|---|---|---|
| `com_future` | Futures Contract | Future COM | future | Long→Clearing House: pays daily variation margin ; Short→Clearing House: pays daily variat |
| `com_trs` | Total Return Swap (Commodity) | TRS COM | swap | Payer→Receiver: pays financing (floating + spread) ; Receiver→Payer: pays total return of  |

## Municipal — Municipal / MMD derivatives  (4)

| id | strategy | tag | family | key legs |
|---|---|---|---|---|
| `muni_trs` | Municipal Total Return Swap | Muni TRS | swap | Payer→Receiver: pays floating rate + asset depreciation ; Receiver→Payer: pays total retur |
| `mmd_trs` | MMD (Municipal Market Data) TRS | MMD TRS | swap | Payer→Receiver: pays floating rate + MMD spread ; Receiver→Payer: pays MMD index total ret |
| `mmd_rate_lock` | MMD Rate Lock | MMD Rate Lock | forward | Borrower/Bank→-: locks MMD rate for a future bond issuance |
| `muni_fees` | Municipal Fees | Muni Fees | fee | Issuer→Underwriter: pays underwriting fees & expenses |

## Funding — Funding, deposit & cost-of-funds instruments  (3)

| id | strategy | tag | family | key legs |
|---|---|---|---|---|
| `deposit` | Deposit | Depo | deposit | Depositor→Bank: lends principal ; Bank→Depositor: pays principal + interest at maturity |
| `interaffiliate_loan` | Interaffiliate Loan | Interaffiliate Loan | loan | A→B: lends loan amount ; B→A: pays interest + principal at maturity |
| `cost_of_funds` | Cost of Funds | COF | funding-benchmark | Bank→Lender/Depositor: pays interest based on its funding cost |
