# ============================================================
# exlang.io_utils: file I/O utilities for CLI
# ============================================================

from pathlib import Path
from xml.etree import ElementTree as ET

from .compiler import compile_xlang_to_xlsx
from .validator import validate_xlang_minimal


def read_xlang_file(path: str | Path) -> str:
    """
    Read EXLANG file with UTF-8 encoding.
    
    Args:
        path: Path to .xlang file
    
    Returns:
        File contents as string
    
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file isn't valid UTF-8
    """
    path = Path(path)
    return path.read_text(encoding='utf-8')


def compile_file(input_path: str | Path, output_path: str | Path) -> None:
    """
    Compile EXLANG file to Excel workbook.
    
    Args:
        input_path: Path to .xlang input file
        output_path: Path for output .xlsx file
    
    Raises:
        FileNotFoundError: Input file not found
        ValueError: Invalid EXLANG syntax or validation errors
        ET.ParseError: Malformed XML
    """
    xlang_text = read_xlang_file(input_path)
    compile_xlang_to_xlsx(xlang_text, output_path)


def validate_file(path: str | Path) -> tuple[bool, list[str]]:
    """
    Validate EXLANG file syntax and structure.
    
    Args:
        path: Path to .xlang file
    
    Returns:
        Tuple of (is_valid, error_list)
        - is_valid: True if file is valid EXLANG
        - error_list: List of error messages (empty if valid)
    
    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file isn't valid UTF-8
    """
    xlang_text = read_xlang_file(path)
    
    try:
        root = ET.fromstring(xlang_text)
        errors = validate_xlang_minimal(root)
        return (len(errors) == 0, errors)
    except ET.ParseError as e:
        return (False, [f"XML Parse Error: {str(e)}"])
