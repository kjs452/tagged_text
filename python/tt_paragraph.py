# this replaced by tt_simple_tags.py
#
# P{....}
#
import taggedtext

#
# Process paragraph tags
#
def run(root):
	root.translate_tag("P", "<p>\n", "\n</p>\n")
