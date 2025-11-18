# EXLang v1 — A Concise Domain Language for Excel Generation  
Version: 1.0 (Preview)  
Last Updated: 2025-11-18  

---

## 1. Introduction

EXLang v1 is a compact, structured markup language designed to allow Large Language Models (LLMs) to generate Excel workbooks directly, without relying on verbose and brittle Python tool calls.

The purpose of EXLang is to provide a middle ground between:

- Full Python code using libraries such as openpyxl, which is expressive but long  
- Raw Excel XML, which is precise but extremely verbose  
- Natural language descriptions, which are easy to write but structurally ambiguous  

EXLang combines structural clarity with concise syntax, making it suitable for:

- LLM output optimisation  
- Automated Excel report generation  
- Low token overhead workbook specifications  
- Deterministic rendering into `.xlsx` files  

This repository contains:

1. A reference implementation of the EXLang v1 compiler in Python  
2. Validation logic for core EXLang tags  
3. Example EXLang documents and their corresponding outputs  
4. Notebook examples demonstrating the full workflow  

### Project Structure

```
exlang/
├── src/exlang/          # Single source of truth (Python package)
│   ├── __init__.py      # Public API exports
│   ├── compiler.py      # compile_xlang_to_xlsx()
│   ├── validator.py     # validate_xlang_minimal()
│   └── helpers.py       # col_letter_to_index(), infer_value()
├── notebook/
│   └── main.ipynb       # Interactive demonstrations
├── tests/               # Automated test suite (97% coverage)
├── docs/
│   └── GRAMMAR.md       # Formal language specification
├── output/              # Generated Excel files
├── pyproject.toml       # Package definition
└── README.md
```

**Design principle**: `src/exlang/` contains the implementation with separated concerns (compiler, validator, helpers). The notebook imports from this package for interactive exploration and testing.  

**Formal specification**: See [`docs/GRAMMAR.md`](docs/GRAMMAR.md) for the complete EBNF grammar, type system, and semantic rules.  

---

## 2. Project Goals

### 2.1 Reduce token cost of structured Excel generation

Typical LLM to Excel workflows require:

1. The model to emit Python code  
2. The Python code to execute  
3. The environment to return the resulting file  

This is expensive in tokens and fragile across model versions.  
EXLang directly expresses workbook structure in a concise, declarative format.

### 2.2 Provide deterministic, machine readable outputs

LLMs are significantly more reliable when instructed to output structured tags.  
EXLang leverages this behaviour to produce stable workbook definitions.

### 2.3 Establish a foundation for future high level constructs

EXLang v1 introduces the core data model.  
Future versions will add, for example:

- `xmerge` for merged cells  
- `xstyle` for styling  
- `xseq` and `xplace` for reusable sequences  
- `xrepeat` for pattern based repetition  
- Range level templates for common layouts  

These higher level constructs are intended to achieve stronger compression and better alignment with real world reporting needs.

---

## 3. Core Concepts

### 3.1 Workbook structure

EXLang adopts a simple hierarchical model:

- `<xworkbook>`  
  - `<xsheet>`  
    - `<xrow>`  
      - `<xv>`  
    - `<xcell>`  

This mirrors Excel’s conceptual structure while remaining token efficient and easy to parse.

### 3.2 Values and type inference

The compiler includes a type inference system:

- Values starting with `=` are treated as formulas  
- Numeric strings are converted to `int` or `float` where appropriate  
- Boolean like values such as `TRUE` or `FALSE` can be auto cast  
- Leading zero strings can be preserved using explicit type hints  

Type hints (for example `t="number"` or `t="string"`) allow you to override automatic inference when necessary.

### 3.3 Deterministic rendering

Every valid EXLang document produces a deterministic Excel file.

The compiler performs validation before generation and rejects invalid structures, which helps prevent subtle runtime issues and makes the output suitable for automated pipelines.

---

## 4. Language Specification

For the complete formal grammar, type system, validation rules, and semantic definitions, see:

