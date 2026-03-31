#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["lxml"]
# ///

import sys
from lxml import etree


def normalize(path: str) -> str:
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(path, parser)
    for el in tree.iter():
        attribs = sorted(el.attrib.items())
        el.attrib.clear()
        el.attrib.update(attribs)
    return etree.tostring(tree, pretty_print=True).decode()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <file.xml>", file=sys.stderr)
        sys.exit(1)
    print(normalize(sys.argv[1]), end="")
