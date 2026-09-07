#!/usr/bin/python3
# =============================================================================
# build_factoids.py — derive analytic factoids for the 120 Block derivatives, for the site's Block page.
#
# Two honest buckets:
#   COMPUTED from the catalog structure (legs/family/payoff/params/variants) — risk, complexity, versatility,
#     and the family's three-axis "Where the Fee Lives" taxonomy (TAIL / MARK / FUNDING / honest).
#   SOURCED, external — real-market usage/rarity. Per-instrument notional is not public; BIS OTC category
#     weights ARE. So usage_tier is a BIS-INFORMED classification (labeled as such), never a faked figure.
# Emits catalog/factoids.json (per-strategy + aggregate headline factoids) and prints the headlines.
# =============================================================================
import json, collections, os
HERE=os.path.dirname(os.path.abspath(__file__))
S=json.load(open(os.path.join(HERE,"derivatives_catalog.json")))["strategies"]

def text(s): return " ".join([str(s.get("name","")),str(s.get("payoff","")),str(s.get("use","")),
                              " ".join(map(str,s.get("legs",[]))),str(s.get("family",""))]).lower()

# --- family → structural tags -------------------------------------------------------------------------
EXOTIC   = {"asian-option","path-option","barrier-option","binary-barrier","binary","variance",
            "credit-tranche","structured-note","structured-credit","structured-rate","structured-forward",
            "structured-deposit","volume-option"}
OPTIONY  = {"option","option-combo","swaption","rate-option","credit-option","inflation-option",
            "barrier-option","asian-option","path-option","binary","binary-barrier","variance","volume-option"}
FUNDINGF = {"xccy-swap","xccy-spread","basis-swap","funding-benchmark","deposit","loan","fee",
            "structured-deposit","bond-plus-swap"}
LINEAR   = {"forward-rate","forward","swap","spot","future","spread","inflation-swap","credit-swap","buyback"}

# structures that ARE inherently short-gamma / unbounded / gap-risk for the typical user (not "has a Seller"):
SHORT_TAIL_FAM={"variance","binary","binary-barrier","barrier-option","credit-tranche","structured-note",
                "structured-credit","volume-option"}
HONEST_FAM={"asian-option","spot","future","forward-rate"}   # averaging / hedging / exchange — buyer-serving
def short_opt(s):  # embeds short optionality / leverage / gap — NOT merely "an option with a seller"
    t=text(s); f=s.get("family","")
    if f in HONEST_FAM: return False
    kw=["target redemption","tarf","autocall","auto-call","range accrual","knock-in","reverse convertible",
        "worst-of","leveraged","geared","3x","2x","short vol","short gamma","digital","one-touch","no-touch"]
    return f in SHORT_TAIL_FAM or any(k in t for k in kw)
def mark_opacity(s):  # value needs unobservable σ / ρ / path
    f=s.get("family",""); t=text(s)
    sc=0
    if f in EXOTIC: sc+=2
    if any(k in t for k in ["correlation","dispersion","basket","tranche","copula"]): sc+=1
    if any(k in t for k in ["average","asian","path","barrier","knock"]): sc+=1
    return min(sc,3)
def otc(s):  # bilateral OTC counterparty/funding exposure (vs exchange-cleared)
    return 0 if s.get("family")=="future" else 1

def risk_score(s):
    f=s.get("family","")
    tail = (2 if short_opt(s) else 0) + (1 if f in {"barrier-option","binary-barrier","binary","variance"} else 0)
    lev  = 2 if any(k in text(s) for k in ["leverage","target redemption","tarf","geared","2x","3x"]) else 0
    exo  = 2 if f in EXOTIC else (1 if f in OPTIONY else 0)
    opa  = mark_opacity(s)
    fund = 1 if f in FUNDINGF else 0
    cpty = otc(s)
    raw  = 3*tail + 2*lev + 1.5*exo + 1.5*opa + 1*fund + 0.5*cpty     # weighted
    return round(min(100, raw/16.5*100))                              # normalize to 0-100

def fee_axis(s):  # the family's "Where the Fee Lives" three-axis taxonomy (+ honest exceptions)
    f=s.get("family",""); t=text(s)
    # honest, buyer-serving exceptions the whitepaper names explicitly — these win outright
    if f in HONEST_FAM or any(k in t for k in ["crack","weather","average rate","asian"]): return "honest / transparent"
    if f in LINEAR and f not in FUNDINGF: return "honest / transparent"   # vanilla linear (IRS/forward/swap/future)
    if short_opt(s): return "TAIL"
    if f in FUNDINGF: return "FUNDING/basis"
    if mark_opacity(s)>=2 or f in OPTIONY: return "MARK (σ/ρ/path)"
    return "honest / transparent"

