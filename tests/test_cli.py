"""
Tests for the CLI interface.
"""

import json
from pathlib import Path
from click.testing import CliRunner
import pytest
from exlang.cli import cli


@pytest.fixture
def runner():
    """Provide a Click CliRunner for testing."""
    return CliRunner()


@pytest.fixture
def sample_xlang_content():
    """Provide valid EXLANG content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<xworkbook>
  <xsheet name="TestSheet">
    <xrow r="1" c="A">
      <xv>Name</xv>
      <xv>Age</xv>
    </xrow>
    <xrow r="2" c="A">
      <xv>Alice</xv>
      <xv>30</xv>
    </xrow>
  </xsheet>
</xworkbook>"""


@pytest.fixture
def invalid_xlang_content():
    """Provide invalid EXLANG content for testing."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<xworkbook>
  <xsheet>
    <xrow r="1" c="A">
      <xv>Data</xv>
    </xrow>
  </xsheet>
</xworkbook>"""


# ============================================================
# Tests: compile command
# ============================================================

def test_compile_success(runner, tmp_path, sample_xlang_content):
    """Test successful compilation of EXLANG file to XLSX."""
    input_file = tmp_path / "input.xlang"
    output_file = tmp_path / "output.xlsx"
    
    input_file.write_text(sample_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["compile", str(input_file), "-o", str(output_file)])
    
    assert result.exit_code == 0
    assert output_file.exists()
    assert "Successfully compiled" in result.output


def test_compile_default_output(runner, tmp_path, sample_xlang_content):
    """Test compilation with default output path (input.xlsx)."""
    input_file = tmp_path / "test.xlang"
    input_file.write_text(sample_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["compile", str(input_file)])
    
    assert result.exit_code == 0
    expected_output = tmp_path / "test.xlsx"
    assert expected_output.exists()


def test_compile_file_not_found(runner, tmp_path):
    """Test compilation with non-existent input file."""
    non_existent = tmp_path / "missing.xlang"
    
    result = runner.invoke(cli, ["compile", str(non_existent)])
    
    assert result.exit_code == 1
    assert "Error" in result.output


def test_compile_output_exists_no_force(runner, tmp_path, sample_xlang_content):
    """Test compilation when output file exists without --force flag."""
    input_file = tmp_path / "input.xlang"
    output_file = tmp_path / "output.xlsx"
    
    input_file.write_text(sample_xlang_content, encoding="utf-8")
    output_file.write_text("existing content")
    
    result = runner.invoke(cli, ["compile", str(input_file), "-o", str(output_file)])
    
    assert result.exit_code == 2
    assert "already exists" in result.output


def test_compile_output_exists_with_force(runner, tmp_path, sample_xlang_content):
    """Test compilation with --force flag overwrites existing file."""
    input_file = tmp_path / "input.xlang"
    output_file = tmp_path / "output.xlsx"
    
    input_file.write_text(sample_xlang_content, encoding="utf-8")
    output_file.write_text("existing content")
    
    result = runner.invoke(cli, ["compile", str(input_file), "-o", str(output_file), "--force"])
    
    assert result.exit_code == 0
    assert "Successfully compiled" in result.output


def test_compile_validation_error(runner, tmp_path, invalid_xlang_content):
    """Test compilation fails with validation error."""
    input_file = tmp_path / "invalid.xlang"
    input_file.write_text(invalid_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["compile", str(input_file)])
    
    assert result.exit_code == 3
    assert "Validation error" in result.output


def test_compile_verbose_mode(runner, tmp_path, sample_xlang_content):
    """Test compilation in verbose mode shows additional information."""
    input_file = tmp_path / "input.xlang"
    input_file.write_text(sample_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["compile", str(input_file), "--verbose"])
    
    assert result.exit_code == 0
    assert "Compiling" in result.output


# ============================================================
# Tests: validate command
# ============================================================

