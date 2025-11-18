# EXLang Comprehensive Examples

Single notebook with 5 increasingly complex real-world scenarios demonstrating all 9 EXLang tags.

## Getting Started

Install the EXLang package first:

```bash
cd ../..
pip install -e .
```

## Notebook: comprehensive_examples.ipynb

**Difficulty**: Beginner → Advanced  
**Tags**: All 9 tags demonstrated

### Examples Included

1. **Sales Dashboard** (Medium complexity)
   - Merged titles, bold headers
   - Product data with quarterly metrics
   - Row and column totals with formulas

2. **Employee Scheduling Matrix** (Medium-High complexity)
   - 20 employees across 3 departments
   - 12-month scheduling grid (240 assignments)
   - Department section headers with merge + style

3. **Financial Statement** (High complexity)
   - Multi-section P&L (Income, Expenses, Net)
   - 4 revenue streams + 6 cost categories
   - Monthly data with YTD totals (156 data points + 39 formulas)

4. **Product Inventory System** (High complexity)
   - 4 product categories, 20 products
   - 8 weeks of stock tracking
   - Automated reorder alerts with IF formulas

5. **Multi-Sheet Annual Report** (Maximum complexity)
   - 3 worksheets (Revenue, Costs, Dashboard)
   - Cross-sheet formulas for KPI calculations
   - Regional and departmental analysis
   - Production-ready executive reporting

**Files generated**: 5 comprehensive Excel workbooks

---

## Quick Reference

### Tag Summary

| Tag | Purpose | Key Constraint |
|-----|---------|----------------|
| `<xworkbook>` | Root container | One per file |
| `<xsheet>` | Worksheet | Multiple allowed |
| `<xrow>` | Row placement | Contains `<xv>` only |
| `<xv>` | Cell value | Text/number/formula |
| `<xcell>` | Direct assignment | addr + v required |
| `<xrange>` | Bulk fill | from/to/fill required |
| `<xrepeat>` | Pattern generation | **Contains `<xv>` only** |
| `<xmerge>` | Cell merging | Range format (A1:B1) |
| `<xstyle>` | Formatting | Boolean attributes |

### Important: xrepeat Limitations

**xrepeat can only contain `<xv>` tags**, not `<xcell>`. This means:

✅ **Correct** - Template variables in values:
```xml
<xrepeat times="5" r="4" c="A" direction="down">
  <xv>Product {{i}}</xv>
  <xv>15000</xv>
</xrepeat>
```

❌ **Incorrect** - Formulas with dynamic addresses:
```xml
<xrepeat times="5" r="4" c="A" direction="down">
  <xv>=SUM(B{{i0}}:E{{i0}})</xv>  <!-- Will create invalid formulas! -->
</xrepeat>
```

**Why?** Template variables `{{i0}}` substitute to 0,1,2,3,4, creating formulas like `=SUM(B0:E0)` which are invalid (Excel rows start at 1).

**Solution**: Use individual `<xcell>` tags for formulas with specific addresses:
```xml
<xcell addr="F4" v="=SUM(B4:E4)"/>
<xcell addr="F5" v="=SUM(B5:E5)"/>
```

### Processing Order

```
xrow → xrange → xrepeat → xcell → xmerge → xstyle
```

**Last write wins** — later tags can overwrite earlier ones.

---

## Running the Notebooks

### Option 1: Jupyter Notebook
```bash
jupyter notebook
```

### Option 2: VS Code
1. Open any `.ipynb` file
2. Select Python kernel
3. Run cells sequentially

### Option 3: JupyterLab
```bash
jupyter lab
```

---

## Output Files

All generated Excel files are saved to `../../output/`:

```
output/examples/
├── 01_minimal.xlsx
├── 02_rows.xlsx
├── 03_formulas.xlsx
├── 04_mixed.xlsx
├── 05_xrange.xlsx
├── 06_xrepeat_down.xlsx
├── 07_xrepeat_right.xlsx
├── 08_template_i0.xlsx
├── 09_large_scale.xlsx
├── 10_combined.xlsx
├── 11_merge_basic.xlsx
├── 12_style_basic.xlsx
├── 13_merge_style.xlsx
├── 14_repeat_style.xlsx
├── 15_complex_table.xlsx
└── 16_complete_budget.xlsx
```

---

## Learning Path

**Recommended order**:
1. **Example 1** → Understand basic structure
2. **Example 2** → Master pattern generation (core ORO concept)
3. **Example 3** → Add professional formatting
4. **Example 4** → Build complete multi-sheet workbooks

**Time estimate**: 2-3 hours to complete all notebooks

---

## Key Concepts

### Output Representation Optimisation (ORO)

EXLang achieves token efficiency through:
- **Pattern-based generation**: `<xrepeat>` replaces 100+ explicit tags
- **Declarative structure**: XML self-documents intent
- **Strategic layering**: xrange → xrepeat → xcell (background → pattern → override)

### When to Use Each Tag

- **`<xrow>`**: Tabular data with varying values per row
- **`<xrange>`**: Large uniform areas (zeros, defaults, backgrounds)
- **`<xrepeat>`**: Templated patterns (12 months, 100 employees, etc.)
- **`<xcell>`**: Specific overrides or one-off values
- **`<xmerge>`**: Titles, section headers, merged cells
- **`<xstyle>`**: Professional appearance (headers, totals, emphasis)

---

## Further Resources

- **Formal grammar**: `../docs/GRAMMAR.md`
- **Test suite**: `../tests/` (90+ examples)
- **Main package**: `../src/exlang/`
- **Project README**: `../README.md`

---

## Questions or Issues?

Check the test suite in `../tests/` for additional examples covering edge cases and validation scenarios.

For language specification details, see `../docs/GRAMMAR.md` with complete EBNF grammar, semantic rules, and validation requirements.

---

**Happy learning! 🎓**

Build production-grade Excel workbooks with minimal token overhead using EXLang's structured markup and pattern-based generation.
