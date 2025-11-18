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


def parse_cell_address(addr: str) -> tuple[int, int]:
    """
    Parse Excel cell address (e.g., 'B4', 'AA10') into (row, col) 1-based indices.
    
    Args:
        addr: Cell address in A1 notation (e.g., 'B4')
    
    Returns:
        Tuple of (row_index, col_index) both 1-based
    
    Raises:
        ValueError: If address format is invalid
    
    Examples:
        >>> parse_cell_address('A1')
        (1, 1)
        >>> parse_cell_address('B4')
        (4, 2)
        >>> parse_cell_address('AA10')
        (10, 27)
    """
    addr = addr.strip().upper()
    match = re.match(r'^([A-Z]+)(\d+)$', addr)
    
    if not match:
        raise ValueError(f"Invalid cell address format: {addr}")
    
    col_letters, row_digits = match.groups()
    row_index = int(row_digits)
    col_index = col_letter_to_index(col_letters)
    
    return (row_index, col_index)


def parse_range(from_addr: str, to_addr: str) -> tuple[int, int, int, int]:
    """
    Parse Excel range addresses into (from_row, from_col, to_row, to_col) 1-based indices.
    
    Args:
        from_addr: Starting cell address (e.g., 'B2')
        to_addr: Ending cell address (e.g., 'D10')
    
    Returns:
        Tuple of (from_row, from_col, to_row, to_col) all 1-based
    
    Raises:
        ValueError: If addresses are invalid or from > to
    
    Examples:
        >>> parse_range('B2', 'D10')
        (2, 2, 10, 4)
        >>> parse_range('A1', 'A1')
        (1, 1, 1, 1)
    """
    from_row, from_col = parse_cell_address(from_addr)
    to_row, to_col = parse_cell_address(to_addr)
    
    if from_row > to_row or from_col > to_col:
        raise ValueError(
            f"Invalid range: 'from' ({from_addr}) must be before or equal to 'to' ({to_addr})"
        )
    
    return (from_row, from_col, to_row, to_col)