def test_validate_single_valid_file(runner, tmp_path, sample_xlang_content):
    """Test validation of a single valid EXLANG file."""
    input_file = tmp_path / "valid.xlang"
    input_file.write_text(sample_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["validate", str(input_file)])
    
    assert result.exit_code == 0
    assert "✓" in result.output
    assert "valid" in result.output.lower()


def test_validate_single_invalid_file(runner, tmp_path, invalid_xlang_content):
    """Test validation of a single invalid EXLANG file."""
    input_file = tmp_path / "invalid.xlang"
    input_file.write_text(invalid_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["validate", str(input_file)])
    
    assert result.exit_code == 1
    assert "✗" in result.output or "Error" in result.output


def test_validate_multiple_files(runner, tmp_path, sample_xlang_content, invalid_xlang_content):
    """Test validation of multiple EXLANG files."""
    valid_file = tmp_path / "valid.xlang"
    invalid_file = tmp_path / "invalid.xlang"
    
    valid_file.write_text(sample_xlang_content, encoding="utf-8")
    invalid_file.write_text(invalid_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["validate", str(valid_file), str(invalid_file)])
    
    assert result.exit_code == 1  # At least one file is invalid
    assert "valid.xlang" in result.output
    assert "invalid.xlang" in result.output


def test_validate_json_format(runner, tmp_path, sample_xlang_content):
    """Test validation output in JSON format."""
    input_file = tmp_path / "valid.xlang"
    input_file.write_text(sample_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["validate", str(input_file), "--format", "json"])
    
    assert result.exit_code == 0
    
    # Parse JSON output
    output_data = json.loads(result.output)
    assert "results" in output_data
    assert len(output_data["results"]) == 1
    assert output_data["results"][0]["valid"] is True


def test_validate_json_format_invalid(runner, tmp_path, invalid_xlang_content):
    """Test validation output in JSON format for invalid file."""
    input_file = tmp_path / "invalid.xlang"
    input_file.write_text(invalid_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["validate", str(input_file), "--format", "json"])
    
    assert result.exit_code == 1
    
    # Parse JSON output
    output_data = json.loads(result.output)
    assert output_data["results"][0]["valid"] is False
    assert "errors" in output_data["results"][0]
    assert len(output_data["results"][0]["errors"]) > 0


def test_validate_file_not_found(runner, tmp_path):
    """Test validation with non-existent file."""
    non_existent = tmp_path / "missing.xlang"
    
    result = runner.invoke(cli, ["validate", str(non_existent)])
    
    assert result.exit_code == 2
    assert "Error" in result.output


def test_validate_verbose_mode(runner, tmp_path, sample_xlang_content):
    """Test validation in verbose mode."""
    input_file = tmp_path / "valid.xlang"
    input_file.write_text(sample_xlang_content, encoding="utf-8")
    
    result = runner.invoke(cli, ["validate", str(input_file), "--verbose"])
    
    assert result.exit_code == 0
    assert "Validating" in result.output


# ============================================================
# Tests: CLI entry point
# ============================================================

def test_cli_help(runner):
    """Test CLI displays help message."""
    result = runner.invoke(cli, ["--help"])
    
    assert result.exit_code == 0
    assert "compile" in result.output
    assert "validate" in result.output


def test_cli_version(runner):
    """Test CLI displays version information."""
    result = runner.invoke(cli, ["--version"])
    
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_compile_help(runner):
    """Test compile command displays help message."""
    result = runner.invoke(cli, ["compile", "--help"])
    
    assert result.exit_code == 0
    assert "input-file" in result.output.lower() or "INPUT_FILE" in result.output
    assert "--output" in result.output
    assert "--force" in result.output


def test_validate_help(runner):
    """Test validate command displays help message."""
    result = runner.invoke(cli, ["validate", "--help"])
    
    assert result.exit_code == 0
    assert "input-files" in result.output.lower() or "INPUT_FILES" in result.output
    assert "--format" in result.output
