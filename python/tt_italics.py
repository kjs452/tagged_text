# this replaced by tt_simple_tags.py
#
# I{....}
#
import taggedtext

#
# Process italics tags
#
def run(root):
	root.translate_tag("I", "<i>", "</i>")
