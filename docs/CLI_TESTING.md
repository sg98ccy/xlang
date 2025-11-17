# CLI Manual Testing Guide

This guide provides step-by-step instructions for manually testing the EXLang command-line interface.

---

## Prerequisites

Ensure you are in the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

Test files are located in `tests/cli/`:
- `test_sample.xlang` — Valid EXLANG file
- `test_invalid.xlang` — Invalid EXLANG file (missing `name` attribute)

---

## Basic Commands

### Test 1: Check Version

```powershell
exlang --version
```

**Expected output**: `exlang, version 0.1.0`

---

### Test 2: View Help

```powershell
exlang --help
```

**Expected**: Shows available commands (compile, validate) with descriptions

---

### Test 3: View Compile Help

```powershell
exlang compile --help
```

**Expected**: Shows compile command options (--output, --force, --verbose)

---

### Test 4: View Validate Help

```powershell
exlang validate --help
```

**Expected**: Shows validate command options (--format, --verbose)

---

## Validation Commands

### Test 5: Validate Valid File

```powershell
exlang validate tests/cli/test_sample.xlang
```

**Expected**:
- Exit code: 0
- Output: Green checkmark (✓) with "valid" message

---

### Test 6: Validate Invalid File

```powershell
exlang validate tests/cli/test_invalid.xlang
```

**Expected**:
- Exit code: 1
- Output: Red cross (✗) or error message about missing "name" attribute

---

### Test 7: Validate with JSON Output

```powershell
exlang validate tests/cli/test_sample.xlang --format json
```

**Expected**:
- Exit code: 0
- Output: JSON object with `"valid": true`

```json
{
  "results": [
    {
      "file": "tests/cli/test_sample.xlang",
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

---

### Test 8: Validate Invalid File with JSON Output

```powershell
exlang validate tests/cli/test_invalid.xlang --format json
```

**Expected**:
- Exit code: 1
- Output: JSON object with `"valid": false` and error details

---

### Test 9: Validate Multiple Files

```powershell
exlang validate tests/cli/test_sample.xlang tests/cli/test_invalid.xlang
```

**Expected**:
- Exit code: 1 (at least one file is invalid)
- Output: Results for both files (one valid, one invalid)

---

### Test 10: Validate with Verbose Mode

```powershell
exlang validate tests/cli/test_sample.xlang --verbose
```

**Expected**:
- Exit code: 0
- Output: Shows "Validating..." message followed by result

---

## Compilation Commands

### Test 11: Compile with Default Output

```powershell
exlang compile tests/cli/test_sample.xlang
```

**Expected**:
- Exit code: 0
- Output: Green success message
- File created: `tests/cli/test_sample.xlsx`

---

### Test 12: Compile with Custom Output Path

```powershell
exlang compile tests/cli/test_sample.xlang -o output/cli_test.xlsx
```

**Expected**:
- Exit code: 0
- Output: Success message showing `output/cli_test.xlsx`
- File created: `output/cli_test.xlsx`

---

### Test 13: Compile When Output Exists (Without Force)

Run Test 11 or 12 again without deleting the output file.

**Expected**:
- Exit code: 2
- Output: Error message stating file already exists

---

### Test 14: Compile with Force Flag

```powershell
exlang compile tests/cli/test_sample.xlang --force
```

**Expected**:
- Exit code: 0
- Output: Success message
- File overwritten: `tests/cli/test_sample.xlsx`

---

### Test 15: Compile with Verbose Mode

```powershell
exlang compile tests/cli/test_sample.xlang -o output/verbose_test.xlsx --verbose
```

**Expected**:
- Exit code: 0
- Output: Shows "Compiling..." message followed by success message
- File created: `output/verbose_test.xlsx`

---

### Test 16: Compile Invalid File

```powershell
exlang compile tests/cli/test_invalid.xlang
```

**Expected**:
- Exit code: 3
- Output: Validation error message (missing "name" attribute)
- No file created

---

### Test 17: Compile Non-Existent File

```powershell
exlang compile tests/cli/nonexistent.xlang
```

**Expected**:
- Exit code: 1
- Output: File not found error

---

## Cleanup

After testing, remove generated files:

```powershell
Remove-Item tests/cli/test_sample.xlsx -ErrorAction SilentlyContinue
Remove-Item output/cli_test.xlsx -ErrorAction SilentlyContinue
Remove-Item output/verbose_test.xlsx -ErrorAction SilentlyContinue
```

---

## Exit Code Reference

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | File not found |
| 2 | Output file already exists (use --force) |
| 3 | Validation error |

---

## Common Issues

**Issue**: `exlang: The term 'exlang' is not recognized`

**Solution**: Ensure you are in the virtual environment and the package is installed:
```powershell
.venv\Scripts\Activate.ps1
pip install -e .
```

**Issue**: Permission denied when creating output files

**Solution**: Ensure the output directory exists and you have write permissions:
```powershell
New-Item -ItemType Directory -Force -Path output
```
