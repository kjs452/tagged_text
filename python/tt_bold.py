# this replaced by tt_simple_tags.py
#
# B{....}
#
import taggedtext

#
# Process bold tags
#
def run(root):
	root.translate_tag("B", "<b>", "</b>")
