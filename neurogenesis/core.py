"""Small, strict contracts and numerical utilities; no optional runtime dependencies."""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Callable

class ValidationError(ValueError):
    """An input or model state is outside this release's declared contract."""


def number(value: Any, name: str, low: float = -math.inf, high: float = math.inf) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValidationError(f"{name}: expected a finite number")
    value = float(value)
    if not math.isfinite(value) or not low <= value <= high:
        raise ValidationError(f"{name}: expected [{low}, {high}], received {value}")
    return value


def integer(value: Any, name: str, low: int, high: int) -> int:
    x = number(value, name, low, high)
    if x != int(x):
        raise ValidationError(f"{name}: expected an integer")
    return int(x)


def keys(obj: Any, allowed: set[str], required: set[str] | None = None) -> None:
    if not isinstance(obj, dict) or not all(isinstance(k, str) for k in obj):
        raise ValidationError("Expected an object with string keys")
    if set(obj) - allowed:
        raise ValidationError(f"Unknown keys: {sorted(set(obj)-allowed)}")
    if (required or set()) - set(obj):
        raise ValidationError(f"Missing keys: {sorted((required or set())-set(obj))}")


def canonical(obj: Any) -> str:
    try:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except (ValueError, TypeError, RecursionError) as exc:
        raise ValidationError("Object cannot be serialized as finite JSON") from exc


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode()).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def loads(text: str) -> Any:
    try:
        obj = json.loads(text, object_pairs_hook=_pairs,
                         parse_constant=lambda s: (_ for _ in ()).throw(ValidationError(f"Invalid JSON constant: {s}")))
        canonical(obj)  # rejects exponent overflow, too
        return obj
    except (ValueError, TypeError, RecursionError) as exc:
        raise ValidationError(f"Invalid JSON: {exc}") from exc


def load_json(path: str | Path, max_bytes: int = 16_000_000) -> Any:
    p = Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > max_bytes:
        raise ValidationError("Input must be a regular, bounded-size JSON file")
    try:
        return loads(p.read_text(encoding="utf-8"))
    except UnicodeError as exc:
        raise ValidationError("JSON must be UTF-8") from exc


def write_json(path: Path, obj: Any) -> None:
    canonical(obj)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)+"\n", encoding="utf-8")


def source_identity() -> str:
    root = Path(__file__).parent
    paths = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix in {".py", ".json", ".html", ".js", ".css"} and "__pycache__" not in p.parts)
    return digest({p.relative_to(root).as_posix(): file_digest(p) for p in paths})


def mean(xs: list[float]) -> float:
    if not xs:
        raise ValidationError("An empty sample has no mean")
    return math.fsum(xs)/len(xs)


def variance(xs: list[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = mean(xs)
    return math.fsum((x-m)**2 for x in xs)/(len(xs)-1)


def rmse(a: list[float], b: list[float]) -> float:
    if not a or len(a) != len(b):
        raise ValidationError("RMSE requires non-empty equal-length arrays")
    return math.sqrt(mean([(x-y)**2 for x, y in zip(a, b)]))


def rk4(y: list[float], h: float, f: Callable[[list[float]], list[float]]) -> list[float]:
    k1 = f(y)
    k2 = f([v+h*k/2 for v, k in zip(y, k1)])
    k3 = f([v+h*k/2 for v, k in zip(y, k2)])
    k4 = f([v+h*k for v, k in zip(y, k3)])
    z = [v+h*(a+2*b+2*c+d)/6 for v, a, b, c, d in zip(y, k1, k2, k3, k4)]
    if not all(math.isfinite(x) for x in z):
        raise ValidationError("Non-finite integration state; no clipping applied")
    return z


def solve(a: list[list[float]], b: list[float], tolerance: float = 1e-12) -> list[float]:
    """Partial-pivot Gaussian elimination for small design matrices."""
    n = len(b)
    if n == 0 or len(a) != n or any(len(row) != n for row in a):
        raise ValidationError("Square matrix required")
    z = [list(row)+[v] for row, v in zip(a, b)]
    for i in range(n):
        pivot = max(range(i, n), key=lambda r: abs(z[r][i]))
        if abs(z[pivot][i]) <= tolerance:
            raise ValidationError("Rank-deficient design: parameters are not identifiable")
        z[i], z[pivot] = z[pivot], z[i]
        d = z[i][i]
        z[i] = [v/d for v in z[i]]
        for j in range(n):
            if j != i:
                d = z[j][i]
                z[j] = [x-d*y for x, y in zip(z[j], z[i])]
    return [r[-1] for r in z]


def ols(x: list[list[float]], y: list[float]) -> list[float]:
    if len(x) != len(y) or not x:
        raise ValidationError("Invalid regression arrays")
    n = len(x[0])
    if len(x) <= n or any(len(row) != n for row in x):
        raise ValidationError("Regression needs consistent rows and more samples than parameters")
    gram = [[math.fsum(row[i]*row[j] for row in x) for j in range(n)] for i in range(n)]
    rhs = [math.fsum(row[i]*v for row, v in zip(x, y)) for i in range(n)]
    return solve(gram, rhs)


def predict(x: list[list[float]], weights: list[float]) -> list[float]:
    return [math.fsum(v*w for v, w in zip(row, weights)) for row in x]


def numerical_equal(a: Any, b: Any, rtol: float = 1e-9, atol: float = 1e-12) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return math.isfinite(a) and math.isfinite(b) and math.isclose(a, b, rel_tol=rtol, abs_tol=atol)
    if type(a) is not type(b): return False
    if isinstance(a, dict): return set(a) == set(b) and all(numerical_equal(a[k], b[k], rtol, atol) for k in a)
    if isinstance(a, list): return len(a) == len(b) and all(numerical_equal(x,y,rtol,atol) for x,y in zip(a,b))
    return a == b

# SI conversion factors plus semantic dimensions; amount and concentration differ.
UNITS = {
    "V":("voltage",1.), "mV":("voltage",1e-3), "uV":("voltage",1e-6),
    "s":("time",1.), "ms":("time",1e-3), "Hz":("frequency",1.),
    "A":("current",1.), "pA":("current",1e-12), "nA":("current",1e-9),
    "F":("capacitance",1.), "pF":("capacitance",1e-12), "nF":("capacitance",1e-9),
    "S":("conductance",1.), "nS":("conductance",1e-9),
    "J":("energy",1.), "nJ":("energy",1e-9), "pJ":("energy",1e-12),
    "J/mol":("molar_energy",1.), "kJ/mol":("molar_energy",1000.),
    "mol/L":("concentration",1000.), "mmol/L":("concentration",1.),
    "mol":("amount",1.), "mmol":("amount",1e-3), "K":("temperature",1.),
    "bit":("information",1.), "1":("dimensionless",1.)
}


def convert(value: float, source: str, target: str) -> float:
    value = number(value, "quantity")
    if not isinstance(source,str) or not isinstance(target,str) or source not in UNITS or target not in UNITS:
        raise ValidationError("Unsupported unit")
    ds, fs = UNITS[source]; dt, ft = UNITS[target]
    if ds != dt:
        raise ValidationError(f"Cannot convert {source} ({ds}) into {target} ({dt})")
    return value*fs/ft
