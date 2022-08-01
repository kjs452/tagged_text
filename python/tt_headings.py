# this replaced by tt_simple_tags.py
#
# Some misc. tags for Titles, Headings, Sections, SubSection
# and fancy Title Box
#
#
#
import taggedtext

def run_title(root):
	root.translate_tag("Title", "<center><h1>", "</h1></center>")

def run_section(root):
	root.translate_tag("Section", "<h1>", "</h1>")

def run_subsection(root):
	root.translate_tag("SubSection", "<h2>", "</h2>")

def run_subsubsection(root):
	root.translate_tag("SubSubSection", "<h3>", "</h3>")

# seems to be same as subsection
def run_titlebox(root):
	root.translate_tag("TitleBox", "<h2>", "</h2>")

#  BlockQuote{xxx}
def run_blockquote(root):
	root.translate_tag("BlockQuote", "<blockquote>", "</blockquote>")

def run(root):
	run_title(root)
	run_section(root)
	run_subsection(root)
	run_subsubsection(root)
	run_titlebox(root)
	run_blockquote(root)