**[`docs/GRAMMAR.md`](docs/GRAMMAR.md)** — EXLang v1 Formal Grammar Specification

The specification includes:
- EBNF grammar definition
- Type inference algorithm
- Validation rules and error taxonomy
- Compilation semantics
- Railroad syntax diagrams
- Conformance requirements

---

## 5. Supported Tags in Version 1

EXLang v1 supports **9 essential tags** covering data placement, pattern generation, and formatting. This minimal set enables real-world Excel generation while maintaining token efficiency.

### Tag Overview

| Tag | Purpose | Key Attributes |
|-----|---------|----------------|
| `<xworkbook>` | Root container | — |
| `<xsheet>` | Worksheet definition | `name` (optional) |
| `<xrow>` | Row-based placement | `r` (row), `c` (column, default "A") |
| `<xv>` | Cell value | — |
| `<xcell>` | Direct cell assignment | `addr`, `v`, `t` (optional) |
| `<xrange>` | Fill rectangular range | `from`, `to`, `fill`, `t` (optional) |
| `<xrepeat>` | Pattern generation | `times`, `r`, `c`, `direction` |
| `<xmerge>` | Merge cells | `addr` (range) |
| `<xstyle>` | Font formatting | `addr`, `bold`, `italic`, `underline` |

**Processing order:** xrow → xrange → xrepeat → xcell → xmerge → xstyle (last write wins)

For complete grammar and semantics, see [`docs/GRAMMAR.md`](docs/GRAMMAR.md).

---

### 5.1 `<xworkbook>`

Top level container for the entire Excel file.

Example:

```xml
<xworkbook>
  ...
</xworkbook>
```

### 5.2 `<xsheet name="...">`

Defines a sheet.  
The `name` attribute is optional. If omitted, sheets are auto-named as "Sheet1", "Sheet2", "Sheet3", etc.  
Explicit names should be unique across the workbook.

Example with explicit name:

```xml
<xsheet name="KPI">
  ...
</xsheet>
```

Example with auto-naming:

```xml
<xsheet>
  <!-- Auto-named as "Sheet1" -->
  ...
</xsheet>
<xsheet>
  <!-- Auto-named as "Sheet2" -->
  ...
</xsheet>
```

**Auto-naming rules:**

- Unnamed sheets receive sequential names starting from "Sheet1"
- Auto-generated names must not conflict with explicitly named sheets
- If a conflict exists (e.g., unnamed sheet would be "Sheet1" but an explicit `name="Sheet1"` exists), compilation fails with a validation error
- Auto-numbering is independent of explicit names

### 5.3 `<xrow r="..." c="...">`

Specifies a row of values.  
Attributes:

- `r`: row index (required, 1 based)  
- `c`: starting column letter (optional, default `A`)  

Values are specified by nested `<xv>` tags and are written across columns from the starting column.

Example:

```xml
<xrow r="1" c="A">
  <xv>Region</xv><xv>Sales</xv>
</xrow>
```

### 5.4 `<xv>...</xv>`

Represents a cell value within a row.  
The text content is interpreted using EXLang's type inference:

- If it begins with `=`, it is treated as a formula  
- Otherwise, it may become a number, boolean or string depending on its content  

Example:

```xml
<xrow r="2">
  <xv>North</xv><xv>120000</xv>
</xrow>
```

### 5.5 `<xcell addr="..." v="..." t="...">`

Explicit single cell assignment.  
Attributes:

- `addr`: Excel cell address in A1 notation (required)  
- `v`: value or formula (required)  
- `t`: optional type hint (`string`, `number`, `bool`, `date`)  

Example:

```xml
<xcell addr="B4" v="=SUM(B2:B3)"/>
```

Type hints allow you to enforce interpretations such as preserving leading zeros or enforcing booleans.

### 5.6 `<xrange from="..." to="..." fill="..." t="...">`

Fill a rectangular range of cells with the same value.  
Attributes:

