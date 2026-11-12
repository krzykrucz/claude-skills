# Skill test results

Scenario and checks: `skill-test-scenario.md`. Model: claude-opus-5-5-high, five fresh subagents per side.

## Summary

| Check | Baseline (`main`) | With Kotlin examples |
|---|---|---|
| Ports as `fun interface` + `suspend operator fun invoke` | 0/5 | 5/5 |
| Infrastructure failures returned in `Either`, kept out of the pure core | 0/5 | 5/5 |
| Companion `operator fun invoke` smart constructors | 0/5 | 4/5 |
| `Raise<E>.` step functions | 1/5 | 3/5 |
| Control: exhaustive `when`, no `else` | 5/5 | 5/5 |

The skill already taught the core ideas well without Kotlin examples. Every baseline used sealed interfaces, Arrow `Either`, exhaustive `when`, and two chained sandwiches around the signing call. The drift was all in the shell: how ports, infrastructure failures and smart constructors look in Kotlin.

The with-skill runs land on one shape, so the wording needs no further changes.

## Baseline (RED)

| Run | Ports | Infra errors | Smart constructors | `Raise<E>.` |
|---|---|---|---|---|
| 1 | plain `interface`, named methods | thrown | `of`, `Either<String, _>` | yes (`Raise<ValidationError>.field`) |
| 2 | `fun interface SigningService { suspend fun sign(...): Signature }` | thrown | `of` | no |
| 3 | `fun interface FiscalDayEventPublisher { suspend fun publish(...) }` | thrown | `parse` | no |
| 4 | `fun interface FiscalSigner { suspend fun sign(...): Signature }` | thrown ("infra failures throw from suspend calls") | `parse` | no |
| 5 | `fun interface FiscalSigner { suspend fun sign(request): Signature }` | thrown | `parse` | no |

Rationalizations seen:

- Run 4's comment: "infra failures throw from suspend calls". The baselines treated the skill's `Aff` / `Task<Fin<T>>` advice as C#-only and fell back to exceptions.
- Ports got named methods every time, because the skill's only port examples were C# `interface`s with named methods.

## With Kotlin examples (GREEN)

| Run | Ports | Infra errors | Smart constructors | `Raise<E>.` |
|---|---|---|---|---|
| 1 | `fun interface LoadFiscalDay { suspend operator fun invoke(...): Either<CloseDayError.InfrastructureError, FiscalDay> }` | `Either.catch` in adapters → `InfrastructureError` | `of` | no |
| 2 | `fun interface SignDayTotal { suspend operator fun invoke(...): InfraResult<Signature> }` | `Either.catch` in adapters | companion `invoke` | yes (`Raise<ValidationError>.required`, `.parseDate`) |
| 3 | `fun interface` + `suspend operator fun invoke` | `Either.catch` in adapters | companion `invoke` | yes |
| 4 | `fun interface` + `suspend operator fun invoke` | `Either.catch` in adapters → `InfrastructureError` | companion `invoke` | no (`either { ensure(...) }` instead) |
| 5 | `fun interface` + `suspend operator fun invoke` | `Either.catch` in adapters | companion `invoke` | yes (`Raise<ValidationError>.`) |

Runs 1 and 2 also wrote the workflow itself as a `fun interface`. That matches the skill's `PlaceOrder` example and fiscalization-service's flows-as-function-types.

Remaining gaps:

- **`of` constructor (run 1).** Not added to the skill: `of` returning `Either` is still a correct smart constructor. Companion `invoke` is a house style.
- **No `Raise<E>.` in runs 1 and 4.** Both used `either { ensure(...) }` instead, which is equally idiomatic Arrow. The skill shows `Raise<E>` as an option, not a rule.
