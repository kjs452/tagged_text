#
# This file provides these Tagged Text Tree  operations:
#
# include{filename}
# //{this is a comment}
#
# HEREDOC{ Tag{filename} }
#	This embeds a here is document tag using filename for the content
#
# Usage:
#		tt_include.run(root, dirs)
#
#	f = tt_include.bind(dirs)
#
#	taggedtext.commnd(f)
#
#
import os
import copy
import taggedtext

#
# This was provided during the development
# of the comment tag, to ensure all comments were
# removed. This will highlight any remaining comments. Shouldn't
# ever be the case that comments remain.
#
def comments_reveal(root):
	root.translate_tag("//", " <font size=+4><tt>COMMENT: ", "</tt></font> ")

#
# Remove comment nodes '//{ this is a comment }'
# Assumes that will never be called with a root node
# that is a comment. There can be no NULL tree.
#
def comments(root):

	def is_comment(n):
		return n.is_tag_named("//")

	root.delete_children_if(is_comment)

	for child in root.children():
		comments(child)

#
# Open include files 'include{filename.tt}'
# Replace 'include{}' node in the document tree
# with the results of including the file.
#
# Before:
#	parent
#		a
#		b
#		include{foo.tt}
#		include{bar.tt}
#		c
#		d
#
# After:
#	parent
#		a
#		b
#		foo_a
#		foo_b
#		foo_c
#		bar_a
#		bar_b
#		c
#		d
#
# 'dirs' is an array of search path to hunt
# for the include file. The first
# one found will be used.
#
# If an error occurs the include{} tag is
# replaced with an Error node indicating the
# reason and location.
#
# Yes, this operation is recursive in the sense
# that includes that include other files
# will be processed. Including
# the same file multiple files
# is not permitted.
#
# This iterated over 'root' in a breadth-first
# manner. First expanding immediate children
#
#
def includes(root, dirs):

	def find_file(dirs, filename):
		found = False
		for d in dirs:
			full_path = d + "/" + filename

			if os.path.isfile(full_path):
				found = True
				break

		return full_path if found else None

	#
	# 'root' is an include tag node. Process it
	# for correctness. If an error is encountered
	# append to 'children' an error node.
	#
	# Else append as many 'children' as the
	# include document contains to 'children'
	#
	# If the included file has already been 'seen'
	# do nothing.
	#
	# The main output of this function is having
	# new nodes appended to 'tmp'.
	#
	# 'dirs' is an array of search paths. The include file
	# is searched in order and the first one is used.
	#
	# returns a list of children to added to the parent node
	#
	def process_include(root, dirs, seen):
		nc = root.num_children()
		if nc != 1:
			n = taggedtext.make_error_node(
						root.filename(),
						root.lineno(),
						root.column(),
						"include{} tag contains %s elements (just one please)"
									% ( "more than one" if nc > 1 else "no" ) )
			return [n]

		c = root.get_child(0)
		if not c.is_word():
			n = taggedtext.make_error_node(
					root.filename(),
					root.lineno(),
					root.column(),
					"include{} tag doesn't contain a word" )
			return [n]

		filename = c.word()

		full_path = find_file(dirs, filename)

		if full_path == None:
			n = taggedtext.make_error_node(
						root.filename(),
						root.lineno(),
						root.column(),
						"include{} could not locate file '%s' in any search directory" % (filename) )
			return [n]

		#
		# the cycle detect scheme must use absolute paths
		# for most reliable results.
		#
		abs_path = os.path.abspath(full_path)

		if abs_path in seen:
			loc = seen[abs_path]
			
			n = taggedtext.make_error_node(
					root.filename(),
					root.lineno(),
					root.column(),
					"include{%s} cycle detected (previous include at '%s' Line: %d, Column %d)."
										% (filename, loc[0], loc[1], loc[2]) )
			return [n]

		f = open(full_path, 'r')

		n = taggedtext.parse(f, full_path)
		f.close()
		if n.is_error():
			return [n]

		#
		# This is kind of important, comments need to be respected
		# For example, someone could "comment out" an include{}
		# tag for testing purposes and it would never get processed.
		#
		comments(n)

		new_seen = copy.copy(seen)
		new_seen[abs_path] = ( root.filename(), root.lineno(), root.column() )

		helper(n, dirs, new_seen)

		result = []
		for child in n.children():
			result.append(child)

		return result

	#
	# process this tag:
	#	HEREDOC{ Tag{filename} }
	#
	def process_heredoc(root, dirs):
		nc = root.num_children()
		if nc != 1:
			n = taggedtext.make_error_node(
						root.filename(),
						root.lineno(),
						root.column(),
						"HEREDOC{} tag contains %s elements (just one please)"
									% ( "more than one" if nc > 1 else "no" ) )
			return [n]

		c = root.get_child(0)
		if not c.is_tag():
			n = taggedtext.make_error_node(
					root.filename(),
					root.lineno(),
					root.column(),
					"HEREDOC{} tag doesn't contain a tag" )
			return [n]

		nc = c.num_children()
		if nc != 1:
			n = taggedtext.make_error_node(
						root.filename(),
						root.lineno(),
						root.column(),
						"%s{} tag contains %s elements (just one please)"
									% (c.tag(), "more than one" if nc > 1 else "no" ) )
			return [n]

		filename = c.get_child(0).word()
		full_path = find_file(dirs, filename)

		if full_path == None:
			n = taggedtext.make_error_node(
						root.filename(),
						root.lineno(),
						root.column(),
						"HEREDOC{} could not locate file '%s' in any search directory" % (filename) )
			return [n]

		f = open(full_path, 'r')
		lines = f.read().split("\n")
		f.close()

		n = taggedtext.make_heredoc_node(
					root.filename(),
					root.lineno(),
					root.column(),
					c.tag(),
					lines )

		return [n]

	#
	# 'seen' is a associative array index by full filename
	#
	def helper(root, dirs, seen):
		new_children = []
		for child in root.children():
			if child.is_tag_named("include"):
				x = process_include(child, dirs, seen)
				new_children.extend(x)
			elif child.is_tag_named("HEREDOC"):
				x = process_heredoc(child, dirs)
				new_children.extend(x)
			else:
				new_children.append(child)

		root.set_children(new_children)

		for child in root.children():
			helper(child, dirs, seen)

	#
	# Call the helper function to do the work.
	# Make sure we add ourselves to the "seen" list to
	# detect self inclusion
	#
	ap = os.path.abspath(root.filename())

	helper(root, dirs, {ap: (root.filename(), 0, 0) } )

#
# dirs an array of file search paths
#
def run(root, dirs):
	comments(root)
	includes(root, dirs)
	comments_reveal(root)

#
# taggedtext.command(f) expects the function 'f' to take
# a single argument. This allows the additional argument
# of 'dirs' to tbe provided
#
# run_func = tt_include.bind(dirs)
#
# taggedtext.command(run_func)
#
#
def bind(dirs):
	return (lambda root: run(root, dirs))
