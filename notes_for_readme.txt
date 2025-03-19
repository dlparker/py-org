
1. The block quote type in org mode exports to html poorly. The cite
attribute of the blockqoute html element does nothing. There is a lot
of confusion on how to use block quotes and some strange issues around
associating them with author names, citations, etc. It makes no sense
to put that stuff inside the quote, because it is not part of the quote.
Also, people commonly say the cite should be an url to the source,
by the standards indicate it should be the name of the work, definitely
not the author. 
Probably should build some kind of special structure to allow the cite to
show up above or below the block quote. One commented suggested an <aside>
element would produce the desired visual effect and still work for
accessibility. Maybe a <div><aside>quote</aside><cite>Name Of Work</cite>
<span>Author Name</span><a href="url if you have it"></div>

2. It is important to tell the users that this tool is not intende to replace
org mode export to html (or LaTex, or whatever). It is only meant to allow
export of org roam files. It is likely to be deficient in features and completeness
compared to directly exporting from org mode. Since there isn't any export tool
that properly handles roam links between files, you need something like this
to get that effect.

