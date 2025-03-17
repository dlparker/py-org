#!/usr/bin/env python
import sys
from pathlib import Path
try:
    import pyorg2 as test_import
except ModuleNotFoundError:
    parent = str(Path(__file__).resolve().parent.parent)
    sys.path.append(parent)
from pyorg2.file_parser import parse_org_file, parse_org_directory, parse_org_files, OrgFileParser


def main(filepath):
    parser = OrgFileParser()
    parser.parse_file(filepath)


if __name__=="__main__":
    if len(sys.argv) != 2:
        raise Exception('You must supply an input file')
    filepath = Path(sys.argv[1]).resolve()
    main(filepath)
