# Kotlin examples for domain-modeling-made-functional Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put a Kotlin/Arrow example next to every C# example in the `domain-modeling-made-functional` skill, in the style of fiscalization-service, and prove agents follow it.

**Architecture:** One Markdown file changes. Kotlin blocks are inserted after the C# blocks they mirror. Two short Kotlin-only notes cover the places Kotlin differs from C# (no `Aff`; `else` in `when`). The description gains "Kotlin with Arrow" within the 1024-character limit.

**Tech Stack:** Markdown skill, Kotlin 2.3 compiler (`kotlin-compiler-embeddable`), arrow-core 1.2.1, Python 3 for the block-compile harness.

**Spec:** `.agents/specs/2026-11-12-dmmf-kotlin-examples-design.md`

## Global Constraints

- Only `plugins/engineering-practices/skills/domain-modeling-made-functional/SKILL.md` changes, plus this plan, the spec and the `.superpowers/sdd/2026-11-12-dmmf-kotlin-examples/` workspace.
- Frontmatter stays valid YAML; `description` stays at or under 1024 characters.
- Kotlin examples use only arrow-core 1.2 APIs: `Either`, `either { }`, `bind()`, `ensure`, `raise`, `Raise<E>`, `Either.catch`, `NonEmptyList`.
- Writing-skills Iron Law: no skill edit before a failing baseline.

## Review Focus

- Every Kotlin block must compile. A skill that teaches uncompilable Kotlin teaches agents to guess. Task 4 compiles every block.
- The infrastructure-error note must not contradict the three-track railroad. Infrastructure failures go on the shell's error type, never on a pure domain function's.
- Description length: it was 1023 characters before the change.

---

### Task 1: Baseline — run the scenario without Kotlin examples

**Files:**
- Create: `.superpowers/sdd/2026-11-12-dmmf-kotlin-examples/skill-test-scenario.md`
- Create: `.superpowers/sdd/2026-11-12-dmmf-kotlin-examples/skill-test-results.md`

- [x] **Step 1: Snapshot the current skill**

```bash
mkdir -p /tmp/skilltest/baseline
cp plugins/engineering-practices/skills/domain-modeling-made-functional/SKILL.md /tmp/skilltest/baseline/SKILL.md
```

- [x] **Step 2: Dispatch five fresh subagents with the scenario prompt pointing at `/tmp/skilltest/baseline/SKILL.md`**

Prompt: `skill-test-scenario.md`. One sample per subagent, no other files readable.

- [x] **Step 3: Score each run on the four style checks and record verbatim evidence**

Checks: ports as `fun interface` + `suspend operator fun invoke`; infrastructure failure returned in `Either` from adapters and kept out of the pure core; companion `operator fun invoke` smart constructors; `Raise<E>` step functions. Control: exhaustive `when` without `else`.

Expected: drift on the first four in most runs. Observed: 0/5, 0/5, 0/5, 1/5 (control 5/5).

### Task 2: Description and intro

**Files:**
- Modify: `plugins/engineering-practices/skills/domain-modeling-made-functional/SKILL.md` (frontmatter, intro paragraph)

- [x] **Step 1: Add "Kotlin with Arrow" to the trigger list and trim to fit**

`the functional rendering of domain-driven design` → `functional domain-driven design`; `C# with records and LanguageExt` → `C# with LanguageExt, Kotlin with Arrow`.

- [x] **Step 2: Say in the intro that Kotlin examples sit alongside the C# ones, with Arrow in LanguageExt's role**

- [x] **Step 3: Check YAML and length**

```bash
python3 -c "import yaml; s=open('plugins/engineering-practices/skills/domain-modeling-made-functional/SKILL.md').read(); d=yaml.safe_load(s.split('---')[1])['description']; print(len(d)); assert len(d) <= 1024"
```

Expected: `1013`

### Task 3: Kotlin examples next to the C# ones

**Files:**
- Modify: `plugins/engineering-practices/skills/domain-modeling-made-functional/SKILL.md`

