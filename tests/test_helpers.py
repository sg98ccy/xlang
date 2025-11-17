# ============================================================
# tests.test_helpers: unit tests for helper functions
# ============================================================

import pytest
from exlang import col_letter_to_index, infer_value


# ============================================================
# Column letter to index conversion tests
# ============================================================

class TestColLetterToIndex:
    """Test Excel column letter to numeric index conversion."""

    @pytest.mark.parametrize("col,expected", [
        ("A", 1),
        ("B", 2),
        ("C", 3),
        ("Z", 26),
        ("AA", 27),
        ("AB", 28),
        ("AZ", 52),
        ("BA", 53),
        ("ZZ", 702),
        ("AAA", 703),
    ])
    def test_valid_columns(self, col, expected):
        """Valid column letters convert correctly."""
        assert col_letter_to_index(col) == expected

    def test_lowercase_handled(self):
        """Lowercase letters are converted correctly."""
        assert col_letter_to_index("a") == 1
        assert col_letter_to_index("aa") == 27
        assert col_letter_to_index("zz") == 702

    def test_whitespace_stripped(self):
        """Leading/trailing whitespace is ignored."""
        assert col_letter_to_index(" A ") == 1
        assert col_letter_to_index("\tAA\n") == 27

    def test_invalid_characters(self):
        """Non-letter characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid column letter"):
            col_letter_to_index("A1")
        with pytest.raises(ValueError, match="Invalid column letter"):
            col_letter_to_index("1A")
        with pytest.raises(ValueError, match="Invalid column letter"):
            col_letter_to_index("A-B")


# ============================================================
# Value inference tests
# ============================================================

class TestInferValue:
    """Test automatic type inference for cell values."""

    def test_formula_preserved(self):
        """Formulas starting with = are kept as strings."""
        assert infer_value("=SUM(A1:A5)") == "=SUM(A1:A5)"
        assert infer_value("=AVERAGE(B2:B10)") == "=AVERAGE(B2:B10)"
        assert infer_value("=Data!A1+10") == "=Data!A1+10"

    def test_integer_inference(self):
        """Integer-like strings become int."""
        assert infer_value("123") == 123
        assert isinstance(infer_value("123"), int)
        assert infer_value("0") == 0
        assert infer_value("-456") == -456

    def test_float_inference(self):
        """Float-like strings become float."""
        assert infer_value("123.45") == 123.45
        assert isinstance(infer_value("123.45"), float)
        assert infer_value("-123.45") == -123.45
        assert infer_value("0.5") == 0.5

    def test_string_fallback(self):
        """Non-numeric strings remain strings."""
        assert infer_value("Hello") == "Hello"
        assert infer_value("Region") == "Region"
        assert infer_value("N/A") == "N/A"

    def test_type_hint_string(self):
        """Type hint 'string' preserves leading zeros."""
        assert infer_value("00123", "string") == "00123"
        assert isinstance(infer_value("00123", "string"), str)
        assert infer_value("007", "string") == "007"

    def test_type_hint_number(self):
        """Type hint 'number' forces numeric conversion."""
        assert infer_value("123", "number") == 123
        assert infer_value("123.45", "number") == 123.45
        # Non-numeric strings fall back to original
        assert infer_value("abc", "number") == "abc"

    def test_type_hint_bool(self):
        """Type hint 'bool' converts TRUE/FALSE/YES/NO."""
        assert infer_value("TRUE", "bool") is True
        assert infer_value("True", "bool") is True
        assert infer_value("YES", "bool") is True
        assert infer_value("FALSE", "bool") is False
        assert infer_value("false", "bool") is False
        assert infer_value("NO", "bool") is False
        # Ambiguous values fall back
        assert infer_value("maybe", "bool") == "maybe"

    def test_type_hint_date(self):
        """Type hint 'date' keeps value as string (parsing not yet implemented)."""
        assert infer_value("2025-11-17", "date") == "2025-11-17"

    def test_none_value(self):
        """None input returns None."""
        assert infer_value(None) is None

    def test_empty_string(self):
        """Empty string remains empty string."""
        assert infer_value("") == ""
