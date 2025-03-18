import pytest
from pyorg2.org import (NestingNotValidError, Org, org_to_html, Heading, Paragraph,
                         UnOrderedList, OrderedList, ListItem, DefinitionList, Text)

# TestOrg class converted to functions
def test_org():
    text = ''''''
    o = Org(text)
    assert str(o) == 'Org()'

def test_paragraph():
    text = '''line1
line2'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text Text))'

def test_paragraph_append_str():
    text = '''line1
line2'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text Text))'
    target = o.children[0]
    target.append("line3")
    assert isinstance(target.children[2], Text)
    assert "line3" in target.children[2].get_text()


def test_new_paragraph():
    text = '''para1-1
para1-2

para2-1
para2-2'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text Text) Paragraph(Text Text))'

def test_heading():
    text = '''* Heading1
** Heading2
*** Heading3
**** Heading4
***** Heading5-1
****** Heading6
***** Heading5-2'''
    o = Org(text)
    assert str(o) == 'Org(Heading1(Heading2(Heading3(Heading4(Heading5(Heading6()) Heading5())))))'

def test_slided_heading():
    text = '''* Heading2
** Heading3'''
    o = Org(text, default_heading=2)
    assert str(o) == 'Org(Heading2(Heading3()))'

def test_is_deeper_greater_depth():
    text = '''* Heading1
** Heading2'''
    o = Org(text)
    o.current = o.children[0]  # Set to Heading1
    assert o._is_deeper(Heading, 2)  # 2 > 1
    assert not o._is_deeper(Heading, 1)  # 1 == 1
    
def test_blockquote():
    text = '''#+BEGIN_QUOTE: http://exapmle.com
quoted line1
quoted line2
#+END_QUOTE'''
    o = Org(text)
    assert str(o) == 'Org(Blockquote(Text Text))'

def test_blockquote_with_some_decoration():
    text = '''#+BEGIN_QUOTE
=quoted line=
#+END_QUOTE'''
    o = Org(text)
    assert str(o) == 'Org(Blockquote(Text))'

def test_openless_blockquote():
    text = '''#+END_QUOTE'''
    with pytest.raises(NestingNotValidError):
        Org(text)

def test_endless_blockquote():
    text = '''#+BEGIN_QUOTE'''
    with pytest.raises(NestingNotValidError):
        Org(text)

def test_blockquote_with_cite():
    text = '''#+BEGIN_QUOTE: http://example.com/source
quoted line
#+END_QUOTE'''
    o = Org(text)
    assert str(o) == 'Org(Blockquote(Text))'
    html = o.html()
    assert html == '<blockquote cite="http://example.com/source">quoted line</blockquote>'

def test_src():
    text = '''#+BEGIN_SRC
source code
source code
#+END_SRC'''
    o = Org(text)
    assert str(o) == 'Org(CodeBlock(Text Text))'

def test_src_with_type():
    text = '''#+BEGIN_SRC python
source code
source code
#+END_SRC'''
    o = Org(text)
    assert str(o) == 'Org(CodeBlock(Text Text))'

def test_src_with_some_decoration():
    text = '''#+BEGIN_SRC
=source code=
+source code+
#+END_SRC'''
    o = Org(text)
    assert str(o) == 'Org(CodeBlock(Text Text))'

def test_openless_src():
    text = '''#+END_SRC'''
    with pytest.raises(NestingNotValidError):
        Org(text)

def test_endless_src():
    text = '''#+BEGIN_SRC'''
    with pytest.raises(NestingNotValidError):
        Org(text)

def test_orderedlist():
    text = '''1. listitem1 
2. listitem2
3) listitem3
4) listitem4'''
    o = Org(text)
    assert str(o) == 'Org(OrderedList(ListItem ListItem ListItem ListItem))'
    target = o.children[0]
    assert isinstance(target, OrderedList)
    assert target.html().startswith(target._get_open())

def test_nested_orderedlist():
    text = '''1. listitem1
2. listitem2
  1. shallowitem1
  2. shallowitem2
     1. deepitem1
     2. deepitem2
  3. shallowitem3
3. listitem3'''
    o = Org(text)
    assert str(o) == 'Org(OrderedList(ListItem ListItem OrderedList(ListItem ListItem OrderedList(ListItem ListItem) ListItem) ListItem))'
    target = o.children[0]
    assert isinstance(target, OrderedList)
    assert target.html().startswith(target._get_open())
    target2 = target.children[0]
    assert isinstance(target2, ListItem)
    assert target2.html().startswith(target2._get_open())
    target3 = target.children[2]
    assert isinstance(target, OrderedList)

