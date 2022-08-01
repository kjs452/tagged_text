#
# Set{TaggedText{Tagged Text}}
# Set{Creator{Ken Stauffer}}
# Set{CreatedDate{Decemeber 7, 2016}}
# Set{Location{New York, NY}}
#
# Title{TaggedText{}}
#
# Section{What is TagedText{}?}
# P{
# This is a python package that will parse specially formatted
# text files and convert them into a Tagged Text Tree structure.
#
# It is an attempt to be a simple way to structure text documents
# for processing by other tools to convert text into nicely formated
# documents for HTML, PDF, etc....
# }
#
#
import re
import json
import copy
import sys

######################################################################
# Exception classes:
#	Rather invent wacky class names for each and
# every exception. I just increment the error code here.
# For each location where an exception needs to be raised
# just pick a new ERRxxx code number. They way each exception
# refers to a unique location in the code.
#
class ERR_BASE(Exception):
	pass

class ERR001(ERR_BASE):
	pass

class ERR002(ERR_BASE):
	pass

class ERR003(ERR_BASE):
	pass

class ERR004(ERR_BASE):
	pass

class ERR005(ERR_BASE):
	pass

class ERR006(ERR_BASE):
	pass

class ERR007(ERR_BASE):
	pass

class ERR008(ERR_BASE):
	pass

class ERR009(ERR_BASE):
	pass

class ERR010(ERR_BASE):
	pass

class ERR011(ERR_BASE):
	pass

class ERR012(ERR_BASE):
	pass

######################################################################
#
# These are the token types
#
TK_EOF         = 1
TK_ERROR       = 2
TK_WORD        = 3
TK_TAG_BEGIN   = 4
TK_TAG_END     = 5
TK_HEREDOC     = 6

#
# Token names, this list should be kept in
# correspondence with the token types above.
#
TokenTypeNames = [
	None,
	"EOF",
	"ERROR",
	"WORD",
	"TAG_BEGIN",
	"TAG_END",
	"HEREDOC"
]

######################################################################
#
# Tag names can consist of any sequence of characters consisting of
# ASCII letters, digits and most punctuation characters excluding '<' '\' '{' '}'
#
IdentPattern = r'[a-zA-Z0-9!@#$%\^&*_\-+=?/"\'.>\[\]|~,:;,`]+'
IdentRegularExpression = re.compile('^' + IdentPattern + '$')

######################################################################
#
# The HereDoc terminiation string is just a tag name, it can
# be surrounded by whitespace
#
HereDocTerminatorPattern = r'\s*(%s)\s*' % (IdentPattern)
HereDocTerminatorRegularExpression = re.compile('^' + HereDocTerminatorPattern + '$')

######################################################################
#
# This helps collect the leading whitespace characters at the start
# of the line in a here document. The common white space prefix
# chararacters are chopped from each line.
#
LeadingWhiteSpacePattern = r'^(\s*).*$'
LeadingWhiteSpaceRegularExpression = re.compile(LeadingWhiteSpacePattern)

######################################################################
#
# This helps identify a safe heredoc termination label
# that is unique
#
HeredocTermLabel = r'^(\s*)_EOF_[0-9]+(\s*)$'
HeredocTermLabelRegularExpression = re.compile(HeredocTermLabel)

######################################################################
#
# a token obtained from an input stream. Contains
# the file location, as well as a string property and of course
# a token type. The strlist is used for the TK_HEREDOC token type.
#
class Token:
	def __init__(self, ttype, lineno, column, str, strlist):
		self.ttype = ttype
		self.lineno = lineno
		self.column = column
		self.str = str
		self.strlist = strlist

	def __repr__(self):
		name = TokenTypeNames[self.ttype]
		return "Token type: %s, Line: %d, Column: %d, Str: '%s'" % (
			name,
			self.lineno+1,
			self.column+1,
			self.str )

