# detective_engine — a constraint-driven detective-fiction generator (foundation)

[English](README_EN.md) | [简体中文](README.md)

Turning the idea that "a detective story = evidence forged into a chain" into a
**runnable, extensible** engine skeleton.

## Core stance

Purely random combinations of clues do not produce "ingenious" — they produce
noise. Because:

- a random combination of clues is, in the vast majority of cases, not a
  **solvable process at all** (the constraint-satisfaction problem is almost
  always unsatisfiable);
- ingenious = **surprise × inevitability × uniqueness**. Randomness is good at
  manufacturing surprise, but it cannot produce the inevitability that makes a
  reader look back and think "it could only have been this way", nor can it
  guarantee "there is exactly one solution".

So the engine works **backwards**:

```
Truth trajectory --causes--> Traces --select + order--> Plot --score--> Score
        randomness picks raw material here   craft here            choice here
```

## Layered structure

| File | Responsibility |
| --- | --- |
| `detective/model.py` | Data model: `Trace` / `Trick` / `World` / `Trajectory` / `Plot` |
| `detective/trick_library.py` | **Trick library**: each device's preconditions, necessary traces, and reveal |
| `detective/element_library.py` | Raw-material library: core truth clues, red herrings, character/place pools, world settings |
| `detective/constraints.py` | Constraints: premise satisfaction, trick conflicts, **fairness**, consistency |
| `detective/scorer.py` | **Scoring function**: inevitability / uniqueness / surprise / economy / consistency / timing / diversity; ingenious = inevitability × uniqueness × surprise |
| `detective/generator.py` | Backwards-generation pipeline + skeleton dedup and ranking |

## Running

```bash
cd detective_engine
python demo.py                              # generate and print the most ingenious candidates
python -m unittest discover -s tests -v     # self-test
```

## Three extension routes

1. **Add a trick**: append a `Trick` to `trick_library.ALL_TRICKS`, specifying
   `premises` / `traces` / `reveal`. The generator picks it up automatically.
2. **Add a world**: add world facts to `element_library.WORLDS` to open or close
   different combination spaces of tricks.
3. **Tune the taste**: change `scorer.WEIGHTS` and `_INGENUITY_SHARE` to change
   what counts as "ingenious".

## Refactor log: from "the fuller the better" to "surprise × inevitability × uniqueness"

The first scoring function had a fatal bias: **surprise rose monotonically with
the number of red herrings**, so the "optimal" solution was always a crowded
story stuffed with 3 tricks and 3 red herrings, and the top entries were clones
of the same template.

After the refactor:

- ingenious became the product `inevitability × uniqueness × surprise` — any
  factor collapsing kills it;
- surprise gained **diminishing returns + a crowding penalty** (non-monotone);
- **unique solvability** was added (piling several red herrings on the same
  suspect is penalised);
- **misleading timing** (red herrings up front, truth at the end) and **anti-cliché**
  (same-type tricks are not stacked) were added;
- `rank` gained **skeleton dedup**, so it no longer outputs clones.

Effect (suburban villa, 600 candidates, top 50): the trick count no longer
reaches 3; only 1–2 remain.

## An honest finding: any fixed scoring function induces its own template

The refactor fixed the old bias, but a **new bias appeared immediately**. Top-50
statistics:

- red herrings are almost always 3 (surprise is still monotone within its cap);
- killers are heavily concentrated in "younger brother / chauffeur / private
  doctor" — because the red herrings point at "spouse / partner / former
  employee / heir", so the scoring function **automatically prefers the
  characters nobody suspects** (the least-likely suspect).

In other words: **what you change is "which template", not "eliminate the
template".** This is the project's central conclusion — generation is not hard;
what is hard is defining a "taste function" that does not collapse into itself.

## Known boundaries (next steps)

- **Unique solvability is still approximate**: alternative solutions are judged
  only by "suspect vote counts", without real logical entailment.
- **Calibrating surprise / economy**: red herrings still saturate (at 3) within
  reach; a stronger or non-linear load model is needed.
- **Presentation order** has only two modes ("up front / shuffled"); a real
  **information-throttling curve** is not yet done.
- The timeline is not yet modelled as an explicit **event graph**.
- **The trick library is still too small** — the real ceiling on novelty.

## Human-in-the-loop interface (important)

The trick and element libraries are **human-input-first**. Details from real
life, and inspiration you get while reading detective fiction, can go straight
into the library:

- one real-world observation -> one `Trace` (phenomenon + surface misreading +
  what it really points to)
- one "what if..." -> one `Trick` (premise + necessary traces + reveal)

The engine handles combination, constraints and scoring; **the quality of the
inspiration is yours to define.** That is exactly how "taste" is handed back to
the human.

---

[English](README_EN.md) | [简体中文](README.md)
