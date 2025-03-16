import pytest
from bs4 import BeautifulSoup
from pyorg2.file_parser import OrgFileParser
from pathlib import Path

@pytest.fixture
def sample_files(tmp_path):
    """Create temporary Org files for testing."""
    # File 1: agriculture.org
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
    return [ag_file, tr_file]

def test_org_roam_links(sample_files):
    """Test that Org-roam links resolve correctly in combined HTML."""
    parser = OrgFileParser()
    parser.parse_file_list(sample_files)
    html = parser.to_html(newline='\n', wrap=True)

    # Parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')

    # Find all links
    links = soup.find_all('a')
    assert len(links) == 1, "Expected one Org-roam link"
    link = links[0]
    assert link['href'] == '#abc-456', "Link href mismatch"
    assert link.text == 'Trade Networks', "Link text mismatch"

    # Find all headings with IDs
    headings = soup.find_all(lambda tag: tag.name.startswith('h') and tag.get('id'))
    assert len(headings) == 2, "Expected two headings with IDs"
    
    # Map IDs to headings
    id_map = {h['id']: h.text for h in headings}
    assert 'abc-123' in id_map, "Agriculture ID missing"
    assert id_map['abc-123'] == 'Agriculture', "Agriculture title mismatch"
    assert 'abc-456' in id_map, "Trade Networks ID missing"
    assert id_map['abc-456'] == 'Trade Networks', "Trade Networks title mismatch"

    # Verify link points to an existing ID
    assert link['href'][1:] in id_map, "Link points to nonexistent ID"
