#
# Code<<_EOF_
# 	printf("Hi!");
# _EOF_
#
import taggedtext
import cgi

#
# Process code here documents
#
def run(root):
	def f(heredoc):
		return cgi.escape(heredoc)

	root.translate_heredoc("Code", "\n<pre>\n", "</pre>\n", f)
