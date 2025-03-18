from re import compile
from slugify import slugify  


# types that can CONATAIN target
# Text (and kids)
# ListItem 

# types that ARE targets
# Heading (is by default)

# types that can be designated a target by have #+NAME pre-line
# Table
# Para (if it is just a blank spot, emacs tries to make a header)
# quotes, block quotes code block codes

class Syntax(object):
    LINK = r'\[\[(?P<url>https?://.+?)\](?:\[(?P<subject>.+?)\])?\]'
    IMAGE = r'\[\[(?P<image>.+?)\](?:\[(?P<alt>.+?)\])?\]'
    BOLD = r'\*(?P<text>.+?)\*'
    ITALIC = r'/(?P<text>.+?)/'
    UNDERLINED = r'_(?P<text>.+?)_'
    LINETHROUGH = r'\+(?P<text>.+?)\+'
    CODE = r'=(?P<text>.+?)='
    MONOSPACE = r'~(?P<text>.+?)~'
    WHITELINE = r'\s*$'
    HEADING = r'(?P<level>\*+)\s+(?P<title>.+)$'
    QUOTE_BEGIN = r'#\+BEGIN_QUOTE(?P<c>:)?(?(c)\s+(?P<cite>.+)|)$'
    QUOTE_END = r'#\+END_QUOTE$'
    SRC_BEGIN = r'#\+BEGIN_SRC(?:\s+(?P<src_type>.+))?\s*$'
    SRC_END = r'#\+END_SRC'
    ORDERED_LIST = r'(?P<depth>\s*)\d+(\.|\))\s+(?P<item>.+)$'
    UNORDERED_LIST = r'(?P<depth>\s*)(-|\+)\s+(?P<item>.+)$'
    DEF_LIST = r'(?P<depth>\s*)(-|\+)\s+(?P<item>.+?)\s*::\s*(?P<desc>.+)$'
    TABLE_ROW = r'\s*\|(?P<cells>(.+\|)+)s*$'
    # [[#anchor][title]] or [[#anchor]]
    INTERNAL_LINK = r'\[\[#(?P<anchor>[^][]+?)\](?:\[(?P<title>.+?)\])?\]'
    TARGET = r'<<(?P<target>[^>]+)>>'  # <<target>>


class BaseError(Exception):
    pass

class NestingNotValidError(BaseError):
    pass

class OrgElement:

    def __init__(self, org_root):
        self.org_root = org_root
        self.is_target = False
        # if element is a target, this is the "link to" text
        self.target_string = None 

class Target:

    def __init__(self, org_root, target_text, target_element):
        self.org_root = org_root
        self.target_text = target_text
        self.target_element = target_element
        # guarantees uniqueness even of the target_text does not
        self.target_id = org_root.create_target_id(self)

    def link_matches(self, link_text):
        pass

    def get_html_id(self):
        return self.target_id
        
class Node(OrgElement):
    '''Base class for elements that may have children, nodes in a tree'''
    
    def __init__(self, org_root, parent=None):
        super().__init__(org_root)
        self.type_ = self.__class__.__name__
        self.children = []
        self.parent = parent
        if self.parent is None:
            self.parent = org_root

    def __str__(self):
        str_children = [str(child) for child in self.children]
        return self.type_ + '(' + ' '.join(str_children) + ')'

    def append(self, child):
        if isinstance(child, str):
            child = Text(self, child)
        self.children.append(child)
        child.parent = self

    def html(self, br='', lstrip=False):
        '''Get HTML'''
        inner = br.join([child.html(br, lstrip) for child in self.children])
        return ''.join([self._get_open(), inner,  self._get_close()])

    def _get_open(self):
        '''returns HTML open tag str'''
        raise NotImplementedError

    def _get_close(self):
        '''returns HTML close tag str'''
        raise NotImplementedError


