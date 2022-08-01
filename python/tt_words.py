#
# Word processing for HTML output
#
# This does the final processing on all Word Nodes which
# is basically all the text of the document.
#
# Since TaggedText{} strips all whitespace, the purpose
# here is to re-introduce whitespace around words.
#
# Since this processing step is intended for HTML display
# words need to be properly escaped from looking
# like HTML tags and such. Uses cgi.escape() for this.
#
# This processing step should occur pretty much last.
#
import taggedtext
import cgi

MAX_WORDS_PER_LINE = 20

#
# process all words
#
# A word will be preceed by a space and followed by a space:
#	1. If last word in the node then no trailing white space is present
#	2. If the word begins with punctuation then no leading space
#	3. If lines per word reached then trailing space is replaced with newline
#
# The main goal is to translate words. The rule is to ensure white
# space around words. Special handling for punctuation. Suprisingly
# the rules are simple for handling '.' period and other punctuation.
#
# The goal is to have decent spacing when other tags are
# invloved.
#
# wsflag is an array containing of a single boolean.
# Whenever a word is translated and not given a trailing whitespace
# this flag is set to True. Whenever the last word translated
# was given trailing whitespace, then this flag is False
#
def run_helper(root, wsflag):

	#
	# Returns TRUE for words that should not have beginning whitespace added
	# Usually things that end a sentence.
	#
	def is_no_begin_whitespace_word(word):
		return word[0] in '.?,:;!@%"\'})>]';

	#
	# Returns TRUE for words that should not have ending whitespace added
	# Usually punctuation that begins groupings.
	#
	def is_no_end_whitespace_word(word):
		return word[len(word)-1] in '("\'{<['

	#
	# 'wpl' - word per line
	#
	def process_word(child, wsflag, i, num_children, wpl):
		if is_no_begin_whitespace_word(child.word()):
			begin_txt = ""
		elif i == 0:
			if wsflag[0]:
				begin_txt = " "
			else:
				begin_txt = ""
		else:
			begin_txt = " "

		if is_no_end_whitespace_word(child.word()):
			end_txt = ""
			wsflag[0] = False   # here we don't want the next word to add a beginning space
		elif i+1 == num_children:
			end_txt = ""
			wsflag[0] = True
		elif (i+1) % wpl == 0:
			end_txt = "\n"
			wsflag[0] = False
		else:
			end_txt = " "
			wsflag[0] = False

		n = taggedtext.make_translated_node(
					child.filename(),
					child.lineno(),
					child.column(),
					begin_txt + cgi.escape( child.word() ),
					end_txt)

		child.morph(n)

	i = 0
	num_children = root.num_children()
	for child in root.children():
		if child.is_word():
			process_word(child, wsflag, i, num_children, MAX_WORDS_PER_LINE)
		else:
			run_helper(child, wsflag)
		i += 1

def run(root):
	run_helper(root, [False])