######################################################################
# Tokenizer:
# Once created, get_token() is called to return
# sucessive tokens that have been obtained from the input 'f'
#
# TK_EOF
# TK_ERROR
# TK_WORD
# TK_TAG_BEGIN
# TK_TAG_END
# TK_HEREDOC
#
class Tokenizer:
	def __init__(self, f):
		self.f = f
		self.lineno = 0
		self.column = 0
		self.got_undo = False
		self.prev_lineno = 0
		self.prev_column = 0
		self.prev_ch = ''

	# respected white space characters
	def is_white(self, ch):
		return ch == ' ' or ch == '\t' or ch == '\n' or ch == '\r'

	def is_escapable(self, ch):
		return ch == '\\' or ch == '{' or ch == '}' or ch == '<'

	def is_bad_char(self, ch):
		return ord(ch) < ord(' ') and not self.is_white(ch)

	def make_eof_token(self):
		return Token(TK_EOF, self.lineno, self.column, "EOF", [])

	def make_tag_begin_token(self, word, lineno, column):
		tag = ''.join(word)
		m = IdentRegularExpression.match(tag)
		if m == None: 
			if len(tag) == 0:
				msg = "Missing tag name or missing escape '\\' before '{'."
			else:
				msg = "Illegal tag name '%s' ('<' '\\' '{' '}' are not allowed)." % (tag)
			return Token(TK_ERROR, lineno, column, msg, [])
		else:
			return Token(TK_TAG_BEGIN, lineno, column, tag, [])

	def make_tag_end_token(self):
		return Token(TK_TAG_END, self.lineno, self.column, "}", [])

	def make_word_token(self, word, lineno, column):
		wordstr = ''.join(word)
		return Token(TK_WORD, lineno, column, wordstr, [])

	def make_bad_escape_error_token(self, ch):
		msg = "Illegal escaping of '\\%s'. Only these characters may be escaped: '\\' '{' '}' '<'" % (ch)
		return Token(TK_ERROR, self.lineno, self.column, msg, [])

	def make_bad_char_error_token(self, ch):
		msg = "Illegal un-printable character '0x%02x'" % ( ord(ch) )
		return Token(TK_ERROR, self.lineno, self.column, msg, [])

	def make_malformed_heredoc_operator_error_token(self, ch):
		msg = "Malformed Here Document operator '<%s', expecting '<<'." % (ch)
		return Token(TK_ERROR, self.lineno, self.column, msg, [])

	def make_missing_escape_lt_error_token(self):
		msg = "Missing escape '\\' before '<' or malformed Here Document operator."
		return Token(TK_ERROR, self.lineno, self.column, msg, [])

	#
	# Return the next character from the input.
	# remembers the state so we can rewind 1 character
	#
	def getchar(self):
		if self.got_undo:
			self.got_undo = False
			self.lineno = self.prev_lineno
			self.column = self.prev_column
			ch = self.prev_ch
		else:
			if self.prev_ch == '\n':
				self.lineno += 1
				self.column = 0
			elif self.prev_ch != '':
				self.column += 1

			ch = self.f.read(1)

			self.prev_lineno = self.lineno
			self.prev_column = self.column
			self.prev_ch = ch
	
		return ch

	#
	# Go back 1 character in the input stream, as if the last
	# call to getchar() never happened.
	#
	def undo_getchar(self):
		self.got_undo = True

	#
	# Read until newline. Return the line including the newline character.
	# On EOF, the empty string shall be returned.
	#
	def getline(self):
		line = []
		done = False
		while not done:
			ch = self.getchar()

			if ch == '':
				done = True

			elif ch == '\n':
				line.append(ch)
				done = True

			else:
				line.append(ch)

		return ''.join(line)

	#
	# Here Documents are cleaned up a little:
	#
	# 1) Right trim white-space from all lines.
	# 2) Left trim largest common leading white-space pattern.
	#		(ignoring blank lines)
	# 3) Remove leading and trailing blank lines
	#
	def heredoc_post_processing(self, lines):
		result = []

		leading_blank_lines = 0
		trailing_blank_lines = 0
		got_first = False

		#
		# Right trim each line and find smallest leading whitespace pattern
		#
		min_leading = None
		for oldline in lines:
			line = oldline.rstrip()

			if len(line) > 0:
				trailing_blank_lines = 0
				got_first = True
				m = LeadingWhiteSpaceRegularExpression.match(line)
				if m != None:
					leading = m.group(1)
					if min_leading == None or len(leading) < len(min_leading):
						min_leading = leading
			else:
				trailing_blank_lines += 1
				if not got_first:
					leading_blank_lines += 1

			result.append(line)

		# remove trailing blank lines
		if trailing_blank_lines > 0:
			del result[ -trailing_blank_lines : ]

		# remove leading blank lines
		del result[ : leading_blank_lines ]

		#
		# Count number of non-blank lines that possess 'min_leading' (in 'count')
		# and count number of non-blank lines (in 'total')
		#
		count = 0
		total = 0
		for i in range(len(result)):
			line = result[i]
			if len(line) > 0:
				total += 1
				m = LeadingWhiteSpaceRegularExpression.match(line)
				if m != None:
					leading = m.group(1)
					if leading[:len(min_leading)] == min_leading:
						count += 1

		#
		# Chop the common leading whitespace from each
		# non blank line
		#
		if count == total:
			for i in range(len(result)):
				line = result[i]
				if len(line) > 0 and min_leading != None:
					line = line[len(min_leading):]
					result[i] = line

		return result

	#
	# Helper function to tokenize a Here Document
	#
	# The syntax is,
	#
	#		TagName<< _THING_
	#		abd def
	#		jjj kkkk lll
	#		x = 1 + 2 + 3 * T / sine(x)
	#		XXYYZZ
	#		_THING_
	#
	# On entry to this function:
	#	* The TagName has been consumed and is in 'word'
	#		(as an array of characters)
	#	* The << operator has been consumed.
	#
	# The tag name is not empty. But it needs to be
	# validated as a proper identifier name.
	#
	# _THING_ is referred to as the Termination Label. 
	# The termination label must also be a valid identifier.
	#
	# The body of a Here Document
	#
	#
	def tokenize_heredoc(self, word, lineno, column):
		tag = ''.join(word)
		m = IdentRegularExpression.match(tag)

		if m == None:
			if len(tag) == 0:
				msg = "Missing tag name before Here Document operator '<<'."
			else:
				msg = "Illegal tag name '%s' ('<' '\\' '{' '}' are not allowed)." % (tag)
			return Token(TK_ERROR, lineno, column, msg, [])

		#
		# Get the termination label
		#
		rest = self.getline()
		if rest == '':
			msg = "Unexpected EOF after Here Document operator '<<' (expecting termination label)."
			return Token(TK_ERROR, lineno, column, msg, [])

		elif rest.strip() == '':
			msg = "No Here Document termination label given after '<<' operator."
			return Token(TK_ERROR, lineno, column, msg, [])

		else:
			m = HereDocTerminatorRegularExpression.match(rest)
			if m == None:
				msg = "Invalid Here Document termination label '%s'." % (rest.strip())
				return Token(TK_ERROR, lineno, column, msg, [])

			termlabel = m.group(1)

		#
		# Collect lines of text until the termination label is detected
		#
		lines = []
		done = False
		while not done:
			line = self.getline()
			if line == '':
				msg = "EOF reached inside of Here Document, expecting termination tag '%s'." % (termlabel)
				return Token(TK_ERROR, lineno, column, msg, [])

			else:
				m = HereDocTerminatorRegularExpression.match(line)
				if m != None:
					t = m.group(1)
					if t == termlabel:
						done = True
					else:
						lines.append(line)
				else:
					lines.append(line)

		lines = self.heredoc_post_processing(lines)

		return Token(TK_HEREDOC, lineno, column, tag, lines)

	#
	# Return the next token from the input
	#
	def get_token(self):
		result = None
		done = False
		while not done:
			ch = self.getchar()

			if ch == '':
				result = self.make_eof_token()
				done = True

			elif self.is_white(ch):
				pass

			elif ch == '}':
				result = self.make_tag_end_token()
				done = True

			elif self.is_bad_char(ch):
				result = self.make_bad_char_error_token(ch)
				done = True

			else:
				lineno = self.lineno
				column = self.column
				word = []
				while not done:
					if ch == '\\':
						ch = self.getchar()
						if self.is_escapable(ch):
							word.append(ch)
						else:
							result = self.make_bad_escape_error_token(ch)
							done = True

					elif ch == '{':
						result = self.make_tag_begin_token(word, lineno, column)
						done = True

					elif ch == '}':
						self.undo_getchar()
						result = self.make_word_token(word, lineno, column)
						done = True

					elif self.is_white(ch):
						self.undo_getchar()
						result = self.make_word_token(word, lineno, column)
						done = True

					elif ch == '<':
						ch = self.getchar()
						if ch != '<':
							if len(word) > 0:
								result = self.make_malformed_heredoc_operator_error_token(ch)
								done = True

							else:
								result = self.make_missing_escape_lt_error_token()
								done = True

						else:
							result = self.tokenize_heredoc(word, lineno, column)
							done = True

					elif ch == '':
						self.undo_getchar()
						result = self.make_word_token(word, lineno, column)
						done = True

					elif self.is_bad_char(ch):
						self.undo_getchar()
						result = self.make_word_token(word, lineno, column)
						done = True

					else:
						word.append(ch)

					if not done:
						ch = self.getchar()

		return result

