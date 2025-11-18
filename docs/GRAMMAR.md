# EXLang v1 Formal Grammar Specification

**Version:** 1.0  
**Date:** 2025-11-17  
**Status:** Stable  
**Authors:** Jackson Chai

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Notation and Conventions](#2-notation-and-conventions)
3. [Lexical Structure](#3-lexical-structure)
4. [Syntax Grammar (EBNF)](#4-syntax-grammar-ebnf)
5. [Type System](#5-type-system)
6. [Semantic Rules](#6-semantic-rules)
7. [Validation Rules](#7-validation-rules)
8. [Error Taxonomy](#8-error-taxonomy)
9. [Compilation Semantics](#9-compilation-semantics)
10. [Railroad Diagrams](#10-railroad-diagrams)
11. [Conformance](#11-conformance)
12. [References](#12-references)

---

## 1. Introduction

### 1.1 Purpose

EXLang (Excel Language) v1 is a domain-specific markup language designed for generating Excel workbooks through structured, token-efficient specifications. The language prioritises:

- **Determinism**: Identical input produces identical output
- **Conciseness**: Lower token overhead compared to imperative code
- **Clarity**: Human-readable structure aligned with spreadsheet semantics
- **Type safety**: Explicit type system with automatic inference

### 1.2 Design Goals

1. **Output Representation Optimisation (ORO)**: Reduce token count in LLM-generated Excel specifications
2. **Semantic alignment**: Language constructs map directly to spreadsheet concepts
3. **Formal verifiability**: Grammar enables automated validation and testing
4. **Extensibility**: Foundation for advanced features (styles, merges, patterns)

### 1.3 Scope

This specification defines EXLang v1, which supports:

- Workbook and worksheet structure
- Row-based and direct cell placement
- Value type inference and explicit type hints
- Formula preservation
- Multi-sheet workbooks with cross-sheet references

**Out of scope for v1:**
- Cell styling and formatting
- Merged cells
- Named ranges
- Charts and graphics
- Data validation

---

## 2. Notation and Conventions

### 2.1 EBNF Notation

This specification uses Extended Backus-Naur Form (EBNF) with the following conventions:

| Notation | Meaning |
|----------|---------|
| `::=` | Definition |
| `|` | Alternation (OR) |
| `( ... )` | Grouping |
| `[ ... ]` | Optional (0 or 1) |
| `{ ... }` | Repetition (0 or more) |
| `'...'` | Terminal string literal |
| `"..."` | Terminal string literal (alternative) |
| `(* ... *)` | Comment |

### 2.2 Terminology

- **Document**: A complete EXLang specification
- **Element**: An XML tag with optional attributes and content
- **Attribute**: A name-value pair within an element
- **Terminal**: A lexical token that cannot be subdivided
- **Production**: A grammar rule defining element structure

### 2.3 Character Encoding

All EXLang documents must be encoded in **UTF-8** and must be valid XML 1.0 documents.

---

## 3. Lexical Structure

### 3.1 XML Compliance

EXLang is an XML-based language. All documents must:

1. Begin with optional XML declaration: `<?xml version="1.0" encoding="UTF-8"?>`
2. Have exactly one root element (`<xworkbook>`)
3. Follow XML well-formedness rules (properly nested, closed tags)
4. Escape special characters in text content (`<`, `>`, `&`, `"`, `'`)

### 3.2 Tag Names

All EXLang tags use lowercase with `x` prefix:

```
xworkbook  xsheet  xrow  xv  xcell  xrange
```

**Rationale**: The `x` prefix prevents collision with potential future XML namespaces and clearly identifies EXLang-specific elements.

### 3.3 Attribute Names

Attribute names are lowercase ASCII:

```
name  r  c  addr  v  t
```

### 3.4 Whitespace

- Whitespace between elements is **ignored**
- Whitespace within text content is **preserved**
- Indentation is recommended for readability but has no semantic meaning

---

## 4. Syntax Grammar (EBNF)

### 4.1 Document Structure

```ebnf
(* ============================================================ *)
(* Top-level productions                                        *)
(* ============================================================ *)

Document      ::= XMLDecl? Workbook

XMLDecl       ::= '<?xml' VersionInfo EncodingDecl? '?>'
VersionInfo   ::= 'version="1.0"'
EncodingDecl  ::= 'encoding="UTF-8"'

Workbook      ::= '<xworkbook>' Sheet+ '</xworkbook>'
```

### 4.2 Sheet Structure

```ebnf
(* ============================================================ *)
(* Worksheet definition                                         *)
(* ============================================================ *)

Sheet         ::= '<xsheet' SheetName '>' SheetContent* '</xsheet>'

SheetName     ::= 'name="' Identifier '"'

SheetContent  ::= Row | Cell | Range

(* Sheet may be empty (no content) *)
```

### 4.3 Row-Based Placement

```ebnf
(* ============================================================ *)
(* Row-based value placement                                    *)
(* ============================================================ *)

Row           ::= '<xrow' RowIndex [ ColumnStart ] '>' Value+ '</xrow>'

RowIndex      ::= 'r="' PositiveInt '"'
ColumnStart   ::= 'c="' ColumnLetter '"'

Value         ::= '<xv>' TextContent '</xv>'

(* Default column start: "A" *)
(* Values placed sequentially from column start *)
```

### 4.4 Direct Cell Placement

```ebnf
(* ============================================================ *)
(* Direct cell addressing                                       *)
(* ============================================================ *)

Cell          ::= '<xcell' CellAddr CellValue [ TypeHint ] '/>'

CellAddr      ::= 'addr="' CellAddress '"'
CellValue     ::= 'v="' TextContent '"'
TypeHint      ::= 't="' TypeName '"'

(* Type hint is optional; if absent, type is inferred *)
```

### 4.5 Range Fill

```ebnf
(* ============================================================ *)
(* Range fill for rectangular cell areas                        *)
(* ============================================================ *)

Range         ::= '<xrange' FromAddr ToAddr FillValue [ TypeHint ] '/>'

FromAddr      ::= 'from="' CellAddress '"'
ToAddr        ::= 'to="' CellAddress '"'
FillValue     ::= 'fill="' TextContent '"'

(* Fills all cells in rectangular range [from, to] with fill value *)
(* from must be ≤ to (both row and column) *)
(* Type hint applies to fill value inference *)
```

### 4.6 Terminal Definitions

```ebnf
(* ============================================================ *)
(* Lexical terminals                                            *)
(* ============================================================ *)

Identifier    ::= [A-Za-z0-9_-]+
                  (* Sheet names, allows letters, digits, underscore, hyphen *)

PositiveInt   ::= [1-9] [0-9]*
                  (* 1-based row index: 1, 2, 3, ... *)

ColumnLetter  ::= [A-Z]+
                  (* Excel column: A, B, ..., Z, AA, AB, ..., ZZ, AAA, ... *)

CellAddress   ::= ColumnLetter PositiveInt
                  (* A1 notation: A1, B2, Z26, AA1, etc. *)

TypeName      ::= 'string' | 'number' | 'bool' | 'date'
                  (* Allowed type hints *)

TextContent   ::= XMLChar*
                  (* Any valid XML character sequence *)

XMLChar       ::= <any Unicode character except XML special chars>
                  (* Must escape: < > & " ' *)
```

### 4.7 Grammar Summary

Complete grammar in condensed form:

```ebnf
Document      ::= XMLDecl? Workbook
Workbook      ::= '<xworkbook>' Sheet+ '</xworkbook>'
Sheet         ::= '<xsheet' 'name="' Identifier '"' '>' ( Row | Cell | Range )* '</xsheet>'
Row           ::= '<xrow' 'r="' PositiveInt '"' [ 'c="' ColumnLetter '"' ] '>' Value+ '</xrow>'
Value         ::= '<xv>' TextContent '</xv>'
Cell          ::= '<xcell' 'addr="' CellAddress '"' 'v="' TextContent '"' [ 't="' TypeName '"' ] '/>'
Range         ::= '<xrange' 'from="' CellAddress '"' 'to="' CellAddress '"' 'fill="' TextContent '"' [ 't="' TypeName '"' ] '/>'

Identifier    ::= [A-Za-z0-9_-]+
PositiveInt   ::= [1-9][0-9]*
ColumnLetter  ::= [A-Z]+
CellAddress   ::= ColumnLetter PositiveInt
TypeName      ::= 'string' | 'number' | 'bool' | 'date'
TextContent   ::= XMLChar*
```

---

## 5. Type System

### 5.1 Value Types

EXLang defines five primitive value types:

| Type | Description | Excel Type | Example |
|------|-------------|------------|---------|
| **Formula** | Expression starting with `=` | Formula | `=SUM(A1:A5)` |
| **Integer** | Whole number | Number (int) | `123`, `-456` |
| **Float** | Decimal number | Number (float) | `123.45`, `-0.5` |
| **Boolean** | Logical value | Boolean | `TRUE`, `FALSE` |
| **String** | Text content | Text | `"Hello"`, `"00123"` |

### 5.2 Type Inference Rules

Type inference follows this decision tree:

```
infer_type(raw_value, type_hint):
  
  # Step 1: Formula detection (highest priority)
  if raw_value[0] == '=':
    return Formula(raw_value)
  
  # Step 2: Explicit type hint
  if type_hint is not None:
    if type_hint == 'string':
      return String(raw_value)
    
    if type_hint == 'number':
      return parse_number(raw_value) OR String(raw_value)
    
    if type_hint == 'bool':
      return parse_bool(raw_value) OR String(raw_value)
    
    if type_hint == 'date':
      return String(raw_value)  # Future: date parsing
  
  # Step 3: Automatic inference
  if matches_regex(raw_value, r'^[+-]?\d+$'):
    return Integer(raw_value)
  
  if matches_regex(raw_value, r'^[+-]?\d*\.\d+$'):
    return Float(raw_value)
  
  # Step 4: Default fallback
  return String(raw_value)
```

### 5.3 Type Hint Semantics

| Type Hint | Behaviour | Use Case |
|-----------|-----------|----------|
| `t="string"` | Force string type | Preserve leading zeros: `"00123"` |
| `t="number"` | Force numeric parsing | Ensure numeric interpretation |
| `t="bool"` | Parse as boolean | `TRUE`, `FALSE`, `YES`, `NO` |
| `t="date"` | Reserved for future | Date/time values (v2) |

### 5.4 Boolean Parsing

Boolean values are case-insensitive:

```
TRUE, True, true → Boolean(True)
FALSE, False, false → Boolean(False)
YES, Yes, yes → Boolean(True)
NO, No, no → Boolean(False)
```

Any other value with `t="bool"` falls back to string.

### 5.5 Type Coercion

EXLang performs **no implicit type coercion** during compilation. Type inference occurs once during cell value assignment. Excel may perform runtime coercion when formulas are evaluated.

---

## 6. Semantic Rules

### 6.1 Document Semantics

**Rule 6.1.1**: Every EXLang document represents exactly one Excel workbook.

**Rule 6.1.2**: The root element must be `<xworkbook>`.

**Rule 6.1.3**: A workbook must contain at least one sheet.

### 6.2 Sheet Semantics

**Rule 6.2.1**: Each `<xsheet>` element creates one worksheet in the output workbook.

**Rule 6.2.2**: The `name` attribute specifies the worksheet name visible in Excel.

**Rule 6.2.3**: Sheet names should be unique. Duplicate names may cause Excel warnings.

**Rule 6.2.4**: Empty sheets (no content) are valid and create blank worksheets.

### 6.3 Row Placement Semantics

**Rule 6.3.1**: `<xrow>` places values sequentially in a single row.

**Rule 6.3.2**: The `r` attribute specifies the 1-based row index (1 = first row).

**Rule 6.3.3**: The `c` attribute specifies the starting column letter. Default: `"A"`.

**Rule 6.3.4**: Values within `<xrow>` are placed in consecutive columns:
```
<xrow r="1" c="B">
  <xv>First</xv>   <!-- B1 -->
  <xv>Second</xv>  <!-- C1 -->
  <xv>Third</xv>   <!-- D1 -->
</xrow>
```

**Rule 6.3.5**: Empty `<xv>` elements result in `None` (empty cell) in Excel.

### 6.4 Cell Placement Semantics

**Rule 6.4.1**: `<xcell>` places a single value at an exact address.

**Rule 6.4.2**: The `addr` attribute uses A1 notation (e.g., `"B5"`, `"AA100"`).

**Rule 6.4.3**: The `v` attribute contains the cell value or formula.

**Rule 6.4.4**: Direct cell placement overrides row-based placement at the same address.

### 6.5 Range Fill Semantics

**Rule 6.5.1**: `<xrange>` fills all cells in a rectangular area with the same value.

**Rule 6.5.2**: The `from` attribute specifies the top-left cell (starting cell).

**Rule 6.5.3**: The `to` attribute specifies the bottom-right cell (ending cell).

**Rule 6.5.4**: The `fill` attribute contains the value to place in all cells.

**Rule 6.5.5**: Range bounds are inclusive: both `from` and `to` cells are filled.

**Rule 6.5.6**: `from` must be before or equal to `to` (both row and column).

**Example:**
```xml
<xrange from="B2" to="D4" fill="0"/>
<!-- Fills 3×3 grid: B2, B3, B4, C2, C3, C4, D2, D3, D4 all = 0 -->
```

**Rule 6.5.7**: Type inference applies to the `fill` value:
- Numeric strings become integers or floats
- Formulas (starting with `=`) remain as formulas
- Type hint `t` overrides inference

**Rule 6.5.8**: Single-cell ranges (`from = to`) are valid.

###  6.6 Overlap Resolution

**Rule 6.6.1**: If multiple elements write to the same cell, **last write wins**.

**Rule 6.6.2**: Processing order within a sheet:
1. All `<xrow>` elements (in document order)
2. All `<xrange>` elements (in document order)
3. All `<xcell>` elements (in document order)

**Example:**
```xml
<xsheet name="Test">
  <xrow r="1"><xv>Original</xv></xrow>      <!-- A1 = "Original" -->
  <xrange from="A1" to="A3" fill="Range"/>  <!-- A1 = "Range" (overwrites) -->
  <xcell addr="A1" v="Override"/>           <!-- A1 = "Override" (final) -->
</xsheet>
```

**Rule 6.6.3**: `<xrange>` can overwrite row-based placement.

**Rule 6.6.4**: `<xcell>` can overwrite range fills.

### 6.7 Formula Semantics

**Rule 6.7.1**: Values starting with `=` are treated as Excel formulas.

**Rule 6.7.2**: Formulas are **stored**, not evaluated during compilation.

**Rule 6.7.3**: Formula syntax must be valid Excel formula notation.

**Rule 6.7.4**: Cross-sheet references use `SheetName!CellAddress` syntax:
```xml
<xcell addr="A1" v="=Data!B2+Summary!C5"/>
```

---

## 7. Validation Rules

### 7.1 Structural Validation

**V1**: Root element must be `<xworkbook>`  
**V2**: `<xworkbook>` must contain at least one `<xsheet>`  
**V3**: `<xsheet>` must have `name` attribute  
**V4**: `<xrow>` must have `r` attribute  
**V5**: `<xcell>` must have `addr` and `v` attributes  
**V6**: `<xrange>` must have `from`, `to`, and `fill` attributes  

### 7.2 Attribute Validation

**V7**: `name` must be non-empty string  
**V8**: `r` must be positive integer (≥ 1)  
**V9**: `c` must match pattern `[A-Z]+`  
**V10**: `addr` must match pattern `[A-Z]+[1-9][0-9]*`  
**V11**: `from` must match pattern `[A-Z]+[1-9][0-9]*`  
**V12**: `to` must match pattern `[A-Z]+[1-9][0-9]*`  
**V13**: `t` (if present) must be one of: `string`, `number`, `bool`, `date`  

### 7.3 Type Validation

**V14**: Type hint must be from allowed set  
**V15**: Formula values (starting with `=`) ignore type hints  
**V16**: Invalid type hint values are rejected before compilation  

### 7.4 Range Validation

**V17**: For `<xrange>`, `from` cell must be ≤ `to` cell (both row and column)  
**V18**: Invalid cell addresses in `from` or `to` are rejected  
**V19**: Range addresses must follow A1 notation strictly  

### 7.4 XML Well-Formedness

**V14**: Document must be valid XML 1.0  
**V15**: All elements must be properly nested  
**V16**: All tags must be closed  
**V17**: Attribute values must be quoted  

---

## 8. Error Taxonomy

### 8.1 Parse Errors (P-Class)

**P1**: Malformed XML syntax  
**P2**: Unclosed tags  
**P3**: Invalid character encoding  
**P4**: Empty document  

**Example:**
```xml
<xworkbook><xsheet name="Test">  <!-- P2: Missing closing tags -->
```

### 8.2 Validation Errors (V-Class)

**V1**: Wrong root element  
**V2**: Missing required attribute  
**V3**: Invalid attribute value  
**V4**: Unknown type hint  

**Example:**
```xml
<xworkbook>
  <xsheet>  <!-- V2: Missing 'name' attribute -->
    <xcell addr="A1" v="123"/>
  </xsheet>
</xworkbook>
```

### 8.3 Runtime Errors (R-Class)

**R1**: Invalid column letter conversion  
**R2**: Non-numeric row index  
**R3**: File system I/O error  

**Example:**
```xml
<xrow r="one">  <!-- R2: Non-numeric row index -->
  <xv>Test</xv>
</xrow>
```

### 8.4 Error Handling

**Rule 8.4.1**: Validation errors prevent compilation (fail-fast).

**Rule 8.4.2**: All validation errors are collected before reporting.

**Rule 8.4.3**: Error messages include element location and specific violation.

---

## 9. Compilation Semantics

### 9.1 Translation Model

```
EXLang Document  →  Parse  →  Validate  →  Compile  →  Excel Workbook
```

### 9.2 Execution Phases

**Phase 1: Parsing**
- Input: EXLang text (UTF-8 string)
- Process: XML parsing with ElementTree
- Output: XML element tree
- Errors: P-class errors

**Phase 2: Validation**
- Input: XML element tree
- Process: Apply validation rules V1–V14
- Output: Validation result (pass/fail + errors)
- Errors: V-class errors

**Phase 3: Compilation**
- Input: Validated element tree
- Process: Excel workbook generation
- Output: `.xlsx` file
- Errors: R-class errors

### 9.3 Determinism Guarantee

**Theorem 9.3.1**: For any valid EXLang document `D`, compiling `D` multiple times produces byte-identical Excel files.

**Proof sketch**: 
1. Parsing is deterministic (XML standard)
2. Validation is deterministic (rule-based)
3. Cell placement follows fixed ordering (Rule 6.5.2)
4. Type inference is deterministic (Section 5.2)
5. Excel generation uses fixed parameters (no timestamps, no random IDs)

### 9.4 Translation Rules

| EXLang Construct | Excel Output |
|------------------|--------------|
| `<xworkbook>` | Excel workbook (.xlsx file) |
| `<xsheet name="N">` | Worksheet named "N" |
| `<xrow r="R" c="C">` | Values at row R, columns C, C+1, C+2, ... |
| `<xv>V</xv>` | Cell value (type inferred) |
| `<xcell addr="A" v="V" t="T">` | Cell at address A with value V (type T) |

---

## 10. Railroad Diagrams

### 10.1 Document Structure

```
Document: ──┬────────────┬─── Workbook ───
            └─ XMLDecl ──┘
```

### 10.2 Workbook

```
Workbook: ── <xworkbook> ──┬─ Sheet ──┬─── </xworkbook> ───
                           └───────────┘
                              (1 or more)
```

### 10.3 Sheet

```
Sheet: ── <xsheet name="..."> ──┬─────────────────┬─── </xsheet> ───
                                 │  ┌───────────┐ │
                                 └──┤ Row       ├─┘
                                    │ Cell      │
                                    └───────────┘
                                    (0 or more)
```

### 10.4 Row

```
Row: ── <xrow r="..." ──┬─────────────┬──> ──┬─ Value ──┬─── </xrow> ───
                        └─ c="..." ──┘      └───────────┘
                         (optional)           (1 or more)
```

### 10.5 Cell

```
Cell: ── <xcell addr="..." v="..." ──┬─────────────┬─── /> ───
                                       └─ t="..." ──┘
                                        (optional)
```

### 10.6 Value

```
Value: ── <xv> ─── TextContent ─── </xv> ───
```

---

## 11. Conformance

### 11.1 Reference Implementation

**Name**: `exlang` Python package  
**Version**: 0.1.0  
**Language**: Python 3.10+  
**Dependencies**: `openpyxl` (Excel generation), `xml.etree.ElementTree` (parsing)  
**Test Coverage**: 97%+ (72 automated tests)  
**Repository**: https://github.com/sg98ccy/exlang

### 11.2 Conformance Requirements

An EXLang implementation conforms to this specification if:

1. It accepts all valid EXLang documents (Section 4)
2. It rejects all invalid documents with appropriate errors (Sections 7–8)
3. It produces Excel files matching the translation rules (Section 9)
4. It implements the type system correctly (Section 5)
5. It preserves semantic equivalence (Section 6)

### 11.3 Test Suite

The reference implementation includes:

- **Parsing tests**: 13 tests (valid + invalid documents)
- **Helper tests**: 20 tests (column conversion, type inference)
- **Compiler tests**: 12 tests (value types, placement)
- **Roundtrip tests**: 12 tests (semantic preservation)
- **Error tests**: 15 tests (error handling)

All tests must pass for conformance.

### 11.4 Validation

Conformance can be verified by:

1. Running the automated test suite: `pytest tests/`
2. Comparing output against reference Excel files
3. Verifying type inference matches Section 5.2

---

## 12. References

### 12.1 Normative References

- **XML 1.0**: W3C Recommendation, https://www.w3.org/TR/xml/
- **EBNF**: ISO/IEC 14977:1996
- **Excel Cell Addressing**: A1 notation (standard spreadsheet convention)

### 12.2 Informative References

- **openpyxl**: Python library for Excel generation, https://openpyxl.readthedocs.io/
- **Output Representation Optimisation (ORO)**: Research framework for LLM output efficiency

### 12.3 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-17 | Initial formal specification |

---

## Appendix A: Complete Grammar (Single Block)

```ebnf
(* ============================================================ *)
(* EXLANG v1 Complete Grammar                                   *)
(* ============================================================ *)

Document      ::= [ XMLDecl ] Workbook
XMLDecl       ::= '<?xml version="1.0" encoding="UTF-8"?>'

Workbook      ::= '<xworkbook>' Sheet { Sheet } '</xworkbook>'
Sheet         ::= '<xsheet name="' Identifier '">' { SheetContent } '</xsheet>'
SheetContent  ::= Row | Cell

Row           ::= '<xrow r="' PositiveInt '"' [ ' c="' ColumnLetter '"' ] '>' 
                  Value { Value } '</xrow>'
Value         ::= '<xv>' TextContent '</xv>'

Cell          ::= '<xcell addr="' CellAddress '" v="' TextContent '"' 
                  [ ' t="' TypeName '"' ] '/>'

(* Terminals *)
Identifier    ::= ( Letter | Digit | '_' | '-' ) { Letter | Digit | '_' | '-' }
PositiveInt   ::= NonZeroDigit { Digit }
ColumnLetter  ::= UpperLetter { UpperLetter }
CellAddress   ::= ColumnLetter PositiveInt
TypeName      ::= 'string' | 'number' | 'bool' | 'date'
TextContent   ::= { XMLChar }

Letter        ::= 'A' | 'B' | ... | 'Z' | 'a' | 'b' | ... | 'z'
UpperLetter   ::= 'A' | 'B' | ... | 'Z'
Digit         ::= '0' | '1' | ... | '9'
NonZeroDigit  ::= '1' | '2' | ... | '9'
XMLChar       ::= <any valid XML character>
```

---

## Appendix B: Example Documents

### B.1 Minimal Valid Document

```xml
<xworkbook>
  <xsheet name="Sheet1"></xsheet>
</xworkbook>
```

### B.2 Complete Example

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xworkbook>
  <xsheet name="Data">
    <xrow r="1"><xv>ID</xv><xv>Name</xv><xv>Value</xv></xrow>
    <xrow r="2"><xv>1</xv><xv>Alice</xv><xv>100</xv></xrow>
    <xrow r="3"><xv>2</xv><xv>Bob</xv><xv>200</xv></xrow>
  </xsheet>
  <xsheet name="Summary">
    <xcell addr="A1" v="Total"/>
    <xcell addr="B1" v="=SUM(Data!C2:C3)"/>
  </xsheet>
</xworkbook>
```

---

**End of Specification**
