# ============================================================
# tests.test_parser: validation and parsing tests
# ============================================================

import pytest
from xml.etree import ElementTree as ET
from exlang import validate_xlang_minimal


# ============================================================
# Valid document tests
# ============================================================

class TestValidDocuments:
    """Test that valid EXLANG documents pass validation."""

    def test_minimal_valid_workbook(self):
        """Minimal valid workbook with one empty sheet."""
        xml = "<xworkbook><xsheet name='Test'></xsheet></xworkbook>"
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert errors == []

    def test_workbook_with_xrow(self):
        """Workbook with xrow elements."""
        xml = """
        <xworkbook>
          <xsheet name="Data">
            <xrow r="1"><xv>A</xv><xv>B</xv></xrow>
            <xrow r="2"><xv>1</xv><xv>2</xv></xrow>
          </xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert errors == []

    def test_workbook_with_xcell(self):
        """Workbook with xcell elements."""
        xml = """
        <xworkbook>
          <xsheet name="Data">
            <xcell addr="A1" v="Hello"/>
            <xcell addr="B1" v="123"/>
          </xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert errors == []

    def test_multiple_sheets(self):
        """Multiple sheets are valid."""
        xml = """
        <xworkbook>
          <xsheet name="Sheet1"></xsheet>
          <xsheet name="Sheet2"></xsheet>
          <xsheet name="Sheet3"></xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert errors == []

    def test_xcell_with_type_hints(self):
        """Type hints on xcell are valid."""
        xml = """
        <xworkbook>
          <xsheet name="Types">
            <xcell addr="A1" v="00123" t="string"/>
            <xcell addr="A2" v="123" t="number"/>
            <xcell addr="A3" v="TRUE" t="bool"/>
            <xcell addr="A4" v="2025-11-17" t="date"/>
          </xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert errors == []


# ============================================================
# Invalid document tests
# ============================================================

class TestInvalidDocuments:
    """Test that invalid EXLANG documents are rejected."""

    def test_wrong_root_tag(self):
        """Root tag must be xworkbook."""
        xml = "<workbook><xsheet name='Test'></xsheet></workbook>"
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert len(errors) == 1
        assert "Root tag must be 'xworkbook'" in errors[0]
        assert "found 'workbook'" in errors[0]

    def test_xsheet_missing_name(self):
        """xsheet must have name attribute."""
        xml = "<xworkbook><xsheet></xsheet></xworkbook>"
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert len(errors) == 1
        assert "xsheet missing required attribute 'name'" in errors[0]

    def test_xrow_missing_r(self):
        """xrow must have r attribute."""
        xml = """
        <xworkbook>
          <xsheet name="Data">
            <xrow><xv>A</xv></xrow>
          </xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert len(errors) == 1
        assert "xrow missing required attribute 'r'" in errors[0]

    def test_xcell_missing_addr(self):
        """xcell must have addr attribute."""
        xml = """
        <xworkbook>
          <xsheet name="Data">
            <xcell v="123"/>
          </xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert any("xcell missing required attribute 'addr'" in e for e in errors)

    def test_xcell_missing_v(self):
        """xcell must have v attribute."""
        xml = """
        <xworkbook>
          <xsheet name="Data">
            <xcell addr="A1"/>
          </xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert any("xcell missing required attribute 'v'" in e for e in errors)

    def test_invalid_type_hint(self):
        """Invalid type hints are rejected."""
        xml = """
        <xworkbook>
          <xsheet name="Data">
            <xcell addr="A1" v="123" t="invalid_type"/>
          </xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        assert len(errors) == 1
        assert "invalid type hint t='invalid_type'" in errors[0]

    def test_multiple_validation_errors(self):
        """Multiple errors are collected."""
        xml = """
        <xworkbook>
          <xsheet></xsheet>
          <xsheet name="Valid">
            <xrow><xv>A</xv></xrow>
            <xcell v="123"/>
          </xsheet>
        </xworkbook>
        """
        root = ET.fromstring(xml)
        errors = validate_xlang_minimal(root)
        # Should have: missing sheet name, missing xrow r, missing xcell addr
        assert len(errors) >= 3