######################################################################
#
# Node Types
#
ROOT       = 1
ERROR      = 2
TAG        = 3
TRANSLATED = 4
WORD       = 5
HEREDOC    = 6

######################################################################
# The Tagged Text Tree consists of nested arrays of this structure:
#
#	node[0]		Node Type. integer.
#	node[1]		Filename
#	node[2]		Line number. integer. Zero based.
#	node[3]		Column. integer. Zero based.
#	node[4]		Special String. string. can be error message, tag name, word. Use None if undefined
#	node[5]		Specal array of string. array of strings. Use empty array if not defined
#	node[6]		Children array of nodes. The children of this node. Use empty array if no children
#
# Root Node:
#	[ROOT, "filename", 0, 0, None, [ "log1", "log2", ... ], [ <child0>, <child1>, ... ] ]
#
# Error Node:
#	[ERROR, "filename", <line>, <col>, "error-message", [], [ <child0>, <child1>, <child2>, ... ] ]
#
# Tag Node:
#	[TAG, "filename", <line>, <col>, "tag", [], [ <child0>, <child1>, <child2>, ... ] ]
#
# Translated Node
#	[TRANSLATED, "filename", <line>, <col>, None, [<begin>, <end>], [ <child0>, <child1>, <child2>, ... ] ]
#
# Word Node:
#	[WORD, "filename", <line>, <col>, "word", [], [] ]
#
# Heredoc Node:
#	[HEREDOC, "filename", <line>, <col>, "tag", [<line0>, <line1>, ...], [] ]
#
# Description:
#
#	Root Node		This forms the top-level node for a document. There
#					is only ever one of these.
#					It lacks file location information. It does have an array
#					of log strings in node[5]. This can be used to record
#					the series of processing steps applied to the tree or
#					other data like version numbers, timestamps etc...
#
#	Error Node		This node is inserted into the tree when an error is detected.
#					It includes file location information and an error message.
#					It can have children if the error detected applies to
#					an internal node and you want to retain the rest of the
#					document tree. This is how error handling is performed
#					when you process the tree through many steps. Instead of
#					quitting and reporting a single error, you just keep
#					adding error nodes to the tree. A final step will print
#					all known errors.
#
#	Tag Node		This node represents a tag. Tagged{Text} remember! This
#					is the whole point of this file format really.
#
#	Translated Node	Represents part of the tree that has been translated into
#					its final output form. As each processing step translates
#					a little more of the tree, the tree has more and more of these
#					nodes. To generate the final output, one calls 'write_translated'
#					Which does an in order traversal of the tree and writes
#					all before and after text bits to the output stream.
#
#	Word Node		A naked word in the input is added as a 'word' node. It
#					will not contain any whitespace.
#
#	Heredoc Node	A Here Document will be represented by this node type.
#

