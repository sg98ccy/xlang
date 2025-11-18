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


def parse_merge_range(addr: str) -> tuple[int, int, int, int]:
    """
    Parse a merge range address (e.g., 'A1:B1') into (start_row, start_col, end_row, end_col).
    
    Args:
        addr: Merge range in A1 notation (e.g., 'A1:B1', 'A1:D5')
    
    Returns:
        Tuple of (start_row, start_col, end_row, end_col) - all 1-based
    
    Raises:
        ValueError: If addr format is invalid
    
    Examples:
        >>> parse_merge_range('A1:B1')
        (1, 1, 1, 2)
        >>> parse_merge_range('A1:C3')
        (1, 1, 3, 3)
    """
    if ":" not in addr:
        raise ValueError(f"Merge range must contain ':', got: {addr}")
    
    parts = addr.split(":")
    if len(parts) != 2:
        raise ValueError(f"Merge range must have format 'A1:B1', got: {addr}")
    
    start_addr, end_addr = parts
    
    # Parse start cell
    match_start = re.match(r"([A-Z]+)([1-9][0-9]*)", start_addr)
    if not match_start:
        raise ValueError(f"Invalid start cell address: {start_addr}")
    start_col_letter, start_row_str = match_start.groups()
    start_row = int(start_row_str)
    start_col = col_letter_to_index(start_col_letter)
    
    # Parse end cell
    match_end = re.match(r"([A-Z]+)([1-9][0-9]*)", end_addr)
    if not match_end:
        raise ValueError(f"Invalid end cell address: {end_addr}")
    end_col_letter, end_row_str = match_end.groups()
    end_row = int(end_row_str)
    end_col = col_letter_to_index(end_col_letter)
    
    return (start_row, start_col, end_row, end_col)


def substitute_template_vars(text: str, iteration_index: int) -> str:
    """
    Substitute template variables in text with actual values.
    
    Supported variables:
        {{i}}  - 1-based iteration index (1, 2, 3, ...)
        {{i0}} - 0-based iteration index (0, 1, 2, ...)
    
    Args:
        text: Text containing template variables
        iteration_index: Current iteration (1-based)
    
    Returns:
        Text with variables substituted
    
    Examples:
        >>> substitute_template_vars("Month {{i}}", 1)
        'Month 1'
        >>> substitute_template_vars("Index {{i0}}", 1)
        'Index 0'
        >>> substitute_template_vars("Row {{i}} Col {{i0}}", 3)
        'Row 3 Col 2'
    """
    if text is None:
        return None
    
    text = str(text)
    # Substitute {{i}} with 1-based index
    text = text.replace("{{i}}", str(iteration_index))
    # Substitute {{i0}} with 0-based index
    text = text.replace("{{i0}}", str(iteration_index - 1))
    
    return text
