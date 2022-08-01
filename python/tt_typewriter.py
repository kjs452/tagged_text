# this replaced by tt_simple_tags.py
#
# TT{....}
#
import taggedtext

#
# Process typewriter tags
#
def run(root):
	root.translate_tag("TT", "<tt>", "</tt>")