class TerminalNode(OrgElement):
    '''Base class of all elements that do not have children, may or may not be child of a tree'''
    regexps = {
        'link': compile(Syntax.LINK),
        'image': compile(Syntax.IMAGE),
        'bold': compile(Syntax.BOLD),
        'italic': compile(Syntax.ITALIC),
        'underlined': compile(Syntax.UNDERLINED),
        'linethrough': compile(Syntax.LINETHROUGH),
        'code': compile(Syntax.CODE),
        'monospace': compile(Syntax.MONOSPACE)
    }

    def __init__(self, org_root, value, parent=None, noparse=False):
        super().__init__(org_root)
        self.type_ = self.__class__.__name__
        self.noparse = noparse
        self.org_root = org_root
        self.values = self._parse_value(value)
        self.parent = parent

    def _parse_value(self, value):
        if value is None:
            return ''

        if self.noparse:
            before = after = None
            parsed = value
        elif self.regexps['code'].search(value):
            before, text, after = self.regexps['code'].split(value, 1)
            parsed = InlineCodeText(self, text)
        elif self.regexps['link'].search(value):
            before, url, subject, after = self.regexps['link'].split(value, 1)
            parsed = Link(self, url, subject)
        elif self.regexps['image'].search(value):
            before, src, alt, after = self.regexps['image'].split(value, 1)
            parsed = Image(self, src, alt)
        elif self.regexps['bold'].search(value):
            before, text, after = self.regexps['bold'].split(value, 1)
            parsed = BoldText(self, text)
        elif self.regexps['italic'].search(value):
            before, text, after = self.regexps['italic'].split(value, 1)
            parsed = ItalicText(self, text)
        elif self.regexps['underlined'].search(value):
            before, text, after = self.regexps['underlined'].split(value, 1)
            parsed = UnderlinedText(self,text)
        elif self.regexps['linethrough'].search(value):
            before, text, after = self.regexps['linethrough'].split(value, 1)
            parsed = LinethroughText(self,text)
        elif self.regexps['monospace'].search(value):
            before, text, after = self.regexps['monospace'].split(value, 1)
            parsed = MonospaceText(self, text)
        else:
            before = after = None
            parsed = value
        before = self._parse_value(before) or []
        after = self._parse_value(after) or []
        return before + [parsed] + after

    def __str__(self):
        return self.type_

    def html(self, br='', lstrip=False):
        content = ''
        for value in self.values:
            if isinstance(value, str):
                if lstrip:
                    content += value.strip()
                else:
                    content += value.rstrip()
            else:
                content += value.html(br)
        return self._get_open() + content + self._get_close()

    def _get_open(self):
        '''returns HTML open tag str'''
        raise NotImplementedError

    def _get_close(self):
        '''returns HTML close tag str'''
        raise NotImplementedError

class InternalLink(TerminalNode):

    def __init__(self, org_root, anchor, title):
        self.anchor = anchor
        self.resolved = False  # Track resolution status
        super().__init__(org_root, title or anchor)

    def _get_open(self):
        if self.resolved:
            return f'<a href="#{self.anchor}">'
        return ''  # Unresolved: no link

    def _get_close(self):
        return '</a>' if self.resolved else ''

class Paragraph(Node):
    '''Paragraph Class'''
    def _get_open(self):
        return '<p>'

    def _get_close(self):
        return '</p>'

class Text(TerminalNode):
    '''Text Class'''
    def get_text(self):
        return ''.join([str(value) for value in self.values])

    def _get_open(self):
        return ''

    def _get_close(self):
        return ''


class BoldText(Text):
    '''Bold Text Class'''
    def _get_open(self):
        return '<span style="font-weight: bold;">'

    def _get_close(self):
        return '</span>'


class ItalicText(Text):
    '''Italic Text Class'''
    def _get_open(self):
        return '<span style="text-style: italic;">'

    def _get_close(self):
        return '</span>'


class UnderlinedText(Text):
    '''Underlined Text Class'''
    def _get_open(self):
        return '<span style="text-decoration: underlined;">'

    def _get_close(self):
        return '</span>'

class LinethroughText(Text):
    '''Linethrough Text Class'''
    def _get_open(self):
        return '<span style="text-decoration: line-through;">'

    def _get_close(self):
        return '</span>'

class InlineCodeText(Text):
    '''Inline Code Text Class'''
    less_than = compile(r'<')
    greater_than = compile(r'>')
    def _parse_value(self, value):
        return [value]

    def html(self, br=''):
        content = ''
        content = self.values[0].strip()
        content = self.less_than.sub('&lt;', content)
        content = self.greater_than.sub('&gt;', content)
        return self._get_open() + content + self._get_close()

    def _get_open(self):
        return '<code>'

    def _get_close(self):
        return '</code>'


class MonospaceText(Text):
    '''Monospace Text Class'''
    def _get_open(self):
        return '<span style="font-family: monospace;">'

    def _get_close(self):
        return '</span>'


