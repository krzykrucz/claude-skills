# Kotlin examples for the domain-modeling-made-functional skill

**Date:** 2026-11-12
**Skill:** `plugins/engineering-practices/skills/domain-modeling-made-functional/SKILL.md`
**Style source:** fiscalization-service (Kotlin, arrow-core 1.2.1, Spring at the edges)
**Status:** Implemented in this PR

## Problem

The skill says every principle translates to Kotlin, but it shows only F# and C#. An agent designing a Kotlin workflow has nothing in Kotlin to copy, so it improvises the shell. The improvised shell works but doesn't look like a Kotlin/Arrow codebase that already follows the book.

A baseline run made this concrete. Five agents got the current skill and the same Kotlin task: close a fiscal day, where the signing service needs the computed total, so a decision needs an external call partway through. All five got the core right: sealed interfaces for states and errors, Arrow `Either`, exhaustive `when`, and two chained sandwiches around the signing call. All five drifted from the house style in the same places:

| Drift | Baseline (5 runs) |
| --- | --- |
| Infrastructure failures thrown from `suspend` ports, invisible in the shell's signature | 5 of 5 |
| Ports as interfaces with named methods (`sign`, `publish`, `load`) | 5 of 5 |
| Smart constructors named `of` / `parse` instead of a companion `operator fun invoke` | 5 of 5 |
| No `Raise<E>` step functions | 4 of 5 |

## Locked decisions

| Topic | Decision |
| --- | --- |
| Placement | Kotlin goes inline, right after each existing C# example. No separate `kotlin.md` reference file. |
| Coverage | Every section with a C# example gets a Kotlin one. Sections with only prose or pseudo-signatures stay as they are. |
| Library | Arrow (`arrow-core` 1.2): `Either`, `either { }`, `bind()`, `ensure`, `raise`, `Raise<E>`, `NonEmptyList`. Arrow plays the role LanguageExt plays for C#. |
| Sum types | `sealed interface` with nested `data class` / `data object` cases; shared fields declared on the interface and `override`n. |
| Wrapped primitives | `@JvmInline value class`. Validated ones get a `private constructor` and a companion `operator fun invoke(raw): Either<ValidationError, T>`. |
| Workflow signature | `fun interface` with `suspend operator fun invoke(command): Either<Error, List<Event>>`. `suspend` stands in for `Aff`. |
| Ports | `fun interface` with `suspend operator fun invoke`, returning `Either<InfrastructureError, T>`. |
| Infrastructure errors | Kotlin has no `Aff`, so adapters catch with `Either.catch { }` and map to an `InfrastructureError` case. That case lives in the shell's error type, never in a pure domain function's error type. |
| Composition | `either { }` with `.bind()` per step, mirroring the C# LINQ block. `Raise<E>` extension functions shown as the alternative. |
| Exhaustiveness | Kotlin's `when` over a sealed type or enum is a compile error when a case is missing. The Kotlin hole is `else`, so the example lists the cases, grouping shared results. |
| Description | Add "Kotlin with Arrow" to the trigger list. The description was at 1023 of 1024 characters, so "the functional rendering of domain-driven design" becomes "functional domain-driven design" and "records and" is dropped from the C# entry. |
| Not added | No guidance on `kotlin.Result` or on `data class` `copy()` bypassing a private constructor. No baseline run did either, so there's nothing to fix. |

## Idioms taken from fiscalization-service

| Idiom | Where it appears there |
| --- | --- |
| `sealed interface` errors with nested `data class` / `data object` | `FiscalizationError`, `SigningResult`, `FiscalizationFailure` |
| Companion `operator fun invoke` smart constructor over a private constructor | `FiscalNumber`, `FiscalEventCountry` |
| `@JvmInline value class` wrappers | `ClassificationCode`, `Token`, `CryptoPublicKey` |
| `either { }` with `bind()`, `ensure`, `raise` | `SigningDomainService`, `DomainService`, `AtFiscalizationService` |
| `Raise<E>.` step functions | `Raise<ValidationError>.convertToDomain`, `Raise<TssFailure>.handleResponse` |
| `fun interface` port with `suspend operator fun invoke` returning `Either` | `CreateInvoiceInTSS`, `CashBalanceReadRepository` |
| Flow as a class implementing a function type | `FiscalizeTransactionFlow : (ActiveAccount, BusinessTransaction, …) -> Either<…>` |
| Exhaustive `when` listing grouped cases, no `else` | `is Dk, is Nf525, is Generic, is External, is Norwegian ->` in `FiscalizeTransactionFlow` |
| Read, pure decide, write in every service method | `DomainService` KDoc: I/O port, then in-memory flow, then I/O port |

## Verification

- Each Kotlin block compiles with Kotlin 2.3 and arrow-core 1.2.1, in its own package with stubs for referenced types and `...` placeholders filled in.
- `EmailAddress("...")` called from outside the class resolves to the companion `invoke`, not the private constructor, and returns `Right` or `Left` as expected.
- The baseline task is rerun with the edited skill, five times, and scored on the drifts above.
