from pathlib import Path
import pytest

from pyorg2.file_parser import parse_org_file, parse_org_directory, parse_org_files

test_files_dir = Path(Path(__file__).resolve().parent, "test_notes")

def test_single_file():
    # Single file
    #parser = OrgFileParser()
    #parser.parse_file(Path(test_files_dir, 'trade.org'))
    #html = parser.to_html(newline='\n')
    html = parse_org_file(Path(test_files_dir, 'trade.org'), newline='\n')

def test_directory():
    html = parse_org_directory(Path(test_files_dir), newline='\n')

# File list
def test_file_list():
    files = [Path(test_files_dir, 'centers.org'),
             Path(test_files_dir, 'agriculture.org'),
             Path(test_files_dir, 'trade.org')]
    html = parse_org_files(files, newline='\n')
    breakpoint()
    print(html)

