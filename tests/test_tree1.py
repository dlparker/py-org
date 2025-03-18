import json
from pathlib import Path
import pytest
from pyorg2.tree import (Root, Branch, Section, Heading, Text, Paragraph, BlankLine, TargetText,
                         LinkTarget, BoldText, ItalicText,
                         UnderlinedText, LinethroughText, InlineCodeText,
                         MonospaceText, Blockquote, CodeBlock, List,
                         ListItem, OrderedList, OrderedListItem, UnorderedList,
                         UnorderedListItem, DefinitionList, DefinitionListItem,
                         DefinitionListItemTitle, DefinitionListItemDescription,
                         Table, TableRow, TableCell, Link, Image, InternalLink)


def test_everything_1():
    inner_test_everything()
    
def test_everything_2():
    inner_test_everything(False)
    
def inner_test_everything(heading_on_first=True):

    root = Root('foo')
    heading_text = None
    if heading_on_first:
        heading_text = "Top Heading"
    top = Section(root.trunk, heading_text=heading_text)
    top_para = Paragraph(top)
    top_text = Text(top_para, "Some beautiful Text")
    target_text = TargetText(top_para, "Target 1") 
    first_blank = BlankLine(top)

    mid = Section(root.trunk, heading_text="Middle Section")
    mid_para_1 = Paragraph(mid)
    mid_text_1 = Text(mid_para_1, "In the meat now.")
    mid_text_2 = Text(mid_para_1, "And cookin.")
    mid_para_2 = Paragraph(mid)
    mid_text_3 = Text(mid_para_2, "Lot to say.")
    mid_text_4 = Text(mid_para_2, "Running on.")

    
    text_section = Section(root.trunk, heading_text="Text Section")
    text_para = Paragraph(text_section)
    btext1 = BoldText(text_para, "Should be bold!")
    itext1 = ItalicText(text_para, "Should be italics!")
    utext1 = UnderlinedText(text_para, "Should be underlined!")
    lttext1 = LinethroughText(text_para, "Should be strike through!")
    monottext1 = MonospaceText(text_para, "Should be monospace!")
    inlinecodetext1 = MonospaceText(text_para, "Should be inline code")
    codeblocktext1 = MonospaceText(text_para, "Should be code block")
    block_quote = Blockquote(text_para)
    bq_text = Text(block_quote, 'Should be in block quote')
    text_text_1 = Text(text_para, "That's all folks.")

    list_section = Section(root.trunk, heading_text="List Section")
    list1 = List(list_section)
    li1 = ListItem(list1, 1,  "List 1 item 1")
    li2 = ListItem(list1, 1, "List 1 item 2")
    li2a = ListItem(li2, 2,  "List 1 item 2-a")
    li2a1 = ListItem(li2a, 3, "List 1 item 2-a-1")

    olist_section = Section(root.trunk, heading_text="OrderedList Section")
    olist1 = OrderedList(olist_section)
    oli1 = OrderedListItem(olist1, 1, "List 1 item o-1")
    oli2 = OrderedListItem(olist1, 1, "List 1 item o-2")
    oli2a = OrderedListItem(oli2, 2, "List 1 item o-2-a")
    oli2a1 = OrderedListItem(oli2a, 3, "List 1 item o-2-a-1")

    ulist_section = Section(root.trunk, heading_text="UnorderedList Section")
    ulist1 = UnorderedList(ulist_section)
    uli1 = UnorderedListItem(ulist1, 1, "List 1 item u-1")
    uli2 = UnorderedListItem(ulist1, 1, "List 1 item u-2")
    uli2a = UnorderedListItem(uli2, 2, "List 1 item u-2-a")
    uli2a1 = UnorderedListItem(uli2a, 3, "List 1 item u-2-a-1")

    dlist_section = Section(root.trunk, heading_text="DictionaryList Section")
    dlist1 = DefinitionList(dlist_section)
    dli1_title = DefinitionListItemTitle(dlist1, [Text(root.trunk, "I1"),])
    # make a descripion with multiple text items and a TargetText
    # because that could happen!
    bits = [Text(root, "D1"),  TargetText(root, "Target 2"), Text(root, "D2")]
    dli1_desc = DefinitionListItemDescription(dlist1, bits)
    dli1_item = DefinitionListItem(dlist1, dli1_title, dli1_desc)

    table_section = Section(root.trunk, heading_text="Table Section")
    table1 = Table(table_section)
    t1r1 = TableRow(table1)
    t1r1c1 = TableCell(t1r1, [Text(root, "col 1"),])
    t1r1c2 = TableCell(t1r1, [Text(root, "col 2"),])
    t1r2 = TableRow(table1)
    t1r2c1 = TableCell(t1r2, [Text(root, "value 1"),])
    bits2 = [Text(root, "Value"),  TargetText(root, "Target 3"), Text(root, "2")]
    t1r2c2 = TableCell(t1r2, bits2)

    image_section = Section(root.trunk, heading_text="Image Section")
    image_1 = Image(image_section, "file::///foo.png", "a pretty picture")
    
    link_section = Section(root.trunk, heading_text="Link Section")
    link_1 = Link(link_section, "https://x.com", "Link to X")
    link_2 = InternalLink(link_section, "Target 3", "Internal link to Target 3")
    
    
    print(json.dumps(root, default=lambda o:o.to_json_dict(), indent=4))
    