- `from`: top-left cell address in A1 notation (required)  
- `to`: bottom-right cell address in A1 notation (required)  
- `fill`: value to place in all cells (required)  
- `t`: optional type hint (`string`, `number`, `bool`, `date`)  

Example:

```xml
<xrange from="B2" to="B50" fill="0"/>
```

This fills cells B2 through B50 (inclusive) with the integer value 0.

**Range behaviour:**

- Both `from` and `to` are inclusive
- `from` must be before or equal to `to` (both row and column)
- Single-cell ranges (`from = to`) are valid
- Type inference applies to the `fill` value
- Can be used to initialise large areas efficiently (reduces token count)

**Compression benefits:**

Traditional approach using `<xcell>` for 50 cells:
```xml
<xcell addr="B2" v="0"/>
<xcell addr="B3" v="0"/>
<!-- ... 46 more lines ... -->
<xcell addr="B50" v="0"/>
```

Equivalent using `<xrange>` (single line):
```xml
<xrange from="B2" to="B50" fill="0"/>
```

This achieves approximately 50× token reduction for sparse/irregular layouts.

### 5.7 `<xrepeat times="..." r="..." c="..." direction="...">`

Generate repetitions of template content with iteration variables.  
Attributes:

- `times`: number of repetitions (required, must be ≥ 1)  
- `r`: starting row (optional, defaults to `"1"`)  
- `c`: starting column (optional, defaults to `"A"`)  
- `direction`: iteration direction (optional, defaults to `"down"`)  
  - `"down"`: each iteration moves to the next row  
  - `"right"`: each iteration moves to the next column  

**Template variables:**

- `{{i}}`: 1-based iteration index (1, 2, 3, ...)  
- `{{i0}}`: 0-based iteration index (0, 1, 2, ...)  

**Content constraints:**

- `<xrepeat>` can only contain `<xv>` elements  
- Nested `<xrepeat>` elements are not allowed  
- Each `<xv>` defines a cell value in the template  

**Example (direction=down, default):**

```xml
<xrepeat times="12" r="2" c="A">
  <xv>Month {{i}}</xv>
  <xv>0</xv>
</xrepeat>
```

This generates:
- A2="Month 1", B2=0  
- A3="Month 2", B3=0  
- A4="Month 3", B4=0  
- ... through A13="Month 12", B13=0  

**Example (direction=right):**

```xml
<xrepeat times="4" r="1" c="B" direction="right">
  <xv>Q{{i}}</xv>
  <xv>0</xv>
</xrepeat>
```

This generates:
- B1="Q1", B2=0  
- C1="Q2", C2=0  
- D1="Q3", D2=0  
- E1="Q4", E2=0  

**Compression benefits:**

Traditional approach using `<xrow>` for 12 months:
```xml
<xrow r="2" c="A"><xv>Month 1</xv><xv>0</xv></xrow>
<xrow r="3" c="A"><xv>Month 2</xv><xv>0</xv></xrow>
<xrow r="4" c="A"><xv>Month 3</xv><xv>0</xv></xrow>
<!-- ... 9 more lines ... -->
<xrow r="13" c="A"><xv>Month 12</xv><xv>0</xv></xrow>
```

Equivalent using `<xrepeat>` (single element):
```xml
<xrepeat times="12" r="2" c="A">
  <xv>Month {{i}}</xv>
  <xv>0</xv>
</xrepeat>
```

This achieves approximately **12× token reduction** for templated table structures, demonstrating Output Representation Optimisation (ORO) for pattern-based data. The compression factor scales linearly with the repetition count: `times="100"` achieves 100× compression.

### 5.8 `<xmerge addr="...">`

Merge multiple cells into a single merged cell for headers and titles.  
Attributes:

- `addr`: Merge range in A1 notation (required, format: `"A1:B1"`)  

**Behaviour:**

- Combines cells in specified range into single merged cell  
- Displays only the value from the top-left cell  
- Range must use colon notation: `start_cell:end_cell`  
- Multiple non-overlapping merges allowed in same sheet  

**Example (horizontal merge):**

