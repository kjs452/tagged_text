#
#	TaggedText{}
# Also supports,
#	Tagged{Text}
# also,
#	Tagged{ ...anything.... }
#
# This second form will process any "Text". Like Tagged{FooBar Man}
#
import taggedtext

#
# The TaggedText logo
#
def run(root):
	root.translate_tag("TaggedText", "<tt><b>Tagged{</b>Text<b>}</b></tt>", "")
	root.translate_tag("Tagged", "<tt><b>Tagged{</b>", "<b>}</b></tt>")
