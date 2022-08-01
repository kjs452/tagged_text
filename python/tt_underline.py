# this replaced by tt_simple_tags.py
#
# UND{....}
#
# OVR{....} <--- overline
#
# STRIKE{....} <--- strike through
#
# NOWRAP{....} <--- stop word wrapping for a bunch of text.
#
import taggedtext

#
# Process underline tags, and friends
#
def run(root):
	root.translate_tag("UND", "<u>", "</u>")
	root.translate_tag("OVR", '<span class="OverLine">', '</span>')
	root.translate_tag("STRIKE", '<span class="StrikeThrough">', '</span>')
	root.translate_tag("NOWRAP", '<span class="NoWrap">', '</span>')

