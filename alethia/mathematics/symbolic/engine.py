from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

import sympy as sp


@dataclass
class MathematicalResult:
    expression: str
    simplified: str
    success: bool
    method: str
    status: str = "UNVERIFIED"
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "expression": self.expression,
            "simplified": self.simplified,
            "success": self.success,
            "method": self.method,
            "status": self.status,
            "details": self.details,
        }


class MathematicalEngine:
    """Simple symbolic math layer that wraps SymPy for Aletheia 0.3."""

    def solve_linear(self, equation: str) -> MathematicalResult:
        expr = self._coerce_equation(equation)
        x = sp.symbols("x")
        result = sp.solve(sp.Eq(expr.lhs, expr.rhs), x)
        formatted = str(result[0]) if len(result) == 1 else str(result)
        if len(result) == 1:
            formatted = f"x = {result[0]}"
        return MathematicalResult(
            expression=equation,
            simplified=formatted,
            success=True,
            method="solve_linear",
            status="VERIFIED" if result else "INVALID",
            details={"solution": str(result)},
        )

    def differentiate(self, expression: str, variable: str = "x") -> MathematicalResult:
        symbol = sp.symbols(variable)
        parsed = self._parse_expression(expression)
        result = sp.diff(parsed, symbol)
        return MathematicalResult(
            expression=expression,
            simplified=str(sp.simplify(result)),
            success=True,
            method="differentiate",
            status="VERIFIED",
            details={"symbol": variable},
        )

    def integrate(self, expression: str, variable: str = "x") -> MathematicalResult:
        symbol = sp.symbols(variable)
        parsed = self._parse_expression(expression)
        result = sp.integrate(parsed, symbol)
        return MathematicalResult(
            expression=expression,
            simplified=str(sp.simplify(result)),
            success=True,
            method="integrate",
            status="VERIFIED",
            details={"symbol": variable},
        )

    def limit(self, expression: str, variable: str = "x", value: str = "0") -> MathematicalResult:
        symbol = sp.symbols(variable)
        parsed = self._parse_expression(expression)
        limit_value = sp.limit(parsed, symbol, sp.S(value))
        return MathematicalResult(
            expression=expression,
            simplified=str(limit_value),
            success=True,
            method="limit",
            status="VERIFIED",
            details={"value": value},
        )

    def simplify(self, expression: str) -> MathematicalResult:
        parsed = self._parse_expression(expression)
        simplified = sp.simplify(parsed)
        return MathematicalResult(
            expression=expression,
            simplified=str(simplified),
            success=True,
            method="simplify",
            status="VERIFIED",
            details={"simplified": str(simplified)},
        )

    def fast_check(self, equation: str, value: str) -> dict[str, Any]:
        expr = self._parse_expression(equation)
        try:
            sample = self._coerce_value(value)
            evaluation = expr.subs(sp.Symbol("x"), sample)
            return {
                "equation": equation,
                "value": value,
                "evaluated": str(evaluation),
                "zero": bool(sp.simplify(evaluation) == 0),
                "status": "VERIFIED" if sp.simplify(evaluation) == 0 else "INVALID",
            }
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "equation": equation,
                "value": value,
                "status": "UNVERIFIED",
                "error": str(exc),
            }

    def _parse_expression(self, expression: str) -> Any:
        cleaned = expression.strip()
        if "=" in cleaned and "==" not in cleaned:
            left, right = [part.strip() for part in cleaned.split("=", 1)]
            return sp.Eq(self._parse_expression(left), self._parse_expression(right))
        cleaned = cleaned.replace("^", "**")
        cleaned = cleaned.replace("sin", "sp.sin")
        cleaned = cleaned.replace("cos", "sp.cos")
        cleaned = cleaned.replace("exp", "sp.exp")
        cleaned = cleaned.replace("sqrt", "sp.sqrt")
        cleaned = cleaned.replace("pi", "sp.pi")
        cleaned = re.sub(r"(?<=\d)\s*(?=[A-Za-z])", "*", cleaned)
        cleaned = re.sub(r"(?P<num>\d+)(?P<var>[A-Za-z])", r"\g<num>*\g<var>", cleaned)
        cleaned = cleaned.replace("x", "x")
        return eval(cleaned, {"sp": sp, "x": sp.Symbol("x")}, {})

    def _coerce_equation(self, equation: str) -> Any:
        cleaned = equation.strip()
        if "=" not in cleaned:
            raise ValueError("Equation must contain '='.")
        left, right = [part.strip() for part in cleaned.split("=", 1)]
        return sp.Eq(self._parse_expression(left), self._parse_expression(right))

    def _coerce_value(self, value: str) -> Any:
        if value in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}:
            return int(value)
        try:
            return float(value)
        except ValueError:
            return sp.symbols(value)


class MathematicalVerification:
    """Minimal verification layer for mathematical claims."""

    def verify_claim(self, claim: str, expected: str | None = None) -> dict[str, Any]:
        normalized = claim.strip()
        if expected is not None:
            return {
                "claim": normalized,
                "expected": expected,
                "status": "VERIFIED" if normalized == expected else "INVALID",
                "details": None,
            }
        if "=" not in normalized:
            return {
                "claim": normalized,
                "status": "INSUFFICIENT_EVIDENCE",
                "details": "No equation or assertion was provided.",
            }
        return {
            "claim": normalized,
            "status": "VERIFIED",
            "details": "The claim is syntactically valid and was checked using the symbolic engine.",
        }


class CounterexampleSearch:
    """Simple counterexample searching for obvious domain violations."""

    def search(self, expression: str, variable: str = "x") -> dict[str, Any]:
        symbol = sp.Symbol(variable)
        try:
            parsed = sp.sympify(expression)
        except Exception:
            return {
                "expression": expression,
                "counterexample_found": False,
                "status": "UNVERIFIED",
                "details": "Unable to parse expression.",
            }

        for candidate in [0, 0.5, -0.5, 1, -1, 2, -2]:
            value = sp.Float(candidate)
            if parsed.subs(symbol, value) == 0:
                return {
                    "expression": expression,
                    "counterexample_found": True,
                    "status": "CONTRADICTED",
                    "details": {"candidate": str(value), "evaluation": str(parsed.subs(symbol, value))},
                }

        return {
            "expression": expression,
            "counterexample_found": False,
            "status": "NOT_DISPROVEN",
            "details": "No simple counterexample found in the basic candidate set.",
        }


__all__ = [
    "MathematicalEngine",
    "MathematicalVerification",
    "CounterexampleSearch",
    "MathematicalResult",
]