######################################################################
#
# Class Node
#
# Node contains a reference to the root of the Tagged Text Tree
# plus a pointer to one of the internal nodes. This class
# provides a way to iterate over the children of this node.
#
class Node:
	def __init__(self, root, node):
		self.root = root
		self.node = node

	def __str__(self):
		return "TaggedText.Node:{\n" + str(self.root) + "\n}"

	#
	# Method for iterating of the children
	#
	def children(self):
		for child in self.node[6]:
			yield Node(self.root, child)

	def num_children(self):
		return len(self.node[6])

	#
	# Return the nth child
	#
	def get_child(self, nth):
		if nth >= 0 and nth < self.num_children():
			return Node(self.root, self.node[6][nth])
		else:
			raise ERR010()

	def get_root(self):
		return Node(self.root, self.root)

	def log_lines(self):
		if is_root(self):
			return self.root[5]
		else:
			raise ERR008()

	#
	# Return a nicely formatted location string useful for
	# generating error messages. (For those cases
	# in which an explicit error node is not injected into the tree)
	#
	def location_string(self):
		result = self.filename() + ":"

		if self.lineno() != None:
			result += " Line %d, " % (self.lineno()+1)

		if self.column() != None:
			result += "Column %d:" % (self.column()+1)

		return result

	def heredoc_content(self):
		if self.is_heredoc():
			return self.node[5]
		else:
			raise ERR009()

	def add_log(self, log_line):
		self.root[5].append(log_line)

	def is_root(self):
		return self.node[0] == ROOT

	def is_error(self):
		return self.node[0] == ERROR

	def is_tag(self):
		return self.node[0] == TAG

	def is_tag_named(self, tag_name):
		return self.is_tag() and self.tag() == tag_name

	def is_translated(self):
		return self.node[0] == TRANSLATED

	def is_word(self):
		return self.node[0] == WORD

	def is_heredoc(self):
		return self.node[0] == HEREDOC

	def is_heredoc_named(self, tag_name):
		return self.is_heredoc() and self.tag() == tag_name

	def filename(self):
		return self.node[1]

	def lineno(self):
		return self.node[2]

	def column(self):
		return self.node[3]

	def node_type_string(self):
		if self.node[0] == ROOT:
			return "root"
		elif self.node[0] == ERROR:
			return "error"
		elif self.node[0] == TAG:
			return "tag"
		elif self.node[0] == HEREDOC:
			return "heredoc"
		elif self.node[0] == TRANSLATED:
			return "translated"
		elif self.node[0] == WORD:
			return "word"
		else:
			raise ERR012()

	#
	# Returns true if this node type supports having children
	# (Word nodes, for example cannot have children)
	#
	def can_have_children(self):
		return ( self.is_root()
					or self.is_error()
					or self.is_tag()
					or self.is_translated() )

	def begin_text(self):
		if self.is_translated():
			return self.node[5][0]
		else:
			raise ERR001()

	def end_text(self):
		if self.is_translated():
			return self.node[5][1]
		else:
			raise ERR002()

	def tag(self):
		if self.is_tag() or self.is_heredoc():
			return self.node[4]
		else:
			raise ERR006()

	def word(self):
		if self.is_word():
			return self.node[4]
		else:
			raise ERR007()

	#
	# Format the error node into a nice error message
	#
	def error_string(self):
		if self.is_error():
			return "%s: Line %d, Column %d: %s" % (
						self.node[1],
						self.node[2] + 1,
						self.node[3] + 1,
						self.node[4] )
		else:
			raise ERR011()

	#
	# Traverse 'root' and for each Error Node encountered
	# format a nice error message and write to 'f'.
	# Returns the number of error nodes encountered.
	#
	def report_errors(self, f):
		count = 0

		if self.is_error():
			es = self.error_string()
			f.write(es + "\n")
			count += 1

		for child in self.children():
			count += child.report_errors(f)

		return count

	#
	# Write the tree to file 'f' as Tagged{Text}
	#
	def write(self, f):
		writer_info = { 'file': f, 'column': 0, 'max_width': 100 }
		self.__write(writer_info)
		f.write('\n')

	def __write(self, writer_info):

		if self.is_tag():
			begin_txt = self.tag() + "{"
			end_txt = "} "

		elif self.is_word():
			need_escape = False
			for c in self.word():
				if c in '\\{}<':
					need_escape = True

			if need_escape:
				word = ''
				for c in self.word():
					if c in '\\{}<':
						word += '\\'

					word += c
			else:
				word = self.word()

			begin_txt = word
			end_txt = " "

		elif self.is_heredoc():
			suffix_number = 0
			term_label = "_EOF0_"
			for line in self.heredoc_content():
				m = HeredocTermLabelRegularExpression.match(line)
				if m != None:
					while True:
						if term_label in line:
							suffix_number += 1
							term_label = "_EOF" + str(suffix_number) + "_"
						else:
							break

			begin_txt = self.tag() + "<<" + term_label + "\n"

			for line in self.heredoc_content():
				begin_txt += (line + '\n')

			end_txt = term_label + "\n"

		elif self.is_error():
			begin_txt = "\n\nERROR: " + self.error_string()
			end_txt = "\n\n"

		elif self.is_root():
			begin_txt = ""
			end_txt = ""

		elif self.is_translated():
			begin_txt = self.begin_text()
			end_txt = self.end_text()

		f = writer_info['file']

		max_width = writer_info['max_width']
		column = writer_info['column']

		for ch in begin_txt:
			if ch == '\n':
				column = 0
			else:
				column += 1

		if column > max_width:
			begin_txt = begin_txt + '\n'
			column = 0

		writer_info['column'] = column

		f.write(begin_txt)
		
		for child in self.children():
			child.__write(writer_info)

		column = writer_info['column']

		for ch in end_txt:
			if ch == '\n':
				column = 0
			else:
				column += 1

		writer_info['column'] = column

		f.write(end_txt)

	#
	# Write the tree to file 'f'
	# The format is JSON
	#
	def write_tree(self, f):
		json.dump(self.node, f, indent=4, separators=(',', ': '))
		f.write("\n")

	#
	# Write the tree to file 'f'
	# The format is JSON
	# this formats the tree in a more concise and easy to read format
	#
	def write_tree_pretty(self, indent_str, f):
		self.__write_tree_pretty(0, 0, "", indent_str, f)
		f.write('\n')

	def __write_tree_pretty(self, child_idx, out_of_children, curindent_str, indent_str, f):
		f.write('%s[' % (curindent_str) )

		json.dump(self.node[0], f)
		f.write(', ')

		json.dump(self.node[1], f)
		f.write(', ')

		json.dump(self.node[2], f)
		f.write(', ')

		json.dump(self.node[3], f)
		f.write(', ')

		json.dump(self.node[4], f)
		f.write(', ')

		json.dump(self.node[5], f)
		f.write(', ')

		ooc = self.num_children()

		if ooc == 0:
			f.write('[] ]')
		else:
			f.write('[\n')
			newindent_str = curindent_str + indent_str
			ci = 0
			for child in self.children():
				child.__write_tree_pretty(ci, ooc, newindent_str, indent_str, f)
				ci += 1

			f.write(curindent_str + '] ]')

		if child_idx < out_of_children-1:
			f.write(',')
		f.write('\n')

	#
	# return a copy of the whole tree
	# the cloned node will continue to point
	# to the same node.
	#
	def clone(self):
		c = copy.deepcopy(self.node)
		return Node(self.root, c)

	#
	# Return True if the 'other' is the same as self.
	# "Locgically Equal" means the node structure and tag names
	# are the same, not necessarily the meta data like filenames
	# and line numbers
	#
	def logically_equal(self, other):
		same = self.__logically_equal_node(other)
		if not same:
			return False

		nc = self.num_children()

		if nc != other.num_children():
			return False

		for cidx in range(0, nc):
			sc = self.get_child(cidx)
			oc = other.get_child(cidx)

			same = sc.logically_equal(oc)
			if not same:
				return False

		return True

	#
	# Returns true if the two nodes are equal.
	# This is a shallow equals. This routine
	# only compares the node properties, excluding
	# the children
	#
	def __logically_equal_node(self, other):
		if self.is_root() and other.is_root():
			return True

		elif self.is_error() and other.is_error():
			return self.node[4] == other.node[4]

		elif self.is_tag() and other.is_tag():
			return self.tag() == other.tag()

		elif self.is_translated() and other.is_translated():
			return ( self.begin_text() == other.begin_text()
						and self.end_text() == other.end_text() )

		elif self.is_word() and other.is_word():
			return self.word() == other.word()

		elif self.is_heredoc() and other.is_heredoc():
			return ( self.tag() == other.tag()
						and self.heredoc_content() == other.heredoc_content() )

		else:
			return False

	#
	# Writes the document tree to file 'f'
	# as translated text, by emitting only the
	# Translated Nodes
	#
	def write_translated(self, f):
		if self.is_translated():
			f.write(self.begin_text())

		for child in self.children():
			child.write_translated(f)

		if self.is_translated():
			f.write(self.end_text())

	#
	# Set this nodes children to 'children'
	# 'children' is a list of Node's
	#
	def set_children(self, children):
		new_children = []
		for child in children:
			new_children.append(child.node)

		self.node[6] = new_children

	#
	# push_children: A tree operation
	# in which all the children of the current node
	# become the children of 'n' and and 'n'
	# becomes the sole child of 'self'
	#
	# Any children of 'n' are lost.
	#
	def push_children(self, n):
		if self.can_have_children():
			n.root = self.root
			n.node[6] = self.node[6]
			self.node[6] = [n.node]
		else:
			raise ERR003()

	#
	# Add a a new child to the front
	#
	def add_child_front(self, n):
		if self.can_have_children():
			self.node[6].insert(0, n.node)
			n.root = self.root
		else:
			raise ERR004()

	#
	# Add a a new child to the back
	#
	def add_child_back(self, n):
		if self.can_have_children():
			self.node[6].append(n.node)
			n.root = self.root
		else:
			raise ERR005()

	#
	# Make the current node look like other node 'n'.
	#
	def morph(self, n):
		self.node[0] = n.node[0]
		self.node[1] = n.node[1]
		self.node[2] = n.node[2]
		self.node[3] = n.node[3]
		self.node[4] = n.node[4]
		self.node[5] = n.node[5]
		self.node[6] = n.node[6]

	#
	# replace the current node's children with those from node 'n'.
	#
	def take_children(self, n):
		self.node[6] = n.node[6]

	#
	# 'f' is a function that accepts a node pointer.
	# For each child, if the function 'f' returns
	# True, then delete it from this node.
	#
	def delete_children_if(self, f):
		i = 0
		children = self.node[6]
		while i < len(children):
			n = Node(self.root, children[i])
			if f(n):
				del children[i]
				continue
			i += 1

	#
	# For each tag discovered replace it
	# with a Translated Node which has begin_txt and end_txt
	#
	def translate_tag(self, tag, begin_txt, end_txt):
		if self.is_tag() and self.tag() == tag:
			n = make_translated_node(
				self.filename(),
				self.lineno(),
				self.column(),
				begin_txt,
				end_txt)

			n.take_children(self)
			self.morph(n)

		for child in self.children():
			child.translate_tag(tag, begin_txt, end_txt)

	#
	# Evaluate the tree starting with 'root'
	# eval_functions is an associative array that
	# maps tag names to tag functors:
	#
	#	eval_functions = {
	#				'TagName1':	some_function,
	#				'P':		do_p_tag,
	#				'it':		doit,
	#				'LINK':		( lambda root: do_link(root, link_database) )
	#	}
	#
	# The functor is called thusly,
	#
	#	def some_function(n):
	#		return [ n1, n2, n3 ]
	#
	# 'n' is a tag node whose name matches 'TagName1'
	# The function should return a list of nodes, which
	# replace the node 'n' in the tree.
	#
	# Return the empty list to delete the node.
	#
	# Use lambda to bind additional arguments to your functor:
	#
	#	(lambda root: some_function(root, arg1, arg2))
	#
	def eval(self, eval_functions):
		new_children = []
		for child in self.children():
			new_children.extend( child.eval(eval_functions) )

		self.set_children(new_children)

		if self.is_tag() and self.tag() in eval_functions:
			f = eval_functions[ self.tag() ]
			return f(self)
		else:
			return [self]

	#
	# For each Here Document with tag name 'tag' replace it
	# with a Translated Node which has begin_txt and end_txt
	#
	# The function 'f' is called with the here document text.
	# The function 'f' should return the here document with any
	# transformations applied (like escaping HTML)
	#
	def translate_heredoc(self, tag, begin_txt, end_txt, f):
		if self.is_heredoc() and self.tag() == tag:
			n = make_translated_node(
					self.filename(),
					self.lineno(),
					self.column(),
					begin_txt,
					end_txt )
			lines = self.heredoc_content()
			self.morph(n)

			for line in lines:
				n = make_translated_node(
						self.filename(),
						self.lineno(),
						self.column(),
						f(line),
						"\n" )
				self.add_child_back(n)

		for child in self.children():
			child.translate_heredoc(tag, begin_txt, end_txt, f)

