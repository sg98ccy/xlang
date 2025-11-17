# EXLang v1 — A Concise Domain Language for Excel Generation  
Version: 1.0 (Preview)  
Last Updated: 2025-11-17  

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

EXLang v1 intentionally focuses on a small, coherent subset of tags that already cover many realistic spreadsheets. For the complete grammar, see [`docs/GRAMMAR.md`](docs/GRAMMAR.md).

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
The `name` attribute is required and should be unique across the workbook.

Example:

```xml
<xsheet name="KPI">
  ...
</xsheet>
```

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

---

## 9. Examples

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

### 9.2 Example 2 — Multi sheet regional sales

This example stresses:

- Multiple sheets in a single workbook  
- Numeric inference for integers, floats and negatives  
- Formulas referencing cells on another sheet  

Sheets:

- `Data` holding regional values  
- `Summary` calculating total and average metrics  

### 9.3 Example 3 — Mixed types and layout

This example stresses:

- Non default starting columns using `c` on `xrow`  
- IDs that are numeric  
- Codes that must remain strings with leading zeros  
- Booleans derived from values such as `TRUE`, `FALSE` and `YES`  
- A total formula over a numeric column  

Together, these examples cover a wide range of behaviours for the basic tag set.

---

## 10. Benchmarks and Analysis

### 10.1 Compression experiment

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

### 10.2 Interpretation

The results indicate:

- EXLang is more concise than Python code in multi row and multi sheet tabular content (as in Example 2), where regular structure aligns with EXLang's row based model  
- Python becomes more concise in irregular or override heavy cases (as in Example 3), where EXLang v1 relies on repeated `xcell` assignments and loses its structural advantage

This aligns with the design goal:

- EXLang v1 already yields shorter, structured representations for many realistic reporting scenarios involving predictable tabular layouts  
- Compression weakens when structural irregularity dominates, which is expected at this early stage of the language  
- Future features such as ranges, repetition constructs, sequence placement and templates are expected to improve compression in irregular cases and recover EXLang's advantage  

These observations support the viability of EXLang as a practical structured output language for LLM based Excel generation and as a meaningful testbed for research on Output Representation Optimisation.

---

## 11. Roadmap

### 11.1 Short term (v1.x)

- Add support for `xmerge` to handle merged cell regions  
- Add minimal `xstyle` for formatting (fonts, number formats, alignment)  
- Extend validation to cover more error cases and overlapping ranges  
- Create additional examples, including stress tests and edge cases  

### 11.2 Medium term (v2)

- Introduce `xseq` and `xplace` to define reusable value sequences  
- Add `xrepeat` and `xpattern` for pattern based table generation  
- Improve styling capabilities and introduce simple style presets  
- Add named cells and named ranges for more complex formulas  

### 11.3 Long term (v3)

- Develop a richer pattern language for complex dashboards  
- Introduce theme support for consistent styling  
- Add formula templates for common analytics patterns  
- Extend XLang compilation to additional backends such as HTML tables or CSV  
- Integrate with LLM fine tuning experiments focused on structured output generation  

---

## 12. Contributing

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

## 13. License

This project is licensed under the MIT License.  
See the `LICENSE` file in the repository for full terms.

---

## 14. Contact

For bug reports or feature requests, please open an issue on GitHub.

For collaboration or research discussions related to Output Representation Optimisation and EXLang, please contact the project owner through the channels listed on the repository profile.