def test_unorderedlist():
    text = '''- listitem1
- listitem2
+ listitem3
+ listitem4'''
    o = Org(text)
    assert str(o) == 'Org(UnOrderedList(ListItem ListItem ListItem ListItem))'
    target = o.children[0]
    assert isinstance(target, UnOrderedList)
    assert target.html().startswith(target._get_open())

def test_nested_unorderedlist():
    text = '''- listitem1
- listitem2
  + shallowitem1
  + shallowitem2
     - deepitem1
     - deepitem2
  + shallowitem3
- listitem3'''
    o = Org(text)
    assert str(o) == 'Org(UnOrderedList(ListItem ListItem UnOrderedList(ListItem ListItem UnOrderedList(ListItem ListItem) ListItem) ListItem))'
    target = o.children[0]
    assert isinstance(target, UnOrderedList)
    assert target.html().startswith(target._get_open())
    target2 = target.children[0]
    assert isinstance(target2, ListItem)
    assert target2.html().startswith(target2._get_open())
    target3 = target.children[2]
    assert isinstance(target, UnOrderedList)

def test_definitionlist():
    text = '''- listtitle1:: listdescription1
- listtitle2::listdescription2
- listtitle3 :: listdescription3
- listtitle4::listdescription4
+ listtitle5:: listdescription5
+ listtitle6::listdescription6
+ listtitle7 :: listdescription7
+ listtitle8::listdescription8'''
    o = Org(text)
    assert str(o) == 'Org(DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)))'
    target = o.children[0]
    assert isinstance(target, DefinitionList)
    assert target.html().startswith(target._get_open())

def test_nested_definitionlist():  # Fixed typo 'text_' to 'test_'
    text = '''- listitem1:: desc1
- listitem2 ::desc2
  + shallowitem1 :: shallowdesc1
  + shallowitem2::shallowdesc2
     - deepitem1::deepdesc1
     - deepitem2 :: deepdesc2
  + shallowitem3:: shallowdesc3
- listitem3 :: desc3'''
    o = Org(text)
    assert str(o) == 'Org(DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)) DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)))'
    target = o.children[0]
    assert isinstance(target, DefinitionList)
    assert target.html().startswith(target._get_open())

def test_table():
    text = '''| col1-1 | col2-1|col3-1 |col4-1|
| col1-2|col2-2 |col3-2| col4-2 |
|col1-3 |col2-3| col3-3 | col4-3|
|col1-4| col2-4 | col3-4|col4-4 |'''
    o = Org(text)
    assert str(o) == 'Org(Table(TableRow(TableCell(Text) TableCell(Text) TableCell(Text) TableCell(Text)) TableRow(TableCell(Text) TableCell(Text) TableCell(Text) TableCell(Text)) TableRow(TableCell(Text) TableCell(Text) TableCell(Text) TableCell(Text)) TableRow(TableCell(Text) TableCell(Text) TableCell(Text) TableCell(Text))))'