```xml
<xcell addr="A1" v="2024 Budget Report"/>
<xmerge addr="A1:D1"/>
```

This merges cells A1, B1, C1, and D1, displaying "2024 Budget Report" across the merged area.

**Example (vertical merge):**

```xml
<xcell addr="A1" v="Category"/>
<xmerge addr="A1:A3"/>
```

**Example (rectangular merge):**

```xml
<xcell addr="A1" v="Title Block"/>
<xmerge addr="A1:C2"/>
```

**Real-world use case:**

```xml
<xsheet name="Report">
  <xcell addr="A1" v="Q4 Financial Summary"/>
  <xmerge addr="A1:E1"/>
  <xrow r="2" c="A"><xv>Month</xv><xv>Revenue</xv><xv>Costs</xv><xv>Profit</xv><xv>Margin</xv></xrow>
</xsheet>
```

### 5.9 `<xstyle addr="..." bold="..." italic="..." underline="...">`

Apply font formatting to single cells or ranges.  
Attributes:

- `addr`: Cell address or range in A1 notation (required)  
- `bold`: Apply bold formatting (optional, `"true"` or `"false"`)  
- `italic`: Apply italic formatting (optional, `"true"` or `"false"`)  
- `underline`: Apply underline formatting (optional, `"true"` or `"false"`)  

**Behaviour:**

- Applies to single cell (e.g., `"A1"`) or range (e.g., `"A1:C1"`)  
- Range notation applies styling to all cells in range  
- Multiple xstyle tags on same cell: last write wins  
- Boolean values must be strings: `"true"` or `"false"`  

**Example (single cell, bold):**

```xml
<xcell addr="A1" v="Header"/>
<xstyle addr="A1" bold="true"/>
```

**Example (range, multiple attributes):**

```xml
<xrow r="1" c="A"><xv>Column 1</xv><xv>Column 2</xv><xv>Column 3</xv></xrow>
<xstyle addr="A1:C1" bold="true" italic="true"/>
```

This applies bold and italic to all three header cells.

**Example (combining merge and style):**

```xml
<xcell addr="A1" v="Report Title"/>
<xmerge addr="A1:D1"/>
<xstyle addr="A1" bold="true" underline="true"/>
```

**Real-world table example:**

```xml
<xsheet name="Budget">
  <!-- Title row: merged and styled -->
  <xcell addr="A1" v="2024 Monthly Budget"/>
  <xmerge addr="A1:D1"/>
  <xstyle addr="A1" bold="true"/>
  
  <!-- Header row: styled -->
  <xrow r="2" c="A"><xv>Month</xv><xv>Income</xv><xv>Expenses</xv><xv>Savings</xv></xrow>
  <xstyle addr="A2:D2" bold="true" italic="true"/>
  
  <!-- Data rows using xrepeat -->
  <xrepeat times="12" r="3" c="A">
    <xv>Month {{i}}</xv>
    <xv>0</xv>
    <xv>0</xv>
    <xv>=B{{i+2}}-C{{i+2}}</xv>
  </xrepeat>
</xsheet>
```

**Why xmerge and xstyle matter:**

Real-world Excel documents always include basic formatting. Without merge and style capabilities, EXLang would be limited to raw data entry, making it impractical for actual use. These tags complete the language for production scenarios while maintaining the minimalist design philosophy.

---

## 6. Installation

### 6.1 Requirements

- Python 3.10 or later  
- `openpyxl` for Excel file generation  

### 6.2 Clone the repository

```bash
git clone https://github.com/sg98ccy/exlang
cd exlang
```

### 6.3 Install the package

Install in editable mode to make the `exlang` package available:

```bash
pip install -e .
```

This installs the package from `src/exlang/` and makes it importable from any Python environment or notebook.

### 6.4 Install development dependencies (optional)

For running tests and coverage analysis:

```bash
pip install -e .[dev]
```

This installs pytest and pytest-cov along with the package.

---

## 7. Testing

EXLang includes a comprehensive automated test suite for research reproducibility.

### 7.1 Run all tests