def complexity(s): return len(s.get("legs",[]))+len(s.get("parameters",[]))+(3 if s.get("family") in EXOTIC else 0)
def versatility(s): return len(s.get("variants") or [])+len(s.get("combinations") or [])

# --- usage tier: BIS-INFORMED (OTC category weights), NOT a per-instrument figure ---------------------
# BIS OTC notional outstanding is ~80% rates, then FX, then a long tail (credit/equity/commodity). Vanilla
# linear products (IRS, FX fwd/swap) are ubiquitous; plain options common; exotics niche/rare.
BIS_CLASS={"rates":"largest OTC class (~80% of notional)","fx":"2nd-largest OTC class",
           "credit":"post-2008 shrunk; CDS index liquid","equity":"smaller OTC; listed options huge",
           "commodity":"smallest OTC class","municipal":"US-specific, niche","funding":"money-market plumbing"}
def usage_tier(s):
    f=s.get("family","")
    if f in {"swap","forward","forward-rate","spot","future"}: return "ubiquitous"
    if f in OPTIONY and f not in EXOTIC: return "common"
    if f in EXOTIC or f in {"credit-tranche","xccy-spread","volume-option","path-option"}: return "rare / niche"
    return "specialist"

# --- build per-strategy factoids ----------------------------------------------------------------------
for s in S:
    s["_risk"]=risk_score(s); s["_fee_axis"]=fee_axis(s); s["_complexity"]=complexity(s)
    s["_versatility"]=versatility(s); s["_usage"]=usage_tier(s)

byrisk=sorted(S,key=lambda x:-x["_risk"]); bycomplex=sorted(S,key=lambda x:-x["_complexity"])
byvers=sorted(S,key=lambda x:-x["_versatility"])
axis_ct=collections.Counter(s["_fee_axis"] for s in S); use_ct=collections.Counter(s["_usage"] for s in S)
ac_ct=collections.Counter(s["asset_class"] for s in S)
struct=collections.Counter(("exotic" if s["family"] in EXOTIC else "optional" if s["family"] in OPTIONY else "linear") for s in S)

agg={
 "total":len(S),
 "by_asset_class":dict(ac_ct.most_common()),
 "by_structure":dict(struct),
 "fee_axis":dict(axis_ct.most_common()),
 "usage_tier":dict(use_ct.most_common()),
 "riskiest":[{ "tag":s["tag"],"name":s["name"],"risk":s["_risk"],"axis":s["_fee_axis"]} for s in byrisk[:10]],
 "safest":[{ "tag":s["tag"],"name":s["name"],"risk":s["_risk"]} for s in byrisk[-6:]],
 "most_complex":[{ "tag":s["tag"],"name":s["name"],"complexity":s["_complexity"]} for s in bycomplex[:6]],
 "most_versatile":[{ "tag":s["tag"],"name":s["name"],"versatility":s["_versatility"]} for s in byvers[:6]],
 "pct_relocating":round(100*(len(S)-axis_ct.get("honest / transparent",0))/len(S)),
}
out={"_meta":{"source":"build_factoids.py over derivatives_catalog.json",
      "computed":"risk/complexity/versatility/fee_axis from catalog structure",
      "sourced":"usage_tier = BIS OTC category weights (informed classification, not per-instrument notional)",
      "bis_class_notes":BIS_CLASS},
     "aggregate":agg,
     "strategies":[{k:s[k] for k in ("id","tag","name","asset_class","family","_risk","_fee_axis","_complexity","_versatility","_usage")} for s in S]}
json.dump(out,open(os.path.join(HERE,"factoids.json"),"w"),indent=2)

# --- print the headline factoids ----------------------------------------------------------------------
print("="*90); print(f"BLOCK FACTOIDS — {len(S)} derivatives"); print("="*90)
print(f"\nBy asset class: {agg['by_asset_class']}")
print(f"By structure:   {agg['by_structure']}")
print(f"\nWhere the fee lives (risk-relocation axis): {agg['fee_axis']}")
print(f"  → {agg['pct_relocating']}% of the catalog relocates risk onto an axis the buyer isn't watching")
print(f"\nUsage (BIS-informed): {agg['usage_tier']}")
print("\nRISKIEST 10 (computed risk score 0-100):")
for r in agg["riskiest"]: print(f"  {r['risk']:3d}  {r['tag']:10} {r['name'][:42]:42} [{r['axis']}]")
print("\nSAFEST / most transparent:")
for r in agg["safest"]: print(f"  {r['risk']:3d}  {r['tag']:10} {r['name'][:42]}")
print("\nMOST COMPLEX:");   [print(f"  {r['complexity']:2d} legs+params  {r['tag']:10} {r['name']}") for r in agg["most_complex"]]
print("\nMOST VERSATILE (variants+combinations):"); [print(f"  {r['versatility']:2d}  {r['tag']:10} {r['name']}") for r in agg["most_versatile"]]
print(f"\nemitted → catalog/factoids.json")
