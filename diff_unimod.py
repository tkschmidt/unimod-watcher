#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["lxml"]
# ///
"""
Compare two Unimod XML files and output a markdown summary of changes.
Usage: diff_unimod.py <old.xml> <new.xml>
"""

import sys
from lxml import etree

NS = "http://www.unimod.org/xmlns/schema/unimod_tables_1"
COMPARE_FIELDS = ("code_name", "full_name", "composition", "mono_mass", "avge_mass", "approved")


def parse_modifications(path: str) -> dict[str, dict]:
    tree = etree.parse(path)
    mods = {}
    for el in tree.iter(f"{{{NS}}}modifications_row"):
        record_id = el.attrib["record_id"]
        mods[record_id] = dict(el.attrib)
    return mods


def md_table(rows: list[dict], fields: list[str]) -> str:
    header = "| " + " | ".join(fields) + " |"
    sep = "| " + " | ".join("---" for _ in fields) + " |"
    lines = [header, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(f, "")) for f in fields) + " |")
    return "\n".join(lines)


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <old.xml> <new.xml>", file=sys.stderr)
        sys.exit(1)

    old_path, new_path = sys.argv[1], sys.argv[2]
    old_mods = parse_modifications(old_path)
    new_mods = parse_modifications(new_path)

    old_ids = set(old_mods)
    new_ids = set(new_mods)

    added_ids = sorted(new_ids - old_ids, key=int)
    removed_ids = sorted(old_ids - new_ids, key=int)
    common_ids = old_ids & new_ids

    changed = []
    for rid in sorted(common_ids, key=int):
        old, new = old_mods[rid], new_mods[rid]
        diffs = {f: (old.get(f, ""), new.get(f, "")) for f in COMPARE_FIELDS if old.get(f) != new.get(f)}
        if diffs:
            changed.append((rid, old, new, diffs))

    lines = ["## Unimod Changes\n"]

    # Added
    lines.append(f"### Added ({len(added_ids)})")
    if added_ids:
        rows = [new_mods[rid] for rid in added_ids]
        lines.append(md_table(rows, ["record_id", "code_name", "full_name", "mono_mass", "composition", "approved"]))
    else:
        lines.append("_None_")

    lines.append("")

    # Changed
    lines.append(f"### Changed ({len(changed)})")
    if changed:
        for rid, old, new, diffs in changed:
            lines.append(f"\n**{old['code_name']}** (record_id {rid})")
            field_rows = [{"field": f, "old": old_val, "new": new_val} for f, (old_val, new_val) in diffs.items()]
            lines.append(md_table(field_rows, ["field", "old", "new"]))
    else:
        lines.append("_None_")

    lines.append("")

    # Removed
    lines.append(f"### Removed ({len(removed_ids)})")
    if removed_ids:
        rows = [old_mods[rid] for rid in removed_ids]
        lines.append(md_table(rows, ["record_id", "code_name", "full_name", "mono_mass", "composition"]))
    else:
        lines.append("_None_")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