```bash
pytest tests/ -v
```

### 7.2 Run tests with coverage report

```bash
pytest tests/ --cov=src/exlang --cov-report=term-missing
```

### 7.3 Run tests with HTML coverage report

```bash
pytest tests/ --cov=src/exlang --cov-report=html
```

This generates an HTML report in `htmlcov/index.html`.

### 7.4 Test suite structure

The test suite covers:

- **test_helpers.py**: Utility function unit tests (column conversion, type inference)
- **test_parser.py**: XML validation tests (valid and invalid documents)
- **test_compiler.py**: Compilation correctness (value types, formulas, multi-sheet)
- **test_roundtrip.py**: End-to-end semantic preservation (EXLANG → Excel → verify)
- **test_errors.py**: Error handling and edge cases

Current coverage: **97%+** across all core modules.

---

## 8. Command-Line Interface (CLI)

EXLang provides a command-line tool for compiling and validating `.xlang` files without writing Python code.

### 8.1 Installation

After installing the package with `pip install -e .`, the `exlang` command becomes available:

```bash
exlang --version
exlang --help
```

### 8.2 Compile Command

Compile an EXLANG file to Excel format:

```bash
exlang compile input.xlang
```

This creates `input.xlsx` in the same directory.

**Options:**

- `-o, --output PATH`: Specify output path (default: replaces `.xlang` with `.xlsx`)
- `-f, --force`: Overwrite output file if it already exists
- `-v, --verbose`: Show detailed compilation progress

**Examples:**

```bash
# Compile to default output (input.xlsx)
exlang compile data.xlang

# Specify custom output path
exlang compile data.xlang -o output/report.xlsx

# Overwrite existing file
exlang compile data.xlang --force

# Verbose mode
exlang compile data.xlang --verbose
```

**Exit codes:**

- `0`: Success
- `1`: File not found
- `2`: Output file already exists (use `--force` to overwrite)
- `3`: Validation error in EXLANG syntax

### 8.3 Validate Command

Validate EXLANG files without compiling:

```bash
exlang validate input.xlang
```

**Options:**

- `-f, --format FORMAT`: Output format (`text` or `json`, default: `text`)
- `-v, --verbose`: Show detailed validation progress

**Examples:**

```bash
# Validate single file
exlang validate data.xlang

# Validate multiple files
exlang validate file1.xlang file2.xlang file3.xlang

# JSON output (for integration with tools)
exlang validate data.xlang --format json
```

**Exit codes:**

- `0`: All files valid
- `1`: One or more files invalid
- `2`: File not found
- `3`: Parse error (malformed XML)

**JSON output format:**

```json
{
  "results": [
    {
      "file": "data.xlang",
      "valid": true,
      "errors": []
    }
  ],
  "summary": {
    "total": 1,
    "valid": 1,
    "invalid": 0
  }
}
```

### 8.4 Shell Integration

The CLI can be used in shell scripts and build pipelines:

```bash
# Compile all EXLANG files in a directory
for file in *.xlang; do
  exlang compile "$file" -f
done

# Validate before compiling
if exlang validate data.xlang; then
  exlang compile data.xlang
  echo "Successfully compiled data.xlsx"
else
  echo "Validation failed"
  exit 1
fi

# Batch validation with JSON output
exlang validate *.xlang --format json > validation_report.json
```

---

## 9. Python API Usage

### 9.1 Basic Python API

The core entry point is `compile_xlang_to_xlsx`, which takes an EXLang string and an output path.

Example usage:

```python
from exlang import compile_xlang_to_xlsx

xlang_text = """
<xworkbook>
  <xsheet name="KPI">
    <xrow r="1"><xv>Region</xv><xv>Sales</xv></xrow>
    <xrow r="2"><xv>North</xv><xv>120000</xv></xrow>
  </xsheet>
</xworkbook>
""".strip()

compile_xlang_to_xlsx(xlang_text, "output/kpi_example.xlsx")
```

This generates an Excel workbook that you can open in Excel or any compatible viewer.