######################################################################
#
# Parse a tagged text file.
# On success the node returned will
# have its is_root() property TRUE. Else
# the is_error() property will be TRUE.
#
def parse(f, filename):
	def make_root_node():
		return [ROOT, filename, 0, 0, None, [], [] ]

	def make_word_node(t):
		return [WORD, filename, t.lineno, t.column, t.str, [], [] ]

	def make_heredoc_node(t):
		return [HEREDOC, filename, t.lineno, t.column, t.str, t.strlist, [] ]

	def make_tag_node(t):
		return [TAG, filename, t.lineno, t.column, t.str, [], [] ]

	def make_error_node(lineno, column, msg):
		return [ERROR, filename, lineno, column, msg, [], [] ]

	tokenizer = Tokenizer(f)

	parents = []
	root = make_root_node()
	curr = root

	done = False
	while not done:
		t = tokenizer.get_token()

		if t.ttype == TK_EOF:
			done = True

		elif t.ttype == TK_ERROR:
			n = make_error_node(t.lineno, t.column, t.str)
			root = n
			done = True
			parents = []

		elif t.ttype == TK_WORD:
			n = make_word_node(t)
			curr[6].append(n)

		elif t.ttype == TK_HEREDOC:
			n = make_heredoc_node(t)
			curr[6].append(n)

		elif t.ttype == TK_TAG_BEGIN:
			n = make_tag_node(t)
			curr[6].append(n)
			parents.append(curr)
			curr = n

		elif t.ttype == TK_TAG_END:
			if len(parents) > 0:
				curr = parents.pop()
			else:
				n = make_error_node(t.lineno, t.column, "Mis-matched closing brace '}'.")
				root = n
				done = True

	if len(parents) > 0:
		# 'curr' refers to un closed node
		n =  make_error_node(curr[2], curr[3], "Un-closed tag.")
		root = n

	return Node(root, root)