class Blockquote(Node):
    '''Blockquote Class'''
    def __init__(self, org_root, cite=None):
        self.cite = cite
        super().__init__(org_root)

    def _get_open(self):
        if self.cite:
            return '<blockquote cite="{}">'.format(self.cite)
        else:
            return '<blockquote>'

    def _get_close(self):
        return '</blockquote>'


class CodeBlock(Node):
    ''' Block class Code Class '''
    def __init__(self, org_root, src_type=None):
        self.src_type = src_type
        super().__init__(org_root)

    def _get_open(self):
        if self.src_type:
            return '<pre><code class="{}">'.format(self.src_type)
        else:
            return '<pre><code>'

    def _get_close(self):
        return '</code></pre>'


class Heading(Node):
    '''Heading Class'''
    def __init__(self, org_root, depth, title, default_depth=1):
        self.depth = depth + (default_depth -1)
        self.title = title
        super().__init__(org_root)
        self.type_ = 'Heading{}'.format(self.depth)

    def html(self, br=''):
        heading = self._get_open() + self.title + self._get_close()
        content = ''.join([child.html(br) for child in self.children])
        return heading + content

    def _get_open(self):
        return '<h{}>'.format(self.depth)

    def _get_close(self):
        return '</h{}>'.format(self.depth)


class List(Node):
    '''Classes that make up a list derive from this base class, forming a tree'''
    def __init__(self, org_root, depth, ordered, definition, start=1):
        self.depth = depth
        self.ordered = ordered
        self.definition = definition
        if self.ordered:
            self.start = start
        super().__init__(org_root)

    def html(self, br='', lstrip=False):
        return super().html('', lstrip)


class ListItem(TerminalNode):
    '''List Item Class'''
    def _get_open(self):
        return '<li>'

    def _get_close(self):
        return '</li>'


class OrderedList(List):
    '''Shortcut Class of Ordered List'''
    def __init__(self, org_root, depth, start=1):
        super().__init__(org_root, depth, True, False, start)

    def _get_open(self):
        return '<ol>'

    def _get_close(self):
        return '</ol>'


class UnOrderedList(List):
    '''Shortcut Class of UnOrdered List'''
    def __init__(self, org_root, depth):
        super().__init__(org_root, depth, False, False)

    def _get_open(self):
        return '<ul>'

    def _get_close(self):
        return '</ul>'


class DefinitionList(List):
    '''Shortcut Class of Definition List'''
    def __init__(self, org_root, depth):
        super().__init__(org_root, depth, False, True)

    def _get_open(self):
        return '<dl>'

    def _get_close(self):
        return '</dl>'


class DefinitionListItem(Node):
    '''Definition List Item Class'''
    def __init__(self, org_root, title, description):
        super().__init__(org_root)
        self.children.append(DefinitionListItemTitle(org_root, title))
        self.children.append(DefinitionListItemDescription(org_root, description))

    def _get_open(self):
        return ''

    def _get_close(self):
        return ''


class DefinitionListItemTitle(TerminalNode):
    def _get_open(self):
        return '<dt>'

    def _get_close(self):
        return '</dt>'


class DefinitionListItemDescription(TerminalNode):
    def _get_open(self):
        return '<dd>'

    def _get_close(self):
        return '</dd>'


class Table(Node):
    '''Table Class'''
    def _get_open(self):
        return '<table>'

    def _get_close(self):
        return '</table>'


class TableRow(Node):
    '''Table Row Class'''
    def _get_open(self):
        return '<tr>'

    def _get_close(self):
        return '</tr>'


class TableCell(Node):
    '''Table Cell Class'''
    def html(self, br='', lstrip=False):
        '''Get HTML'''
        inner = br.join([child.html(br, True) for child in self.children])
        return ''.join([self._get_open(), inner,  self._get_close()])

    def _get_open(self):
        return '<td>'

    def _get_close(self):
        return '</td>'


class Link(TerminalNode):
    '''Link Class'''
    def __init__(self, org_root, href, title):
        self.href = href
        if title is None:
            title = href
        super().__init__(org_root, title)

    def _get_open(self):
        return '<a href="{}">'.format(self.href)

    def _get_close(self):
        return '</a>'