### 9.2 Available imports

```python
from exlang import compile_xlang_to_xlsx   # Main compiler
from exlang import validate_xlang_minimal  # Validator
from exlang import col_letter_to_index     # Helper: A → 1, B → 2, etc.
from exlang import infer_value             # Helper: type inference
from exlang import compile_file            # Compile .xlang file to .xlsx
from exlang import validate_file           # Validate .xlang file
from exlang import read_xlang_file         # Read .xlang file content
```

### 9.3 File-based API

For working with `.xlang` files directly:

```python
from exlang import compile_file, validate_file

# Compile a file
compile_file("input.xlang", "output.xlsx")

# Validate a file
is_valid, errors = validate_file("input.xlang")
if not is_valid:
    for error in errors:
        print(error)
```

### 9.4 Running the demonstration notebook

The repository provides a Jupyter Notebook (`notebook/main.ipynb`) that:

- Introduces the EXLang syntax  
- Demonstrates importing and using the `exlang` package  
- Shows how validation and type inference work  
- Includes multiple examples with programmatic verification  

After installing the package with `pip install -e .`, you can open the notebook:

```bash
jupyter lab notebook/main.ipynb
```

The notebook imports directly from the installed package:

```python
from exlang import compile_xlang_to_xlsx, validate_xlang_minimal
```

### Automatic XML Escaping with Jinja2

EXLang **automatically** uses Jinja2 template preprocessing to handle XML escaping in formulas. This significantly reduces token overhead and makes EXLang more LLM-friendly.

#### The XML Escaping Problem

Excel formulas often contain comparison operators (`<`, `>`, `<=`, `>=`, `<>`) and quotes (`"`), which are special characters in XML. Without escaping, these characters break XML parsing:

**Manual escaping required (verbose):**
```xml
<!-- ❌ INVALID: Breaks XML parsing -->
<xcell addr="B4" v="=IF(A4<100,"Low","High")"/>

<!-- ✓ VALID: Manual XML escaping (verbose) -->
<xcell addr="B4" v="=IF(A4&lt;100,&quot;Low&quot;,&quot;High&quot;)"/>
```

This manual escaping adds ~30% more tokens and reduces LLM reliability.

#### Jinja2 Solution: Natural Formula Syntax

With automatic Jinja2 preprocessing, you can write formulas naturally without manual escaping:

```python
from exlang import compile_xlang_to_xlsx

xlang = '''
<xworkbook>
  <xsheet name="Report">
    <xcell addr="A1" v="{{ formula }}"/>
  </xsheet>
</xworkbook>
'''

# Pass formula as template variable - Jinja2 auto-escapes XML characters automatically
compile_xlang_to_xlsx(
    xlang,
    "output/report.xlsx",
    formula='=IF(A4<100,"Low","High")'  # No manual escaping needed!
)
```

**How it works:**

1. Jinja2's `autoescape=True` automatically converts `<` → `&lt;`, `>` → `&gt;`, `"` → `&quot;`, etc.
2. Template variables (`{{ formula }}`) are substituted and escaped before XML parsing
3. The Excel file receives the correct unescaped formula: `=IF(A4<100,"Low","High")`

#### Token Efficiency Comparison

| Approach | Formula Syntax | Approx. Tokens |
|----------|---------------|----------------|
| Manual escaping | `v="=IF(A4&lt;100,&quot;Low&quot;,&quot;High&quot;)"` | ~18 |
| Jinja2 template | `formula='=IF(A4<100,"Low","High")'` | ~13 |
| **Savings** | **Natural syntax** | **~30% reduction** |

#### Advanced Jinja2 Features

**Multiple template variables:**
```python
xlang = '''
<xworkbook>
  <xsheet name="Inventory">
    <xcell addr="A1" v="{{ title }}"/>
    <xcell addr="B4" v="{{ reorder_formula }}"/>
    <xcell addr="B5" v="{{ status_formula }}"/>
  </xsheet>
</xworkbook>
'''

compile_xlang_to_xlsx(
    xlang,
    "inventory.xlsx",
    title="Weekly Inventory Report",
    reorder_formula='=IF(C4<100,"REORDER","OK")',
    status_formula='=IF(D5>E5,"OVER","UNDER")'
)
```