- [x] **Step 1: Wrapped primitives** — `@JvmInline value class CustomerId`; `EmailAddress` with private constructor and companion `operator fun invoke` returning `Either<ValidationError, EmailAddress>` via `either { ensure(...) }`.
- [x] **Step 2: Sum types** — nullable-fields `data class Order` (bad), `sealed interface Order` with nested `data class` states (better).
- [x] **Step 3: Workflow signature** — `fun interface PlaceOrder { suspend operator fun invoke(...): Either<PlaceOrderError, List<PlaceOrderEvent>> }`.
- [x] **Step 4: Errors as values** — throwing `placeOrder` (bad), `Either`-returning signature and `sealed interface PlaceOrderError` (good).
- [x] **Step 5: Infrastructure-error note** — `CloseDayError.InfrastructureError`, `fun interface SaveFiscalDay`, adapter using `Either.catch { }.mapLeft(...)`.
- [x] **Step 6: Total functions** — `when` with `else` (bad), exhaustive grouped `when` (good), plus the note that `else` is Kotlin's hole.
- [x] **Step 7: Dependency parameterization** — `class PlaceOrder(private val pricing: PricingService)` (OO) and `fun placeOrder(getPrice: (ProductId) -> Money, ...)` (parameterized).
- [x] **Step 8: Two chained sandwiches** — `either { }` shell with `when (val plan = planOrder(...))` over `ReadyToPlace` / `NeedsReprice`.
- [x] **Step 9: Workflow composition** — `either { }` with `.bind()` per step; `Raise<PlaceOrderError>.priceOrder` as the alternative.
- [x] **Step 10: Commands and events, cart states** — `data class PlaceOrderCommand`, `sealed interface PlaceOrderEvent`, `sealed interface Cart` with Arrow `NonEmptyList`.
- [x] **Step 11: Review checklist** — Kotlin partial-function markers (`!!`, `lateinit`, `when` with `else`) and `Instant.now()`.

### Task 4: Compile every Kotlin block

**Files:**
- Create: `.superpowers/sdd/2026-11-12-dmmf-kotlin-examples/check_blocks.py`

- [x] **Step 1: Point the harness at a Kotlin compiler and Arrow**

`KOTLINC_CP` is the compiler classpath (`kotlin-compiler-embeddable`, `kotlin-stdlib`, `kotlin-script-runtime`, `kotlin-reflect`, `kotlin-daemon-embeddable`, `trove4j`, `kotlinx-coroutines-core-jvm`, `annotations`). `KOTLIN_LIB` is the compile classpath (`kotlin-stdlib`, `arrow-core-jvm` 1.2.1, `arrow-atomic-jvm`, `arrow-annotations-jvm`, `arrow-continuations-jvm`, `kotlinx-coroutines-core-jvm`). Both are colon-separated jar lists.

- [x] **Step 2: Run the harness**

```bash
python3 .superpowers/sdd/2026-11-12-dmmf-kotlin-examples/check_blocks.py \
  plugins/engineering-practices/skills/domain-modeling-made-functional/SKILL.md
```

Expected: `13 kotlin blocks -> 14 files`, then `exit 0`. The first run failed on an unqualified nested `InfrastructureError`; the block now uses `CloseDayError.InfrastructureError`.

- [x] **Step 3: Check that the companion `invoke` wins over the private constructor at the call site**

`EmailAddress("a@b.c")` from outside the class prints `Either.Right(EmailAddress(value=a@b.c))`; `EmailAddress("nope")` prints `Either.Left(ValidationError(message=not an email: nope))`.

### Task 5: Re-run the scenario with the edited skill

**Files:**
- Modify: `.superpowers/sdd/2026-11-12-dmmf-kotlin-examples/skill-test-results.md`

- [x] **Step 1: Snapshot the edited skill to `/tmp/skilltest/after/SKILL.md` and dispatch five fresh subagents with the same prompt**

- [x] **Step 2: Score on the same checks**

Expected: each check up from baseline. Observed: 5/5, 5/5, 4/5, 3/5 (control 5/5). Runs converge on one shape, so no wording refactor.

### Task 6: Commit and open the PR

- [x] **Step 1: Commit**

```bash
git add plugins/engineering-practices/skills/domain-modeling-made-functional/SKILL.md
git commit -m "docs(domain-modeling-made-functional): Kotlin readers get Arrow examples next to the C# ones"
```

- [x] **Step 2: Open the PR against `main`** — [krzykrucz/claude-skills#1](https://github.com/krzykrucz/claude-skills/pull/1).

- [x] **Step 3: Commit the spec, this plan and the `.superpowers/` workspace to the PR branch**