class Image(TerminalNode):
    '''Image Class'''
    def __init__(self, org_root, src, alt=""):
        self.src = src
        super().__init__(org_root, alt)

    def html(self, br=''):
        if self.values:
            return '<img src="{}" alt="{}">'.format(self.src, self.values[0]) + br
        else:
            return '<img src="{}">'.format(self.src) + br


class Org(object):
    '''The org-mode object'''
    regexps = {
        'whiteline': compile(Syntax.WHITELINE),
        'heading': compile(Syntax.HEADING),
        'blockquote_begin': compile(Syntax.QUOTE_BEGIN),
        'blockquote_end': compile(Syntax.QUOTE_END),
        'src_begin': compile(Syntax.SRC_BEGIN),
        'src_end': compile(Syntax.SRC_END),
        'orderedlist': compile(Syntax.ORDERED_LIST),
        'unorderedlist': compile(Syntax.UNORDERED_LIST),
        'definitionlist': compile(Syntax.DEF_LIST),
        'tablerow': compile(Syntax.TABLE_ROW),
        'internal_link': compile(Syntax.INTERNAL_LINK),
        'target': compile(Syntax.TARGET),
    }

    def __init__(self, text, default_heading=1, parent=None):
        self.text = text
        self.children = []
        if parent is None:
            self.parent = self
        else:
            self.parent = parent
        self.current = self
        self.bquote_flg = False
        self.src_flg = False
        self.default_heading = default_heading
        self.targets = {}  # Map of <<target>> to nodes
        self._parse(self.text)

    def create_target_id(self, target):
        index = len(self.targets) + 1
        target_id = f'target-{index}-{slugify(target.target_text)}'
        self.targets[target.target_text] = target
        return target_id
        
    def __str__(self):
        return 'Org(' + ' '.join([str(child) for child in self.children]) + ')'

    def _parse(self, text):
        text = text.splitlines()
        for line in text:
            if self.src_flg and not self.regexps['src_end'].match(line):
                self.current.append(Text(self, line, noparse=True))
                continue
            if self.regexps['heading'].match(line):
                m = self.regexps['heading'].match(line)
                while (not isinstance(self.current, Heading) and
                       not isinstance(self.current, Org)):
                    self.current = self.current.parent
                self._add_heading_node(Heading(
                    org_root=self,
                    depth=len(m.group('level')),
                    title=m.group('title'),
                    default_depth=self.default_heading))
            elif self.regexps['internal_link'].match(line):
                m = self.regexps['internal_link'].match(line)
                node = InternalLink(self, m.group('anchor'), m.group('title'))
                self.current.append(node)
            elif self.regexps['target'].match(line) and False:
                m = self.regexps['target'].match(line)
                target = m.group('target')
                node = Text(self, target)  # Could be a custom Target node if needed
                self.current.append(node)
                self.targets[target] = node  # Store for resolution
                node.is_target = True
            elif self.regexps['blockquote_begin'].match(line):
                self.bquote_flg = True
                m = self.regexps['blockquote_begin'].match(line)
                node = Blockquote(org_root=self, cite=m.group('cite'))
                self.current.append(node)
                self.current = node
            elif self.regexps['blockquote_end'].match(line):
                if not self.bquote_flg:
                    raise NestingNotValidError
                self.bquote_flg = False
                while not isinstance(self.current, Blockquote):
                    if isinstance(self.current, Org):
                        raise NestingNotValidError
                    self.current = self.current.parent
                self.current = self.current.parent
            elif self.regexps['src_begin'].match(line):
                self.src_flg = True
                m = self.regexps['src_begin'].match(line)
                node = CodeBlock(org_root=self, src_type=m.group('src_type'))
                self.current.append(node)
                self.current = node
            elif self.regexps['src_end'].match(line):
                if not self.src_flg:
                    raise NestingNotValidError
                self.src_flg = False
                self.current = self.current.parent
            elif self.regexps['orderedlist'].match(line):
                while isinstance(self.current, Paragraph):
                    self.current = self.current.parent
                m = self.regexps['orderedlist'].match(line)
                self._add_olist_node(m)
            elif self.regexps['definitionlist'].match(line):
                while isinstance(self.current, Paragraph):
                    self.current = self.current.parent
                m = self.regexps['definitionlist'].match(line)
                self._add_dlist_node(m)
            elif self.regexps['unorderedlist'].match(line):
                while isinstance(self.current, Paragraph):
                    self.current = self.current.parent
                m = self.regexps['unorderedlist'].match(line)
                self._add_ulist_node(m)
            elif self.regexps['tablerow'].match(line):
                m = self.regexps['tablerow'].match(line)
                self._add_tablerow(m)
            elif not line:
                if isinstance(self.current, Paragraph):
                    self.current = self.current.parent
            elif (not isinstance(self.current, Heading) and isinstance(self.current, Node)):
                if self.regexps['internal_link'].search(line):  # Inline links
                    self.current.append(Text(self, line))  # Let TerminalNode parse it
                elif self.regexps['target'].search(line):  # Inline target
                    self.current.append(Text(self, line))
                    m = self.regexps['target'].search(line)
                    self.targets[m.group('target')] = self.current
                else:
                    self.current.append(Text(self, line))
            else:
                node = Paragraph(org_root=self)
                self.current.append(node)
                self.current = node
                self.current.append(Text(self, line))
        if self.bquote_flg or self.src_flg:
            raise NestingNotValidError

    def _is_deeper(self, cls, depth):
        if isinstance(self.current, cls):
            return depth > self.current.depth
        return False

    def _is_shallower(self, cls, depth, eq=False):
        if isinstance(self.current, cls) and not eq:
            return depth < self.current.depth
        elif isinstance(self.current, cls) and eq:
            return depth <= self.current.depth
        else:
            return False

    def _add_heading_node(self, heading):
        while self._is_shallower(Heading, heading.depth, eq=True):
            self.current = self.current.parent
        self.current.append(heading)
        self.current = heading

    def _add_list_node(self, m, listclass=List):
        is_listclass = isinstance(self.current, listclass)
        depth = len(m.group('depth'))
        if self._is_deeper(listclass, depth) or not is_listclass:
            listnode = listclass(org_root=self, depth=len(m.group('depth')))
            self.current.append(listnode)
            self.current = listnode
        while self._is_shallower(listclass, depth):
            self.current = self.current.parent
        self.current.append(ListItem(self, m.group('item')))

    def _add_olist_node(self, m):
        self._add_list_node(m, listclass=OrderedList)

    def _add_ulist_node(self, m):
        self._add_list_node(m, listclass=UnOrderedList)

    def _add_dlist_node(self, m):
        is_definitionlist = isinstance(self.current, DefinitionList)
        depth = len(m.group('depth'))
        if self._is_deeper(DefinitionList, depth) or not is_definitionlist:
            listnode = DefinitionList(org_root=self, depth=len(m.group('depth')))
            self.current.append(listnode)
            self.current = listnode
        while (isinstance(self.current, DefinitionList) and
               len(m.group('depth')) < self.current.depth):
            self.current = self.current.parent
        self.current.append(
            DefinitionListItem(self, m.group('item'), m.group('desc')))

    def _add_tablerow(self, m):
        cells = [c for c in m.group('cells').split('|') if c != '']
        if not isinstance(self.current, Table):
            tablenode = Table(org_root=self)
            self.current.append(tablenode)
            self.current = tablenode
        rownode = TableRow(org_root=self)
        self.current.append(rownode)
        self.current = rownode
        for cell in cells:
            cellnode = TableCell(org_root=self)
            self.current.append(cellnode)
            self.current = cellnode
            self._parse(cell)
            self.current = self.current.parent
        self.current = self.current.parent

    def append(self, child):
        self.children.append(child)
        child.parent = self

    def resolve_links(self):
        # Build heading map
        heading_map = {}
        def collect_headings(node):
            if isinstance(node, Heading):
                heading_map[node.title] = f"#{slugify(node.title)}"
            if isinstance(node, Node) or node == self:
                for child in node.children:
                    collect_headings(child)
        collect_headings(self)

        # Resolve links
        def resolve_node(node):
            if isinstance(node, InternalLink):
                if node.anchor in self.targets:
                    node.resolved = True
                elif node.anchor in heading_map:
                    node.anchor = heading_map[node.anchor][1:]
                    node.resolved = True
                # Else: stays unresolved, renders as text
            if isinstance(node, Node) or node == self:
                for child in node.children:
                    resolve_node(child)
        resolve_node(self)

    def html(self, br=''):
        self.resolve_links()  # Run before rendering
        return br.join([child.html(br) for child in self.children])

def org_to_html(text, default_heading=1, newline=''):
    return Org(text, default_heading).html(newline)