**Jinja2 loops for repetitive formulas:**
```python
xlang = '''
<xworkbook>
  <xsheet name="Sales">
    <xrow r="1" c="A"><xv>Product</xv><xv>Q1</xv><xv>Q2</xv><xv>Q3</xv><xv>Q4</xv><xv>Total</xv></xrow>
    {% for i in range(2, 7) %}
    <xrow r="{{ i }}" c="A">
      <xv>Product {{ i-1 }}</xv>
      <xv>{{ base_sales }}</xv>
      <xv>{{ base_sales * 1.1 }}</xv>
      <xv>{{ base_sales * 1.2 }}</xv>
      <xv>{{ base_sales * 1.3 }}</xv>
    </xrow>
    <xcell addr="F{{ i }}" v="{{ row_sum_formula.replace('ROW', i|string) }}"/>
    {% endfor %}
  </xsheet>
</xworkbook>
'''

compile_xlang_to_xlsx(
    xlang,
    "sales.xlsx",
    base_sales=10000,
    row_sum_formula='=SUM(B{ROW}:E{ROW})'
)
```

#### Writing Formulas in EXLang

| Use Case | Recommended Approach |
|----------|---------------------|
| **Formulas with `<`, `>`, `<>`, `&`** | ✓ Template variables (auto-escaping) |
| **Many similar formulas** | ✓ Jinja2 loops |
| **LLM-generated content** | ✓ Template variables (token efficiency) |
| **Simple data without formulas** | Direct values (no templates needed) |
| **Static templates** | Either approach works |

#### Backward Compatibility

Jinja2 preprocessing is **always enabled** by default. If your EXLang contains manual XML escaping (e.g., `&lt;`, `&quot;`), it will still work correctly — Jinja2 passes it through unchanged:

```python
# Manual escaping still works (backward compatible)
xlang_manual = '''
<xworkbook>
  <xsheet name="Test">
    <xcell addr="A1" v="=IF(B1&lt;100,&quot;Low&quot;,&quot;High&quot;)"/>
  </xsheet>
</xworkbook>
'''
compile_xlang_to_xlsx(xlang_manual, "output.xlsx")  # Works fine

# Template variables are cleaner and more token-efficient
xlang_template = '''
<xworkbook>
  <xsheet name="Test">
    <xcell addr="A1" v="{{ formula }}"/>
  </xsheet>
</xworkbook>
'''
compile_xlang_to_xlsx(xlang_template, "output.xlsx", 
                     formula='=IF(B1<100,"Low","High")')  # Recommended
```

Existing code with manual escaping continues to work without changes.

#### Why This Matters for ORO Research

Automatic Jinja2 integration aligns perfectly with **Output Representation Optimisation** goals:

- **~30% token reduction** for formula-heavy workbooks
- **Industry standard**: Jinja2 is used by Flask, Ansible, etc. — LLMs are already trained on this syntax
- **LLM-friendly**: Natural formula syntax reduces generation errors
- **Deterministic**: Template engine ensures consistent XML output
- **Research reproducibility**: Standard tool vs custom escaping logic
- **Always reliable**: No need to remember opt-in flags — automatic escaping is always available

**Recommendation**: Use template variables (`{{ variable }}`) when generating EXLang with formulas. The token savings and reduced error rate make it ideal for LLM output.

---

## 10. Examples

### 9.1 Example 1 — Simple KPI sheet

This example defines a single sheet with:

- A header row  
- Two region rows  
- A total row with a SUM formula  

EXLang:

```xml
<xworkbook>
  <xsheet name="KPI">
    <xrow r="1"><xv>Region</xv><xv>Sales</xv></xrow>
    <xrow r="2"><xv>North</xv><xv>120000</xv></xrow>
    <xrow r="3"><xv>South</xv><xv>98000</xv></xrow>
    <xcell addr="A4" v="Total"/>
    <xcell addr="B4" v="=SUM(B2:B3)"/>
  </xsheet>
</xworkbook>
```

### 10.2 Example 2 — Multi sheet regional sales

This example stresses:

- Multiple sheets in a single workbook  
- Numeric inference for integers, floats and negatives  
- Formulas referencing cells on another sheet  

Sheets:

- `Data` holding regional values  
- `Summary` calculating total and average metrics  

### 10.3 Example 3 — Mixed types and layout

This example stresses:

- Non default starting columns using `c` on `xrow`  
- IDs that are numeric  
- Codes that must remain strings with leading zeros  
- Booleans derived from values such as `TRUE`, `FALSE` and `YES`  
- A total formula over a numeric column  

Together, these examples cover a wide range of behaviours for the basic tag set.

---

## 11. Benchmarks and Analysis

### 11.1 Compression experiment

To quantify how concise EXLang is compared to traditional Python, we implemented the same workbooks in:

1. EXLang v1 syntax  
2. Direct Python using `openpyxl`  

We then compared character lengths as an approximate proxy for token counts.

Results:

- Example 2  
  - XLang length: 751 characters  
  - Python length: 1071 characters  
  - Python to XLang ratio: approximately 1.43  

- Example 3  
  - XLang length: 773 characters  
  - Python length: 570 characters  
  - Python to XLang ratio: approximately 0.74  

### 11.2 Interpretation

The results indicate:

- EXLang is more concise than Python code in multi row and multi sheet tabular content (as in Example 2), where regular structure aligns with EXLang's row based model  
- Python becomes more concise in irregular or override heavy cases (as in Example 3), where EXLang v1 relies on repeated `xcell` assignments and loses its structural advantage

This aligns with the design goal:

- EXLang v1 already yields shorter, structured representations for many realistic reporting scenarios involving predictable tabular layouts  
- Compression weakens when structural irregularity dominates, which is expected at this early stage of the language  
- Future features such as ranges, repetition constructs, sequence placement and templates are expected to improve compression in irregular cases and recover EXLang's advantage  

These observations support the viability of EXLang as a practical structured output language for LLM based Excel generation and as a meaningful testbed for research on Output Representation Optimisation.

---

## 12. Roadmap

### 12.1 Short term (v1.x)

- Add support for `xmerge` to handle merged cell regions  
- Add minimal `xstyle` for formatting (fonts, number formats, alignment)  
- Extend validation to cover more error cases and overlapping ranges  
- Create additional examples, including stress tests and edge cases  

### 12.2 Medium term (v2)

- Introduce `xseq` and `xplace` to define reusable value sequences  
- Add `xrepeat` and `xpattern` for pattern based table generation  
- Improve styling capabilities and introduce simple style presets  
- Add named cells and named ranges for more complex formulas  

### 12.3 Long term (v3)

- Develop a richer pattern language for complex dashboards  
- Introduce theme support for consistent styling  
- Add formula templates for common analytics patterns  
- Extend XLang compilation to additional backends such as HTML tables or CSV  
- Integrate with LLM fine tuning experiments focused on structured output generation  

---

## 13. Contributing

Contributions are welcome.

Please follow these guidelines:

1. Keep Python code clean, well commented and consistent with the notebook style (section dividers, clear structure).  
2. When adding new tags or behaviours, ensure:
   - Compiler changes  
   - Validation logic  
   - At least one example EXLang file  
   - Basic tests or notebook verification cells  
3. Update this README and any reference documentation to describe the new features.  

You can propose larger changes via GitHub issues or pull requests.

---

## 14. License

This project is licensed under the MIT License.  
See the `LICENSE` file in the repository for full terms.

---

## 15. Contact

For bug reports or feature requests, please open an issue on GitHub.

For collaboration or research discussions related to Output Representation Optimisation and EXLang, please contact the project owner through the channels listed on the repository profile.
