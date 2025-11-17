# ============================================================
# exlang.helpers: column and value helpers
# ============================================================

import re


def col_letter_to_index(col: str) -> int:
    """
    Convert Excel column letters (A, B, Z, AA, AB etc.)
    into a 1-based integer column index.
    """
    col = col.strip().upper()
    result = 0

    for ch in col:
        if not ("A" <= ch <= "Z"):
            raise ValueError(f"Invalid column letter: {col}")
        result = result * 26 + (ord(ch) - ord("A") + 1)

    return result


def infer_value(raw: str, type_hint: str | None = None):
    """
    Infer the correct Python type for a cell value.

    - Formulas (starting with '=') stay as strings.
    - Optional type hints control behaviour where provided.
    - Otherwise, try int, then float, else keep as string.
    """
    if raw is None:
        return None

    raw = str(raw)

    if raw.startswith("="):
        return raw

    if type_hint == "string":
        return raw

    if type_hint == "bool":
        upper = raw.strip().upper()
        if upper in {"TRUE", "YES"}:
            return True
        if upper in {"FALSE", "NO"}:
            return False
        return raw

    if type_hint == "number":
        try:
            return int(raw)
        except ValueError:
            try:
                return float(raw)
            except ValueError:
                return raw

    if type_hint == "date":
        return raw  # you can add real date parsing later

    stripped = raw.strip()
    if re.fullmatch(r"[+-]?\d+", stripped):
        try:
            return int(stripped)
        except ValueError:
            pass
    if re.fullmatch(r"[+-]?\d*\.\d+", stripped):
        try:
            return float(stripped)
        except ValueError:
            pass

    return raw
