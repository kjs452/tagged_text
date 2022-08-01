#
# HDBAR{
#	Junk<<_EOF_
#            x
#           / \
#         ba   b
#          |   |
#          d   e
#	_EOF_
# }
#
# LINENUMBERS{
#	Code<<_FFF_
#		if( 1 2 3 ) {
#			printf("fsdjkfsdjf");
#		}
# _FFF_
# }
#
#
import taggedtext

#
# Add a vertical bar to the beginning of each here doc line
# encountered. Useful for revealing the left white space
# trimming algorithm used by TaggedText
#
def run(root):

	def tt_hdbar_helper(root, in_hdbar, in_linenumbers):

		if root.is_tag_named("HDBAR"):
			in_hdbar = True

		elif root.is_tag_named("LINENUMBERS"):
			in_linenumbers = True

		elif root.is_heredoc():
			lines = root.heredoc_content()

			for i in range(len(lines)):
				line = lines[i]

				prefix = ""

				if in_linenumbers:
					prefix = ("%3d: " % (i+1))

				if in_hdbar:
					prefix = prefix + "|"

				if len(prefix) > 0:
					lines[i] = prefix + line

		for child in root.children():
			tt_hdbar_helper(child, in_hdbar, in_linenumbers)

	tt_hdbar_helper(root, False, False)
