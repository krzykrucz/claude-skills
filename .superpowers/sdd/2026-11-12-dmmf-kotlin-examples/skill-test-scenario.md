# Skill test scenario: close fiscal day in Kotlin

Pressure: a realistic Kotlin/Arrow/Spring feature with a mid-decision external call, nullable DTO input, and failing infrastructure. Each run gets one fresh subagent that may read only the skill snapshot.

- Baseline: `SKILL_PATH=/tmp/skilltest/baseline/SKILL.md` (skill on `main`)
- With skill: `SKILL_PATH=/tmp/skilltest/after/SKILL.md` (skill on the PR branch)

## Prompt

```text
You are a senior Kotlin backend engineer. First read the skill file ${SKILL_PATH} in full and apply it. Do NOT read any other files or repositories, and do not write any files — answer only in your final message.

Task: Our Kotlin service (Kotlin 1.9, arrow-core 1.2 and arrow-fx-coroutines on the classpath, coroutines, Spring at the edges) needs a new "close fiscal day" feature. Design the domain types and workflow, in Kotlin code only:

- A FiscalDay for a merchant is Open (has a non-empty list of receipts so far, each with a receipt number and gross amount in minor units) or Closed (has the receipts, a total, and a signature) or Empty (no receipts yet).
- Command: CloseFiscalDay(merchantCode: String, day: LocalDate) arrives from a Kafka listener as a DTO with nullable fields.
- Rules: an Empty day cannot be closed (domain failure). A Closed day cannot be closed again (domain failure). Closing computes the total and needs a signature from an external signing service — the signing service needs the computed total first, so the decision needs an external call partway through.
- Infrastructure: a repository loads/saves the day; a publisher emits the FiscalDayClosed event; DB/HTTP can fail.

Deliver: (1) wrapped primitives with validation, (2) the state type, (3) the error and event types, (4) the DTO → domain parsing, (5) the pure domain function(s), (6) the application-service/shell code that orchestrates I/O, (7) a short note on which approach you used for the mid-decision signing call. Keep it compact (around 120-180 lines of Kotlin total). Return the code in your final message.
```

## Checks

Taken from how fiscalization-service writes Kotlin/Arrow:

1. **Ports**: `fun interface` with `suspend operator fun invoke` (`CreateInvoiceInTSS`), not named methods.
2. **Infrastructure errors**: adapters return failures in `Either` as an infrastructure case (`FiscalizationError.InfrastructureError`); the shell `bind()`s them; pure functions' error types stay domain-only.
3. **Smart constructors**: companion `operator fun invoke` returning `Either` (`ClassificationCode`), not `of` / `parse`.
4. **Fallible steps**: `Raise<E>.` extension functions (`Raise<ValidationError>.convertToDomain`).
5. **Control**: exhaustive `when` over sealed types with no `else`. The skill already covered this before the change.