######################################################################
#
# Read a tree from input file 'f'
#
# If not success then 'result' is an error message.
#
def read_tree(f):
	root = json.load(f)
	return Node(root, root)

#
# Construct a root Node
#
# Can be used to construct a temporary node. Useful for
# creating a lists of children nodes.
#
def make_root_node():
	ns = [ROOT, "", 0, 0, None, [], [] ]
	return Node(ns, ns)

#
# Construct a root Node (allow filename to be set)
#
# Can be used to construct a temporary node. Useful for
# creating a lists of children nodes.
#
def make_root_node_with_filename(filename):
	ns = [ROOT, filename, 0, 0, None, [], [] ]
	return Node(ns, ns)

#
# Construct a Translated Node
#
def make_translated_node(filename, lineno, column, begin_text, end_text):
	ns = [TRANSLATED, filename, lineno, column, None, [begin_text, end_text], [] ]
	return Node(ns, ns)

#
# Construct a tag node with no children
#
def make_tag_node(filename, lineno, column, tag):
	ns = [TAG, filename, lineno, column, tag, [], [] ]
	return Node(ns, ns)

#
# Construct a heredoc node with 'tag' and 'lines'
#
def make_heredoc_node(filename, lineno, column, tag,  lines):
	ns = [HEREDOC, filename, lineno, column, tag, lines, [] ]
	return Node(ns, ns)

#
# Construct a error node.
#
def make_error_node(filename, lineno, column, msg):
	ns = [ERROR, filename, lineno, column, msg, [], [] ]
	return Node(ns, ns)

#
# Construct a word node
#
def make_word_node(filename, lineno, column, word):
	ns = [WORD, filename, lineno, column, word, [], [] ]
	return Node(ns, ns)

#
# This runs the function 'f' on a tagged text
# tree which was read from stdin and writes it
# back to stdout.
#
# f -	a function that takes a TaggedText{} Tree as
# 		its first and only arguments
#
def command(f):
	if len(sys.argv) != 1:
		sys.stderr.write("""
Usage: %s
	This script reads from stdin and writes the result to stdout.
	The input must be a tagged text JSON tree.
	The output will also be a tagged text JSON tree.

	Error: This command does not accept any command line arguments.

""" % (sys.argv[0]) )
		exit(1)

	root = read_tree(sys.stdin)
	f(root)
	root.write_tree(sys.stdout)
	exit(0)