def test_link():
    text = '''[[http://example.com]]'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    text = '''[[http://example.com][example]]'''
    target = o.children[0].children[0]
    assert target.get_text() ==  'Link'
    assert target.html().startswith(target._get_open())
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'Link'
    assert target.html().startswith(target._get_open())
    text = '''hoge[[http://example.com]]fuga'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'hogeLinkfuga'
    assert target.html().startswith(target._get_open())

def test_image():
    text = '''[[picture.png]]'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'Image'
    assert target.html().startswith(target._get_open())

def test_image_with_alt():
    text = '''[[picture.png][picture no found]]'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'Image'
    html = target.html()
    assert html.startswith(target._get_open())
    assert "picture no found" in html

def test_link_and_image():
    text = '''hoge[[http://example.com]]fuga[[picture]]piyo'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'hogeLinkfugaImagepiyo'  
    assert target.html().startswith(target._get_open())
    text = '''hoge[[picture]]fuga[[http://example.com]]piyo'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'hogeImagefugaLinkpiyo'
    assert target.html().startswith(target._get_open())

def test_bold():
    text = '''hoge*bold*fuga'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'hogeBoldTextfuga'
    assert target.html().startswith(target._get_open())

def test_italic():
    text = '''hoge/italic/fuga'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() ==  'hogeItalicTextfuga'
    assert target.html().startswith(target._get_open())

def test_underlined():
    text = '''hoge_underlined_fuga'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() ==   'hogeUnderlinedTextfuga'
    assert target.html().startswith(target._get_open())
    
def test_linethrough():
    text = '''hoge+linethrough+fuga'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() ==  'hogeLinethroughTextfuga'
    assert target.html().startswith(target._get_open())

def test_inlinecode():
    text = '''hoge=code=fuga'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'hogeInlineCodeTextfuga'
    assert target.html().startswith(target._get_open())

def test_python_code_block():
    text = '''#+BEGIN_SRC python
python code
#+END_SRC'''
    o = Org(text)
    assert str(o) == 'Org(CodeBlock(Text))'
    target = o.children[0].children[0]
    html = target.html()
    assert html.startswith(target._get_open())
    assert "python code" in html
    assert "class=" in o.html()

def test_random_code_block():
    text = '''#+BEGIN_SRC 
blarch code
#+END_SRC'''
    o = Org(text)
    assert str(o) == 'Org(CodeBlock(Text))'
    target = o.children[0].children[0]
    html = target.html()
    assert html.startswith(target._get_open())
    assert "class=" not in o.html()


def test_monospace():
    text = '''hoge~monospace~fuga'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text))'
    target = o.children[0].children[0]
    assert target.get_text() == 'hogeMonospaceTextfuga'
    assert target.html().startswith(target._get_open())

def test_mix():
    text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3
#+BEGIN_QUOTE
quoted
- hoge
- fuga
#+END_QUOTE'''
    o = Org(text)
    assert str(o) == 'Org(Heading1(Paragraph(Text) Heading2(Paragraph(Text Text)) Heading2(Table(TableRow(TableCell(Text) TableCell(Text)) TableRow(TableCell(Text) TableCell(Text))) Heading3(Blockquote(Text UnOrderedList(ListItem ListItem))))))'

# TestOrgToHTML class converted
def test_html():
    text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3-1
#+BEGIN_QUOTE
quoted
=quoted_decorated=
#+END_QUOTE

*** header3-2
#+BEGIN_SRC python
python code
=hoge=
#+END_SRC'''
    o = Org(text)
    assert o.html() == '<h1>header1</h1><p>paraparapara</p><h2>header2-1</h2><p><img src="image">para<span style="font-weight: bold;">para</span>2<a href="http://example.com">hyperlink</a></p><h2>header2-2</h2><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table><h3>header3-1</h3><blockquote>quoted<code>quoted_decorated</code></blockquote><h3>header3-2</h3><pre><code class="python">python code=hoge=</code></pre>'

    
def test_slide_heading_html():
    text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3
#+BEGIN_QUOTE
quoted
#+END_QUOTE'''
    o = Org(text, default_heading=2)
    assert o.html() == '<h2>header1</h2><p>paraparapara</p><h3>header2-1</h3><p><img src="image">para<span style="font-weight: bold;">para</span>2<a href="http://example.com">hyperlink</a></p><h3>header2-2</h3><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table><h4>header3</h4><blockquote>quoted</blockquote>'

def test_inlinecode():
    text = '=inline text='
    o = Org(text)
    assert o.html() == '<p><code>inline text</code></p>'
    text = '=/inline italic text/='
    o = Org(text)
    assert o.html() == '<p><code>/inline italic text/</code></p>'
    text = '=<tag>='
    o = Org(text)
    assert o.html() == '<p><code>&lt;tag&gt;</code></p>'

# TestOrgToHTMLFunction class converted
def test_html_function():
    text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3-1
#+BEGIN_QUOTE
quoted
#+END_QUOTE
*** header3-2
- hoge
- fuga'''
    assert org_to_html(text) == '<h1>header1</h1><p>paraparapara</p><h2>header2-1</h2><p><img src="image">para<span style="font-weight: bold;">para</span>2<a href="http://example.com">hyperlink</a></p><h2>header2-2</h2><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table><h3>header3-1</h3><blockquote>quoted</blockquote><h3>header3-2</h3><ul><li>hoge</li><li>fuga</li></ul>'

def test_slide_heading_html_function():
    text = '''* header1
paraparapara
** header2-1
[[image]]
para*para*2[[http://example.com][hyperlink]]
** header2-2
| a | b |
| 1 | 2 |

*** header3
#+BEGIN_QUOTE
quoted
#+END_QUOTE'''
    assert org_to_html(text, default_heading=2) == '<h2>header1</h2><p>paraparapara</p><h3>header2-1</h3><p><img src="image">para<span style="font-weight: bold;">para</span>2<a href="http://example.com">hyperlink</a></p><h3>header2-2</h3><table><tr><td>a</td><td>b</td></tr><tr><td>1</td><td>2</td></tr></table><h4>header3</h4><blockquote>quoted</blockquote>'

def test_newline_html_function():
    text = '''* header1
paraparapara
hogehogehoge
- list1
- list2'''
    assert org_to_html(text, newline='\n') == '<h1>header1</h1><p>paraparapara\nhogehogehoge</p><ul><li>list1</li><li>list2</li></ul>'

def test_unclosed_blockquote_eof():
    text = '''#+BEGIN_QUOTE
quoted line'''
    with pytest.raises(NestingNotValidError):
        Org(text)  # bquote_flg True at end

def test_unclosed_src_eof():
    text = '''#+BEGIN_SRC python
code line'''
    with pytest.raises(NestingNotValidError):
        Org(text)  # src_flg True at end

def test_blockquote_end_without_start():
    text = '''text
#+END_QUOTE'''
    with pytest.raises(NestingNotValidError):
        Org(text)  # bquote_flg False, mismatched end

def test_nested_blockquote_end_without_start():
    text = '''* Heading 1
#+BEGIN_QUOTE
** Heading 2
#+END_QUOTE'''
#+END_QUOTE'''
    with pytest.raises(NestingNotValidError):
        Org(text)  # bquote_flg False, mismatched end

def test_src_end_without_start():
    text = '''text
#+END_SRC'''
    with pytest.raises(NestingNotValidError):
        Org(text)  # src_flg False, mismatched end

def test_src_end_after_block_start():
    text = '''text
#+BEGIN_SRC
#+BEGIN_QUOTE
#+END_SRC'''
    o = Org(text)  # should ignore block quote start
    assert str(o) == 'Org(Paragraph(Text CodeBlock(Text)))'

def test_orderedlist_after_paragraph():
    text = '''para1
1. listitem1'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text) OrderedList(ListItem))'
    # Parse sets current to Paragraph, then unwinds to Org for OrderedList
    assert isinstance(o.children[0], Paragraph)
    assert isinstance(o.children[1], OrderedList)

def test_definitionlist_after_paragraph():
    text = '''para1
- title1 :: desc1'''
    o = Org(text)
    assert str(o) == 'Org(Paragraph(Text) DefinitionList(DefinitionListItem(DefinitionListItemTitle DefinitionListItemDescription)))'
    # Parse unwinds from Paragraph to Org for DefinitionList
    assert isinstance(o.children[0], Paragraph)
    assert isinstance(o.children[1], DefinitionList)        


def test_internal_link_explicit_1():
    text = '''<<target>>
[[#target][Go to target]]'''
    o = Org(text)
    assert o.html() == 'target<a href="#target">Go to target</a>'

def test_internal_link_explicit_2():
    text = '''foo bar bee
<<target>>
[[#target][Go to target]]'''
    o = Org(text)
    print('\n', o.html())
    assert 'target<a href="#target">Go to target</a>' in o.html() 

def test_internal_link_explicit_in_quote():
    text = '''#+BEGIN_QUOTE
<<target>>
[[#target][Go to target]]
#+END_QUOTE'''
    o = Org(text)
    print("\n", o.html())
    assert '<a href="#target">Go to target</a>' in o.html()
    
def test_internal_link_heading():
    text = '''* My Heading
[[#My Heading][Go to heading]]'''
    o = Org(text)
    assert o.html() == '<h1>My Heading</h1><a href="#my-heading">Go to heading</a>'

def test_internal_link_unresolved():
    text = '''[[#missing][Go nowhere]]'''
    o = Org(text)
    assert o.html() == 'Go nowhere'  # No <a> tag    

def test_explicit_target_styles():
    text = '''* A heading <<target1>>
some text after the heading <<target2>>
1. An ordered List <<target3>>
2. Foo

- An unordered list
- with some text
  - and a target inside <<target4>>
'''
    o = Org(text)
    print('\n', o.html())
