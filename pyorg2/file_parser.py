# pyorg2/file_parser.py
from pathlib import Path
from .org import Org, org_to_html

class OrgFileParser:

    def __init__(self, default_heading=1):
        self.default_heading = default_heading
        self.nodes = []
        self.id_map = {}  # Global ID map across files

    def parse_file(self, file_path):
        file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(f"{file_path} is not a valid file")
        with file_path.open('r', encoding='utf-8') as f:
            text = f.read()
        # Use filename as fallback ID if no #+ID:
        file_id = file_path.stem if '#+ID:' not in text else None
        org = Org(text, self.default_heading, file_id=file_id)
        self.nodes.append(org)
        self.id_map.update(org.id_map)  # Collect IDs
        return org

    def parse_directory(self, directory_path):
        """Parse all .org files in a directory."""
        directory = Path(directory_path)
        if not directory.is_dir():
            raise NotADirectoryError(f"{directory} is not a valid directory")
        org_files = sorted(directory.glob('*.org'))  # Alphabetical order
        for file_path in org_files:
            self.parse_file(file_path)
        return self.nodes

    def parse_file_list(self, file_paths):
        """Parse a list of Org-mode files in specified order."""
        for file_path in file_paths:
            self.parse_file(file_path)
        return self.nodes

    def to_html(self, newline='', wrap=True):
        if not self.nodes:
            return ''
        content = newline.join(node.html(newline, id_map=self.id_map) for node in self.nodes)
        if wrap:
            return f'<html><body>{content}</body></html>'
        return content

def parse_org_file(file_path, default_heading=1, newline=''):
    """Convenience function for single file parsing."""
    parser = OrgFileParser(default_heading)
    parser.parse_file(file_path)
    return parser.to_html(newline)

def parse_org_directory(directory_path, default_heading=1, newline=''):
    """Convenience function for directory parsing."""
    parser = OrgFileParser(default_heading)
    parser.parse_directory(directory_path)
    return parser.to_html(newline)

def parse_org_files(file_paths, default_heading=1, newline=''):
    """Convenience function for list of files parsing."""
    parser = OrgFileParser(default_heading)
    parser.parse_file_list(file_paths)
    return parser.to_html(newline)
