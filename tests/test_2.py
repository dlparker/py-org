from pathlib import Path
from bs4 import BeautifulSoup
import pytest
from pyorg2.file_parser import parse_org_file, parse_org_directory, parse_org_files

@pytest.fixture
def sample_files(tmp_path):
    """Create temporary Org files for testing."""
    ag_file = tmp_path / "agriculture.org"
    ag_file.write_text(
        "#+ID: abc-123\n"
        "* Agriculture\n"
        "Farming info linked to [[id:abc-456][Trade Networks]]."
    )
    # File 2: trade.org
    tr_file = tmp_path / "trade.org"
    tr_file.write_text(
        "#+ID: abc-456\n"
        "* Trade Networks\n"
        "Details on shipping."
    )
    # File 3: centers.org
    cent_file = tmp_path / "centers.org"
    cent_file.write_text(
        "#+ID: abc-789\n"
        "* Centers\n"
        "Centers are part of [[id:abc-456][Trade Networks]], trading\n"
        "goods from [[id:abc-123][agriculture]]"
    )
    return [ag_file, tr_file, cent_file]

    

def test_single_file(sample_files):
    html = parse_org_file(sample_files[0], newline='\n')

def test_directory(sample_files):
    html = parse_org_directory(Path(sample_files[0]).parent, newline='\n')

# File list
def test_file_list(sample_files):
    files = [sample_files[2],
             sample_files[1],
             sample_files[0]]
    html = parse_org_files(files, newline='\n')
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a')
    assert len(links) == 3, "Expected two Org-roam links"
    link_0 = links[0]
    assert link_0['href'] == '#abc-456', "Link href mismatch"
    assert link_0.text == 'Trade Networks', "Link text mismatch"
    link_1 = links[1]
    assert link_1['href'] == '#abc-123', "Link href mismatch"
    assert link_1.text == 'agriculture', "Link text mismatch"
    link_2 = links[2]
    assert link_2['href'] == '#abc-456', "Link href mismatch"
    assert link_2.text == 'Trade Networks', "Link text mismatch"

