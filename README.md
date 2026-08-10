# Blaque Baux Block

**A block of derivative strategies, bundled into one book.**

Block is a member of the Blaque Baux family. The [core repo](https://github.com/Carter-Warrens/blaquebaux)
is the **engine and blueprint** — a governed, systematic platform (Julia) with a venue-agnostic
execution controller and a Layer-3 live-money safety gate. Block points that engine in its own
direction and inherits the governance wholesale.

> **Not investment advice.** Educational/research software. Nothing here is validated. See [LICENSE](LICENSE).

```bash
git clone --recursive https://github.com/Carter-Warrens/blaquebaux-block.git
julia --project=engine -e 'using Pkg; Pkg.instantiate()'   # one-time engine setup
```

## The thesis

A meta-sleeve: a basket of derivative-based strategies (options overlays, futures/vol, structured payoffs) combined into one book and weighted by the engine's optimizer. It is the derivatives counterpart to how the spine blends sleeves — Brittle (short premium) and Bleed (long tails) are natural components, sized so the block is balanced rather than one-sided.

## Research plan (Path A — not yet built)

- Component strategies — covered/overlay, calendar/vol, defined-risk spreads (build on Brittle).
- Optimizer-weighted blend — use the engine's PortfolioOpt to combine the derivative sleeves.
- Balance convexity — pair Brittle-style short-premium with Bleed-style long tails.

Nothing above is implemented or validated. This is the map, not the territory.

## Status
**Scaffold.** Engine wired as a submodule; strategy research not yet conducted.

## The Blaque Baux family
This repo is one sleeve of the **Blaque Baux** family — a single governed engine steered in
many directions. The [core repo](https://github.com/Carter-Warrens/blaquebaux) is the
base/blueprint and holds the [full family roster](https://github.com/Carter-Warrens/blaquebaux#the-blaque-baux-family).

## Layout
```
engine/     the Blaque Baux platform (git submodule -> Carter-Warrens/blaquebaux)
research/   Path-A strategy sketches (to come)
live/       governed live drivers (once a sleeve graduates to paper A/B)
```

## License
[MIT](LICENSE). (c) 2026 Carter Warrens.
