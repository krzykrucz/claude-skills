"""Compile every ```kotlin block in a SKILL.md against Arrow.

Each block goes into its own package with stubs for the types it uses but
doesn't declare; `...` placeholders become TODO().

Usage: KOTLINC_CP=<compiler jars> KOTLIN_LIB=<stdlib+arrow jars> python3 check_blocks.py SKILL.md
"""
import os, re, sys, pathlib, subprocess, tempfile, textwrap

skill = pathlib.Path(sys.argv[1]).read_text()
blocks = re.findall(r"^ *```kotlin\n(.*?)^ *```", skill, re.M | re.S)

IMPORTS = """
import arrow.core.Either
import arrow.core.NonEmptyList
import arrow.core.raise.Raise
import arrow.core.raise.either
import arrow.core.raise.ensure
import java.time.Instant
import java.time.LocalDate
import java.util.UUID
"""

STUBS = {
    "ValidationError": "data class ValidationError(val message: String)",
    "OrderId": "@JvmInline value class OrderId(val value: UUID)",
    "ProductId": "@JvmInline value class ProductId(val value: String)",
    "CustomerId": "@JvmInline value class CustomerId(val value: UUID)",
    "Money": "data class Money(val value: Long) { operator fun plus(o: Money) = Money(value + o.value); operator fun times(q: Int) = Money(value * q); companion object { val ZERO = Money(0) } }",
    "PaymentRef": "@JvmInline value class PaymentRef(val value: String)",
    "RawLine": "class RawLine",
    "RawOrderLine": "class RawOrderLine",
    "Address": "class Address",
    "ValidatedLine": "data class ValidatedLine(val productId: ProductId, val quantity: Int)",
    "PricedLine": "data class PricedLine(val line: ValidatedLine, val price: Money)",
    "ValidatedOrder": "data class ValidatedOrder(val id: OrderId, val lines: List<ValidatedLine>)",
    "PricedOrder": "data class PricedOrder(val id: OrderId, val lines: List<PricedLine>, val total: Money)",
    "UnvalidatedOrder": "class UnvalidatedOrder",
    "Order": "class Order",
    "InvalidAddressException": "class InvalidAddressException : RuntimeException()",
    "PlaceOrderError": "sealed interface PlaceOrderError { data class ProductOutOfStock(val id: ProductId) : PlaceOrderError }",
    "PlaceOrderEvent": "sealed interface PlaceOrderEvent",
    "PlaceOrderCommand": "data class PlaceOrderCommand(val orderId: OrderId)",
    "PricingService": "interface PricingService",
    "OrderStatus": "enum class OrderStatus { Draft, Paid, Cancelled }",
    "CartLine": "class CartLine",
    "LockReason": "class LockReason",
    "FiscalDay": "sealed interface FiscalDay { data class Closed(val date: LocalDate, val total: Money) : FiscalDay }",
    "JdbcTemplate": "class JdbcTemplate { fun update(sql: String, vararg args: Any): Int = 0 }",
    "INSERT_CLOSED_DAY": "const val INSERT_CLOSED_DAY = \"insert ...\"",
    # chained-sandwich shell
    "State": "class State",
    "OrderPlan": "sealed interface OrderPlan",
    "ReadyToPlace": "data class ReadyToPlace(val events: List<PlaceOrderEvent>) : OrderPlan",
    "NeedsReprice": "data class NeedsReprice(val lines: List<ValidatedLine>) : OrderPlan",
    "Quote": "class Quote",
    "loadState": "suspend fun loadState(id: OrderId): Either<PlaceOrderError, State> = TODO()",
    "planOrder": "fun planOrder(state: State, command: PlaceOrderCommand): OrderPlan = TODO()",
    "persist": "suspend fun persist(events: List<PlaceOrderEvent>): Either<PlaceOrderError, Unit> = TODO()",
    "getQuote": "suspend fun getQuote(lines: List<ValidatedLine>): Either<PlaceOrderError, Quote> = TODO()",
    "applyQuote": "fun applyQuote(state: State, quote: Quote): List<PlaceOrderEvent> = TODO()",
    # composition
    "validateOrder": "suspend fun validateOrder(c: PlaceOrderCommand): Either<PlaceOrderError, ValidatedOrder> = TODO()",
    "priceOrder": "fun priceOrder(o: ValidatedOrder): Either<PlaceOrderError, PricedOrder> = TODO()",
    "sendAcknowledgment": "suspend fun sendAcknowledgment(o: PricedOrder): Either<PlaceOrderError, Unit> = TODO()",
    "createEvents": "fun createEvents(o: PricedOrder): List<PlaceOrderEvent> = TODO()",
}


def declares(block, name):
    return re.search(rf"\b(class|interface|object|fun(\s+Raise<\w+>\.)?|val)\s+{name}\b", block) is not None


def uses(block, name):
    return re.search(rf"\b{name}\b", block) is not None


def prepare(block):
    block = block.replace("{ ...; ", "{ TODO(); ")
    block = block.replace("{ ... }", "{ }")
    block = re.sub(r"= \.\.\.$", "= TODO()", block, flags=re.M)
    block = re.sub(r"^(fun placeOrder\(order: UnvalidatedOrder\): Either<PlaceOrderError, Order>)$", r"\1 = TODO()", block, flags=re.M)
    return block


def split_bad_good(block):
    if "// Bad: caller has no idea" in block:
        bad, good = block.split("// Good:")
        return [bad, "// Good:" + good]
    return [block]


work = pathlib.Path(tempfile.mkdtemp(prefix="kt-blocks-"))
files = []
n = 0
for block in blocks:
    for part in split_bad_good(prepare(textwrap.dedent(block))):
        n += 1
        stubs = []
        # resolve stubs transitively: a stub may reference other stubs
        needed = [k for k in STUBS if uses(part, k) and not declares(part, k)]
        changed = True
        while changed:
            changed = False
            text = "\n".join(STUBS[k] for k in needed)
            for k in STUBS:
                if k not in needed and uses(text, k) and not declares(part, k):
                    needed.append(k)
                    changed = True
        src = f"@file:Suppress(\"UNUSED\")\npackage block{n}\n{IMPORTS}\n" + "\n".join(STUBS[k] for k in needed) + "\n\n" + part
        f = work / f"Block{n}.kt"
        f.write_text(src)
        files.append(f)

print(f"{len(blocks)} kotlin blocks -> {len(files)} files")
res = subprocess.run(
    ["java", "-cp", os.environ["KOTLINC_CP"], "org.jetbrains.kotlin.cli.jvm.K2JVMCompiler", "-no-stdlib", "-no-reflect",
     "-cp", os.environ["KOTLIN_LIB"], "-d", str(work / "out"), *map(str, files)],
    capture_output=True, text=True,
)
print(res.stdout + res.stderr)
print("exit", res.returncode)
sys.exit(res.returncode)
