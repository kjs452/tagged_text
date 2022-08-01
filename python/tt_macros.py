#!/usr/bin/python
#
# How to define a symbol:
#
#	DEFINE{ Bob{Bobby F. Longton}  }
#	DEFINE{ Sue{Susan St. Snortly}  }
#	DEFINE{ ThemFolks{Bob{} and Sue{}}  }
#
# How to reference a definition:
#
#		Bob{} was here.
#
#  * A symbol may only be defined once.
#  * Symbols can be defined in terms of other symbols
#  * Circular definition of symbols is not allowed
#
# Bob{}			//{ show where this is defined }
#
# LIST_DEFINES{}	//{ expands to a error node, listing all macros and where they are defined  }
#
#
import taggedtext

#
# The strings in this table cannot be defined
#
RESERVED_NAMES = [
	"DEFINE",
	"LIST_DEFINES"
]

#
# * Check syntax of DEFINE tag
# * Check for duplicate DEFINE
# * Check for nested DEFINE's (not allowed)
# * Add symbol to symbol_table
#
def process_define_pass1(def_node, symbol_table):
	nc = def_node.num_children()

	if nc != 1:
		n = taggedtext.make_error_node(
				def_node.filename(),
				def_node.lineno(),
				def_node.column(),
				"DEFINE{} tag contains %s elements. Expecting only one element"
							% ( "more than one" if nc > 1 else "no") )

		def_node.morph(n)
		return False

	c = def_node.get_child(0)
	if not c.is_tag():
		n = taggedtext.make_error_node(
				c.filename(),
				c.lineno(),
				c.column(),
				"DEFINE{} tag must contain a single tag. (instead found %s)"
							% (c.node_type_string()) )

		c.morph(n)
		return False

	if c.tag() in RESERVED_NAMES:
		n = taggedtext.make_error_node(
				c.filename(),
				c.lineno(),
				c.column(),
				"'%s' cannot be re-defined in a DEFINE"
							% (c.tag()) )

		c.morph(n)
		return False

	if c.tag() in symbol_table:
		sym = symbol_table[c.tag()]
		defn = sym['definition']
		n = taggedtext.make_error_node(
				c.filename(),
				c.lineno(),
				c.column(),
				"'%s' was already defined at %s"
							% (c.tag(), defn.location_string()) )

		c.morph(n)
		return False

	symbol_table[ c.tag() ] = { 'status': 'U', 'definition': c }
	return True

#
# * Check if child is a tag in symbol table
# * Check it has no children
# * add definition to tmp's children
# * If not a defined macro, leave alone
#
def process_define_pass2(node, symbol_table):

	sym = symbol_table[ node.tag() ]
	defnode = sym['definition']

	if node.num_children() != 0:
		n = taggedtext.make_error_node(
				node.filename(),
				node.lineno(),
				node.column(),
				"Incorrect usage of DEFINE '%s'. must be referenced with 0 children (defined here: %s)"
							% (node.tag(), defnode.location_string()) )
		node.morph(n)
		return [node]

	return list(defnode.children())

#
# PASS 1: Remove all DEFINE's and check for duplicates, populate symbol table
#
def define_helper_pass1(root, symbol_table):

	new_children = []

	for child in root.children():
		if child.is_tag_named("DEFINE"):
			success = process_define_pass1(child, symbol_table)
			if not success:
				new_children.append(child)
		else:
			define_helper_pass1(child, symbol_table)
			new_children.append(child)

	root.set_children(new_children)

#
# PASS 2: Find macros and replace them with their defintion
#
def define_helper_pass2(root, symbol_table):

	new_children = []

	for child in root.children():
		if child.is_tag() and child.tag() in symbol_table:
			nc = process_define_pass2(child, symbol_table)
			new_children.extend(nc);
		else:
			define_helper_pass2(child, symbol_table)
			new_children.append(child)

	root.set_children(new_children)

######################################################################
######################################################################
######################################################################
#
# Iterate over root, expanding any DEFINE macros that are found
#
def expand_definition_root(root, symbol_table):

	new_children = []

	for child in root.children():
		if child.is_tag() and child.tag() in symbol_table:
			sym = symbol_table[ child.tag() ]

			if sym['status'] == 'U':
				success = expand_definition(child.tag(), symbol_table)
				if not success:
					return False

			if sym['status'] == 'D':
				for c in sym['definition'].children():
					new_children.append(c)
			else:
				return False

		elif child.can_have_children():
			success = expand_definition_root(child, symbol_table)
			if not success:
				return False
			new_children.append(child)

		else:
			new_children.append(child)

	root.set_children(new_children)
	return True

def expand_definition(symbol_name, symbol_table):
	sym = symbol_table[symbol_name]

	if sym['status'] == 'D':
		# already defined
		return True

	if sym['status'] == 'P':
		# error, set sym['definition'] to be an error node
		defnode = sym['definition']
		n = taggedtext.make_error_node(
				defnode.filename(),
				defnode.lineno(),
				defnode.column(),
				"DEFINE '%s' has a circular definition" % (defnode.tag()) )
		defnode.morph(n)
		return False

	elif sym['status'] == 'U':
		sym['status'] = 'P'
		success = expand_definition_root(sym['definition'], symbol_table)
		if success:
			sym['status'] = 'D'
			return True
		else:
			return False

	else:
		# assertion, unknown status
		return False

#
# symbol_table is associative array:
#
#	{ 'symbol': {
#			'definition':	<TaggedText Node>,
#			'status':		'D|U|P',			# D=defined, U=undefined, P=in progress
#			}
#
#
def expand_definitions(symbol_table):
	msg = "\nDEFINES:\n"
	for symbol_name in sorted(symbol_table):
		sym = symbol_table[symbol_name]

		msg += symbol_name + "{} was defined at " + sym['definition'].location_string() + "\n"

		expand_definition(symbol_name, symbol_table)

	e = taggedtext.make_error_node("", 0, 0, msg)
	n = taggedtext.make_tag_node("", 0, 0, "LIST_DEFINES")
	n.add_child_back(e)
	symbol_table['LIST_DEFINES'] = { 'status': 'D', 'definition': n }

######################################################################
######################################################################
######################################################################

def run(root):
	symbol_table = {}
	define_helper_pass1(root, symbol_table)
	expand_definitions(symbol_table)
	define_helper_pass2(root, symbol_table)

######################################################################
#
# conditional main() - if called as a command, then run main()
#
def main():
	taggedtext.command(run)

if __name__ == "__main__":
	main()
