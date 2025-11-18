# ============================================================
# exlang.validator: minimal schema checks
# ============================================================

from xml.etree import ElementTree as ET

ALLOWED_TYPES = {"number", "string", "date", "bool"}
ALLOWED_DIRECTIONS = {"down", "right"}
ALLOWED_BOOL_VALUES = {"true", "false"}


def validate_xlang_minimal(root: ET.Element) -> list[str]:
    """
    Perform minimal validation of an exlang document.

    Checks:
      - Root tag is xworkbook
      - xsheet name is optional (auto-generated as Sheet1, Sheet2, etc. if omitted)
      - Auto-generated names must not conflict with explicitly named sheets
      - xrow has r
      - xrepeat has times
      - xcell has addr and v
      - xrange has from, to, and fill
      - Optional t attributes use only allowed type names
      - Optional direction attribute uses only allowed directions
    """
    errors: list[str] = []

    if root.tag != "xworkbook":
        errors.append(f"Root tag must be 'xworkbook' but found '{root.tag}'")
        return errors

    # Check for collisions between auto-generated and explicit sheet names
    explicit_names = set()
    auto_generated_count = 0
    
    for sheet in root.findall("xsheet"):
        name = sheet.attrib.get("name")
        if name:
            explicit_names.add(name)
        else:
            auto_generated_count += 1
    
    # Check if auto-generated names would conflict with explicit names
    for i in range(1, auto_generated_count + 1):
        auto_name = f"Sheet{i}"
        if auto_name in explicit_names:
            errors.append(
                f"Auto-generated sheet name '{auto_name}' conflicts with explicitly named sheet. "
                f"Either name all sheets or ensure explicit names don't use 'Sheet1', 'Sheet2', etc."
            )

    for sheet in root.findall("xsheet"):

        for xrow in sheet.findall("xrow"):
            if "r" not in xrow.attrib:
                errors.append("xrow missing required attribute 'r'")

        for xrepeat in sheet.findall("xrepeat"):
            if "times" not in xrepeat.attrib:
                errors.append("xrepeat missing required attribute 'times'")
            
            # Validate times is a positive integer
            times_str = xrepeat.attrib.get("times", "")
            if times_str:
                try:
                    times_val = int(times_str)
                    if times_val < 1:
                        errors.append(f"xrepeat 'times' must be >= 1, got {times_val}")
                except ValueError:
                    errors.append(f"xrepeat 'times' must be an integer, got '{times_str}'")
            
            # Validate direction if present
            direction = xrepeat.attrib.get("direction")
            if direction is not None and direction not in ALLOWED_DIRECTIONS:
                errors.append(
                    f"xrepeat has invalid direction='{direction}'. "
                    f"Must be one of: {', '.join(ALLOWED_DIRECTIONS)}"
                )
            
            # Check for nested xrepeat (not allowed)
            if xrepeat.findall(".//xrepeat"):
                errors.append("Nested xrepeat is not allowed")
            
            # Validate content contains only xv tags
            for child in xrepeat:
                if child.tag != "xv":
                    errors.append(
                        f"xrepeat can only contain <xv> tags, found <{child.tag}>"
                    )

        for xcell in sheet.findall("xcell"):
            if "addr" not in xcell.attrib:
                errors.append("xcell missing required attribute 'addr'")
            if "v" not in xcell.attrib:
                errors.append("xcell missing required attribute 'v'")
            t = xcell.attrib.get("t")
            if t is not None and t not in ALLOWED_TYPES:
                errors.append(
                    f"xcell at {xcell.attrib.get('addr', '?')} "
                    f"has invalid type hint t='{t}'"
                )

        for xrange in sheet.findall("xrange"):
            if "from" not in xrange.attrib:
                errors.append("xrange missing required attribute 'from'")
            if "to" not in xrange.attrib:
                errors.append("xrange missing required attribute 'to'")
            if "fill" not in xrange.attrib:
                errors.append("xrange missing required attribute 'fill'")
            t = xrange.attrib.get("t")
            if t is not None and t not in ALLOWED_TYPES:
                errors.append(
                    f"xrange from {xrange.attrib.get('from', '?')} to {xrange.attrib.get('to', '?')} "
                    f"has invalid type hint t='{t}'"
                )

        for xmerge in sheet.findall("xmerge"):
            if "addr" not in xmerge.attrib:
                errors.append("xmerge missing required attribute 'addr'")
            else:
                addr = xmerge.attrib["addr"]
                # Validate merge range format (A1:B1)
                if ":" not in addr:
                    errors.append(f"xmerge addr '{addr}' must be a range (e.g., 'A1:B1')")
                else:
                    parts = addr.split(":")
                    if len(parts) != 2:
                        errors.append(f"xmerge addr '{addr}' must have exactly one colon (e.g., 'A1:B1')")

        for xstyle in sheet.findall("xstyle"):
            if "addr" not in xstyle.attrib:
                errors.append("xstyle missing required attribute 'addr'")
            
            # Validate boolean style attributes
            for attr in ["bold", "italic", "underline"]:
                value = xstyle.attrib.get(attr)
                if value is not None and value not in ALLOWED_BOOL_VALUES:
                    errors.append(
                        f"xstyle at {xstyle.attrib.get('addr', '?')} has invalid {attr}='{value}'. "
                        f"Must be 'true' or 'false'"
                    )

    return errors
