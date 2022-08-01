#
# The handles simple tags that map to HTML tags
#
# Tags handles by this function:
#
#	B{....}			Bold Text
#	I{....}			Italics
#	TT{...}			Typewriter text
#	UND{....}		Underline
#	STRIKE{.....}	Strike-thru
#	NOWRAP{....}	Prevent a phrase from being line wrapped
#	P{...}			Paragraph
#	SC{This is small Caps}		Small Caps
#
#	Title{....}				Major Title
#	Section{....}			Section Title
#	SubSection{....}		Sub Section Title
#	SubSubSection{....}		Sub Sub Section Title
#	TitleBox{....}			Box around titlee
#	BlockQuote{....}		Quote text
#	"{....}					"Quote text"
#	'{....}					'Single Quoted text'
#
# 	TableOfContents{}
#		Generates a clickable table of contents for this page
#
import taggedtext

#
# Table of Contents as derived by the occurance of the Title, Section, SubSection
# and SubSubSection titles
#
# Each element of this list is structured thusly,
#
#	{
#		'node':	taggedtext.Node
#		'level':	0,		# 0 = title, 1=section, 2=subsection, 3=subsubsection
#		'ref': 		23		# a counter number to form the reference 
#	}
#
#
COUNTER = 1
TOC = [ ]

def translate(n, begin_txt, end_txt):
	nn = taggedtext.make_translated_node(
				n.filename(),
				n.lineno(),
				n.column(),
				begin_txt,
				end_txt)
	nn.take_children(n)
	return [nn]

def translate_toc(n, level, begin_txt, end_txt):
	global COUNTER
	bt = '<A NAME="TOC%d"></A>%s' % (COUNTER, begin_txt)

	nn = taggedtext.make_translated_node(
				n.filename(),
				n.lineno(),
				n.column(),
				bt,
				end_txt)
	nn.take_children(n)

	t = { 'node': n.clone(), 'level': level, 'ref': COUNTER }
	TOC.append(t)
	COUNTER += 1

	return [nn]

def TableOfContents(n):
	# nestingStack.append(e)		push
	# nestingStack.pop()			pop
	# nestingStack[-1]				top
	nestingStack = []

	curLevel = 0

	lst = taggedtext.make_translated_node(
			n.filename(),
			n.lineno(),
			n.column(),
			"\n<p>\n<ul>\n",
			"\n</ul>\n</p>\n" )

	nestingStack.append(lst)

	for t in TOC:
		tn = t['node']
		ref = t['ref']
		level = t['level']

		if level > curLevel:
			for i in range(curLevel, level):
				lst = taggedtext.make_translated_node(
					n.filename(),
					n.lineno(),
					n.column(),
					"\n<p>\n<ul>\n",
					"\n</ul>\n</p>\n" )

				top = nestingStack[-1]
				top.add_child_back(lst)
				nestingStack.append(lst)
				
		elif level < curLevel:
			for i in range(level, curLevel):
				nestingStack.pop()

		curLevel = level

		li = taggedtext.make_translated_node(
			tn.filename(),
			tn.lineno(),
			tn.column(),
			'\n<li><A HREF="#TOC%d">' % (ref),
			'</A></li>\n' )

		for c in tn.children():
			li.add_child_back(c)

		top = nestingStack[-1]
		top.add_child_back(li)

	for i in range(0, curLevel):
		nestingStack.pop()

	top = nestingStack.pop()

	return [top]

#
# Process bold tags
#
def run(root):
	global COUNTER
	global TOC

	COUNTER = 1
	TOC = []

	eval_functions = {
		'B':		( lambda root: translate(root, '<b>', '</b>') ),
		'I':		( lambda root: translate(root, '<i>', '</i>') ),
		'TT':		( lambda root: translate(root, '<tt>', '</tt>') ),
		'UND':		( lambda root: translate(root, '<u>', '</u>') ),
		'OVR':		( lambda root: translate(root, '<span class="OverLine">', '</span>') ),
		'STRIKE':	( lambda root: translate(root, '<span class="StrikeThrough">', '</span>') ),
		'NOWRAP':	( lambda root: translate(root, '<span class="NoWrap">', '</span>') ),
		'P':		( lambda root: translate(root, '<p>\n', '\n</p>\n') ),

		'SC':		( lambda root: translate(root, 
									'<font style="font-variant: small-caps">',
									'</font>' ) ),

		'Title':			( lambda root: translate_toc(root, 0, "<center><h1>", "</h1></center>") ),
		'Section':			( lambda root: translate_toc(root, 1,"<h1>", "</h1>") ),
		'SubSection': 		( lambda root: translate_toc(root, 2, "<h2>", "</h2>") ),
		'SubSubSection': 	( lambda root: translate_toc(root, 3, "<h3>", "</h3>") ),
		'TitleBox':			( lambda root: translate(root, "<h2>", "</h2>") ),
		'BlockQuote': 		( lambda root: translate(root, "<blockquote>", "</blockquote>") ),
		'"': 				( lambda root: translate(root, "&ldquo;", "&rdquo;") ),
		'\'': 				( lambda root: translate(root, "&lsquo;", "&rsquo;") ),
	}

	root.eval(eval_functions)

	eval_functions_pass2 = {
		'TableOfContents':	TableOfContents,
	}

	root.eval(eval_functions_pass2)

#
# The Blog{} mechanism clears this before each rendering
#
def clear_toc():
	TOC = [ ]
