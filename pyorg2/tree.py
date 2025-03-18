
class Root:
    """ The base of the tree. The source designates the first source file or buffer parsed to
    produce the tree. Normally this should be a pathlike object, but
    other things are possible.
    """ 
    def __init__(self, source):
        self.source = source
        self.node_id = 0
        # Always exactly one branch as trunk, others attach to it or each other
        self.trunk = Branch(self, source)

    def new_node_id(self):
        self.node_id += 1
        return self.node_id
    
    def to_json_dict(self):
        res = dict(cls=str(self.__class__),
                   props=dict(source=self.source,
                   trunk=self.trunk.to_json_dict()))
        return res

    def to_html(self, wrap=True, make_pretty=True):
        indent_level = 0
        lines = []
        if wrap:
            lines.append("<html>")
            lines.append("<body>")
        lines.extend(self.trunk.to_html(indent_level))
        lines.append("</body>")
        if make_pretty:
            return "\n".join(lines)
        stripped = []
        for line in lines:
            stripped.append(line.strip())
        return "".join(lines)
    
    def __str__(self):
        return f"root from source {self.source}"
    
class Branch:
    """ For single file parsing, having a root to the tree is enough, but when combining
    files it is useful to be able to completely parse each file and then combine them into
    a bigger tree. So we use the branch concept to make that work. The source designates the
    first file or buffer parsed to produce the tree. Normally this should be a pathlike object.
    """

    def __init__(self, root, source, parent=None):
        self.root = root
        self.node_id = root.new_node_id()
        self.source = source
        if parent is None:
            parent = root
        self.parent = parent # could be attatched to a trunk branch, not the root
        self.children = []

    def add_node(self, node):
        if node not in self.children:
            self.children.append(node)
        
    def to_json_dict(self):
        # don't include back links, up the tree
        res = dict(cls=str(self.__class__),
                   props=dict(node_id=self.node_id,
                   source=self.source, nodes=[n.to_json_dict() for n in self.children]))
        return res

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("div", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for node in self.children:
            lines.extend(node.to_html(indent_level))
        lines.append(padding + '</div>')
        return lines
    
    def __str__(self):
        return f"(self.node_id) branch from source {self.source}"
    
class Node:
    
    def __init__(self, parent, auto_add=True):
        self.parent = parent
        self.root = self.find_root()
        self.node_id = self.root.new_node_id()
        self.link_targets = []
        if auto_add and self.parent != self.root:
            self.parent.add_node(self)

    def find_root(self):
        parent = self.parent
        while parent is not None and not isinstance(parent, Root):
            parent = parent.parent
        if isinstance(parent, Root):
            return parent
        raise Exception("cannot find root!")
    
    def add_link_target(self, target):
        self.link_targets.append(target)

    def move_to_parent(self, parent):
        if self.parent == parent:
            return
        if not isinstance(self.parent, Root):
            try:
                self.parent.children.remove(self)
            except ValueError:
                pass
        self.parent = parent
        self.parent.add_node(self)
        
    def to_json_dict(self):
        # don't include back links, up the tree
        res = dict(cls=str(self.__class__),
                   props=dict(node_id=self.node_id,
                   link_targets=[lt.to_json_dict() for lt in self.link_targets]))
        return res
        
    def __str__(self):
        msg = f"({self.node_id}) {self.__class__.__name__} "
        msg += f"{self.parent.children.index(self)} child of obj {self.parent.node_id}"
        return msg
    
class BlankLine(Node):
    """ This node records the presence of a blank line in the original text. This
    allows format converters to preserve the original vertical separation of text if
    so desired. They often also mark the end of other elements, such as tables, lists,
    etc.
    """
    def __init__(self, parent):
        super().__init__(parent)
    
    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        line1 = " " * indent_level  * 4
        line1 += "<br>"
        return [line1,]
    
class Container(Node):
    """ This node contains one or more other nodes but does not directly contain text."""
    def __init__(self, parent, content=None):
        super().__init__(parent)
        self.children = []
        if content:
            for item in content:
                item.move_to_parent(self)
        
    def add_node(self, node):
        if node not in self.children:
            self.children.append(node)
        
    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("div", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for child in self.children:
            lines.extend(child.to_html(indent_level))
        lines.append(padding + '</div>')
        return lines
    
    def to_json_dict(self):
        # don't include back links, up the tree
        res = super().to_json_dict()
        res['props']['children']  = [c.to_json_dict() for c in self.children]
        return res
    
class Section(Container):
    """ This type of Container starts with a heading, or at the beginning of the file.
    It may have a set of properties from a "drawer". 
    """
    def __init__(self, parent, heading_text):
        super().__init__(parent)
        par = self.parent
        wraps = 0
        while not isinstance(par, Branch):
            if isinstance(par, Section):
                wraps += 1
            par = par.parent
        level = wraps + 1
        self.heading = Heading(parent=self, text=heading_text, level=level)

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("div", indent_level, self)
        line1 += ">"
        lines.append(line1)
        if self.heading:
            lines.extend(self.heading.to_html(indent_level))
        for node in self.children:
            lines.extend(node.to_html(indent_level))
        lines.append(padding + '</div>')
        return lines
    
    def to_json_dict(self):
        if self.heading:
            res = dict(cls=str(self.__class__),
                   props=dict(heading=self.heading.to_json_dict()))
            res['props'].update(super().to_json_dict()['props'])
        else:
            res = super().to_json_dict()
        return res
        
class Paragraph(Container):
    """ A content container that is visually separated from the surrounding content
    but does not start with a header. Cannot be the top level container, so it
    must have a parent.
    """
    def __init__(self, parent):
        super().__init__(parent)
        
        
class Text(Node):
    """ A node that has actual content, meaning text. Must have a parent."""
    def __init__(self, parent, text):
        super().__init__(parent)
        self.text = text

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("span", indent_level, self)
        line1 += f"'>{self.text}</span>"
        return [line1,]
    
    def to_json_dict(self):
        res = super().to_json_dict()
        res['props']['text'] = self.text
        return res
        
class Heading(Node):
    """ An org heading, meaning it starts with one or more asterisks. Always starts a new
    Section, but not all Sections start with a heading. May have a parent, may not.
    """
    def __init__(self, parent, text, level=1,):
        super().__init__(parent, auto_add=False)
        self.text = text
        self.level = level
        self.properties = {}

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open(f"h{self.level}", indent_level, self)
        line1 += f">{self.text}</h{self.level}>"
        return [line1,]
        
    def to_json_dict(self):
        res = super().to_json_dict()
        res['props']['text'] = self.text
        res['props']['properties'] = self.properties
        res['props']['level'] = self.level
        return res
        
class TargetText(Text):
    """ A node that has actual text content, but with special significance because
    it can be the target of a link. This is for the <<link-to-text>> form which
    needs special processing on conversion to other formats. 
    """
    def __init__(self, parent, text):
        super().__init__(parent, text)


class LinkTarget():
    """
    This is used to record the fact that a node has a link-to-text associated with it so that
    it can be the target of a link. It is not a node, but has a reference to the node that
    is the actual target. This is for the various forms other than explicit text including
    the named element form which is implemented in the TargetText class.

    The supported linkable forms include the explicit name form when can proceed
    any element:

    #+Name: link-to-text
    | col1 | col2 |
    | a    | b    |

    and the custom id form:
    
    * Section Header
    :PROPERTIES:
    :CUSTOM_ID: link-to-text
    :END:
    """
    def __init__(self, target_node, target_text):
        self.target_node = target_node
        self.target_text = target_text
        self.target_node.add_link_target(self)
        
    def to_json_dict(self):
        res = dict(target_node=str(self.target_node), target_text=self.target_text)
        return res


class BoldText(Text):
    pass

class ItalicText(Text):
    pass

class UnderlinedText(Text):
    pass

class LinethroughText(Text):
    pass

class InlineCodeText(Text):
    pass

class MonospaceText(Text):
    pass

class Blockquote(Container):
    pass

class CodeBlock(Text):
    pass

class List(Container):
    pass

class ListItem(Container):

    def __init__(self, parent, level=1, plain_text=None):
        super().__init__(parent)
        if plain_text:
            self.text = Text(self, plain_text)
        self.text = None
        self.level = level

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("li", indent_level, self)
        line1 += ">"
        lines.append(line1)
        if self.text:
            lines.extend(self.text.to_html(intent_level))
        else:
            for node in self.children:
                lines.extend(node.to_html(indent_level))
        lines.append(padding + '</li>')
        return lines

    def to_json_dict(self):
        ## fiddle the resluts around to make it easier to understand
        ## by getting the children last
        superres = super().to_json_dict()
        lres = dict(level=self.level)
        lres.update(superres['props'])
        res = dict(cls=superres['cls'], props=lres)
        return res
    
class OrderedList(List):

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("ol", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for node in self.children:
            lines.extend(node.to_html(indent_level))
        lines.append(padding + '</ol>')
        return lines


class OrderedListItem(ListItem):
    pass

class UnorderedList(List):

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("ul", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for node in self.children:
            lines.extend(node.to_html(indent_level))
        lines.append(padding + '</ul>')
        return lines


class UnorderedListItem(ListItem):
    pass

class DefinitionList(List):

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("dl", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for node in self.children:
            lines.extend(node.to_html(indent_level))
        lines.append(padding + '</dl>')
        return lines


class DefinitionListItem(ListItem):

    def __init__(self, parent, title, description):
        super().__init__(parent)
        # This is pretty ugly, but it is that way
        # because the stuff it is manipulating is optimized
        # for the common case. This is not the common case.
        # Let this be ugly instead of spreading it far and wide
        title.move_to_parent(self)
        description.move_to_parent(self)
        self.children = []
        self.title = title
        self.description = description

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        lines.extend(self.title.to_html(indent_level))
        lines.extend(self.description.to_html(indent_level))
        return lines

    def to_json_dict(self):
        ## fiddle the resluts around to make it easier to understand
        ## by getting the children last
        superres = super().to_json_dict()
        lres = dict(title=self.title.to_json_dict(),
                    description=self.description.to_json_dict())
        lres.update(superres['props'])
        res = dict(cls=superres['cls'], props=lres)
        return res
    
class DefinitionListItemTitle(Container):

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("dt", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for child in self.children:
            lines.extend(child.to_html(indent_level))
        lines.append(padding + '</dt>')
        return lines

class DefinitionListItemDescription(Container):

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("dd", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for child in self.children:
            lines.extend(child.to_html(indent_level))
        lines.append(padding + '</dd>')
        return lines

class Table(Container):

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("table", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for child in self.children:
            lines.extend(child.to_html(indent_level))
        lines.append(padding + '</table>')
        return lines

class TableRow(Container):

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("tr", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for child in self.children:
            lines.extend(child.to_html(indent_level))
        lines.append(padding + '</tr>')
        return lines

class TableCell(Container):

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("td", indent_level, self)
        line1 += ">"
        lines.append(line1)
        for child in self.children:
            lines.extend(child.to_html(indent_level))
        lines.append(padding + '</td>')
        return lines


class Link(Container):

    def __init__(self, parent, target_text, display_text=None):
        super().__init__(parent)
        self.children = []
        self.target_text = target_text
        self.display_text = display_text

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("a", indent_level, self)
        line1 += f' href="{self.target_text}">'
        lines.append(line1)
        if self.display_text:
            lines.append(padding + "   " + self.display_text)
        lines.append(padding + '</a>')
        return lines

    def to_json_dict(self):
        ## fiddle the resluts around to make it easier to understand
        ## by getting the children last
        superres = super().to_json_dict()
        lres = dict(target_text=self.target_text, display_text=self.display_text)
        lres.update(superres['props'])
        res = dict(cls=superres['cls'], props=lres)
        return res

class Image(Node):
    
    def __init__(self, parent, src_text, alt_text=None):
        super().__init__(parent)
        self.src_text = src_text
        self.alt_text = alt_text

    def to_html(self, indent_level):
        lines = []
        indent_level += 1
        padding, line1 = setup_tag_open("img", indent_level, self)
        line1 += f' src="{self.src_text}"'
        if self.alt_text:
            line1 += f' alt="{self.alt_text}>"'
        line1 += '</img>'
        return [line1,]

    def to_json_dict(self):
        ## fiddle the resluts around to make it easier to understand
        ## by getting the children last
        superres = super().to_json_dict()
        lres = dict(src_text=self.src_text, alt_text=self.alt_text)
        lres.update(superres['props'])
        res = dict(cls=superres['cls'], props=lres)
        return res

class InternalLink(Link):
    pass

def setup_tag_open(tag, indent_level, obj):
    padding = " " * indent_level  * 4
    line1 = padding
    line1 += f'<{tag} id="obj-{obj.node_id}" '
    line1 += f'class="org-auto-{obj.__class__.__name__}"'
    return padding, line1
    



    
    
