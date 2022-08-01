# this replaced by tt_simple_tags.py
#
# SC{This is small Caps}
#
import taggedtext

#
# Process small caps tag
#
def run(root):
	root.translate_tag(
			"SC",
			'<font style="font-variant: small-caps">',
			'</font>' )
