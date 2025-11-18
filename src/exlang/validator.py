# ============================================================
# exlang.validator: minimal schema checks
# ============================================================

from xml.etree import ElementTree as ET

ALLOWED_TYPES = {"number", "string", "date", "bool"}


def validate_xlang_minimal(root: ET.Element) -> list[str]:
    """
    Perform minimal validation of an exlang document.

    Checks:
      - Root tag is xworkbook
      - xsheet has name
      - xrow has r
      - xcell has addr and v
      - xrange has from, to, and fill
      - Optional t attributes use only allowed type names
    """
    errors: list[str] = []

    if root.tag != "xworkbook":
        errors.append(f"Root tag must be 'xworkbook' but found '{root.tag}'")
        return errors

    for sheet in root.findall("xsheet"):
        if "name" not in sheet.attrib:
            errors.append("xsheet missing required attribute 'name'")

        for xrow in sheet.findall("xrow"):
            if "r" not in xrow.attrib:
                errors.append("xrow missing required attribute 'r'")

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

    return errors
