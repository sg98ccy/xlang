# XLang v1 — A Concise Domain Language for Excel Generation  
Version: 1.0 (Preview)  
Last Updated: 2025-11-17  

---

## 1. Introduction

XLang v1 is a compact, structured markup language designed to allow Large Language Models (LLMs) to generate Excel workbooks directly, without relying on verbose and brittle Python tool calls.

The purpose of XLang is to provide a middle ground between:

- Full Python code using libraries such as openpyxl, which is expressive but long  
- Raw Excel XML, which is precise but extremely verbose  
- Natural language descriptions, which are easy to write but structurally ambiguous  

XLang combines structural clarity with concise syntax, making it suitable for:

- LLM output optimisation  
- Automated Excel report generation  
- Low token overhead workbook specifications  
- Deterministic rendering into `.xlsx` files  

This repository contains:

1. A reference implementation of the XLang v1 compiler in Python  
2. Validation logic for core XLang tags  
3. Example XLang documents and their corresponding outputs  
4. Notebook examples demonstrating the full workflow  

---

## 2. Project Goals

### 2.1 Reduce token cost of structured Excel generation

Typical LLM to Excel workflows require:

1. The model to emit Python code  
2. The Python code to execute  
3. The environment to return the resulting file  

This is expensive in tokens and fragile across model versions.  
XLang directly expresses workbook structure in a concise, declarative format.

### 2.2 Provide deterministic, machine readable outputs

LLMs are significantly more reliable when instructed to output structured tags.  
XLang leverages this behaviour to produce stable workbook definitions.

### 2.3 Establish a foundation for future high level constructs

XLang v1 introduces the core data model.  
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

XLang adopts a simple hierarchical model:

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

Every valid XLang document produces a deterministic Excel file.

The compiler performs validation before generation and rejects invalid structures, which helps prevent subtle runtime issues and makes the output suitable for automated pipelines.

---

## 4. Supported Tags in Version 1

XLang v1 intentionally focuses on a small, coherent subset of tags that already cover many realistic spreadsheets.

### 4.1 `<xworkbook>`

Top level container for the entire Excel file.

Example:

```xml
<xworkbook>
  ...
</xworkbook>
```

### 4.2 `<xsheet name="...">`

Defines a sheet.  
The `name` attribute is required and should be unique across the workbook.

Example:

```xml
<xsheet name="KPI">
  ...
</xsheet>
```

### 4.3 `<xrow r="..." c="...">`

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

### 4.4 `<xv>...</xv>`

Represents a cell value within a row.  
The text content is interpreted using XLang’s type inference:

- If it begins with `=`, it is treated as a formula  
- Otherwise, it may become a number, boolean or string depending on its content  

Example:

```xml
<xrow r="2">
  <xv>North</xv><xv>120000</xv>
</xrow>
```

### 4.5 `<xcell addr="..." v="..." t="...">`

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

## 5. Installation

### 5.1 Requirements

- Python 3.10 or later  
- `openpyxl` for Excel file generation  

### 5.2 Install dependencies

```bash
pip install openpyxl
```

### 5.3 Clone the repository

```bash
git clone https://github.com/sg98ccy/xlang
cd xlang
```

---

## 6. Usage

### 6.1 Basic Python API

The core entry point is `compile_xlang_to_xlsx`, which takes an XLang string and an output path.

Example usage:

```python
from xlang import compile_xlang_to_xlsx

with open("examples/kpi_example.xlang", "r", encoding="utf8") as f:
    xlang_text = f.read()

compile_xlang_to_xlsx(xlang_text, "output/kpi_example.xlsx")
```

This generates an Excel workbook that you can open in Excel or any compatible viewer.

### 6.2 Running the demonstration notebook

The repository provides a Jupyter Notebook that:

- Introduces the XLang syntax  
- Walks through the compiler implementation step by step  
- Shows how validation and type inference work  
- Includes multiple examples with programmatic verification  

You can open it using:

```bash
jupyter lab
```

Then navigate to the notebook file in the project.

---

## 7. Examples

### 7.1 Example 1 — Simple KPI sheet

This example defines a single sheet with:

- A header row  
- Two region rows  
- A total row with a SUM formula  

XLang:

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

### 7.2 Example 2 — Multi sheet regional sales

This example stresses:

- Multiple sheets in a single workbook  
- Numeric inference for integers, floats and negatives  
- Formulas referencing cells on another sheet  

Sheets:

- `Data` holding regional values  
- `Summary` calculating total and average metrics  

### 7.3 Example 3 — Mixed types and layout

This example stresses:

- Non default starting columns using `c` on `xrow`  
- IDs that are numeric  
- Codes that must remain strings with leading zeros  
- Booleans derived from values such as `TRUE`, `FALSE` and `YES`  
- A total formula over a numeric column  

Together, these examples cover a wide range of behaviours for the basic tag set.

---

## 8. Benchmarks and Analysis

### 8.1 Compression experiment

To quantify how concise XLang is compared to traditional Python, we implemented the same workbooks in:

1. XLang v1 syntax  
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

### 8.2 Interpretation

The results indicate:

- XLang is more concise than Python code in multi row and multi sheet tabular content (as in Example 2), where regular structure aligns with XLang’s row based model  
- Python becomes more concise in irregular or override heavy cases (as in Example 3), where XLang v1 relies on repeated `xcell` assignments and loses its structural advantage  

This aligns with the design goal:

- XLang v1 already yields shorter, structured representations for many realistic reporting scenarios involving predictable tabular layouts  
- Compression weakens when structural irregularity dominates, which is expected at this early stage of the language  
- Future features such as ranges, repetition constructs, sequence placement and templates are expected to improve compression in irregular cases and recover XLang’s advantage  

These observations support the viability of XLang as a practical structured output language for LLM based Excel generation and as a meaningful testbed for research on Output Representation Optimisation.

---

## 9. Roadmap

### 9.1 Short term (v1.x)

- Add support for `xmerge` to handle merged cell regions  
- Add minimal `xstyle` for formatting (fonts, number formats, alignment)  
- Extend validation to cover more error cases and overlapping ranges  
- Create additional examples, including stress tests and edge cases  

### 9.2 Medium term (v2)

- Introduce `xseq` and `xplace` to define reusable value sequences  
- Add `xrepeat` and `xpattern` for pattern based table generation  
- Improve styling capabilities and introduce simple style presets  
- Add named cells and named ranges for more complex formulas  

### 9.3 Long term (v3)

- Develop a richer pattern language for complex dashboards  
- Introduce theme support for consistent styling  
- Add formula templates for common analytics patterns  
- Extend XLang compilation to additional backends such as HTML tables or CSV  
- Integrate with LLM fine tuning experiments focused on structured output generation  

---

## 10. Contributing

Contributions are welcome.

Please follow these guidelines:

1. Keep Python code clean, well commented and consistent with the notebook style (section dividers, clear structure).  
2. When adding new tags or behaviours, ensure:
   - Compiler changes  
   - Validation logic  
   - At least one example XLang file  
   - Basic tests or notebook verification cells  
3. Update this README and any reference documentation to describe the new features.  

You can propose larger changes via GitHub issues or pull requests.

---

## 11. License

This project is licensed under the MIT License.  
See the `LICENSE` file in the repository for full terms.

---

## 12. Contact

For bug reports or feature requests, please open an issue on GitHub.

For collaboration or research discussions related to Output Representation Optimisation and XLang, please contact the project owner through the channels listed on the repository profile.
