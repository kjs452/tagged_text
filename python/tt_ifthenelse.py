#!/usr/bin/python
#
# IFEQUAL{ word1 word2 THEN{ true stuff } ELSE{ false stuff } }
#
# This tag gets replaced with 'true stuff' or 'false stuff'
#
# The ELSE clause is optional, in which case this tag evaluates
# to nothing is word1 and word2 are not equal
#
# word1 and word2 MUST be word nodes, or an error is generated.
#
#
import taggedtext

def process_ifequal(n):
	num = n.num_children()
	if num == 4:
		word1 = n.get_child(0)
		word2 = n.get_child(1)
		then_node = n.get_child(2)
		else_node = n.get_child(3)
	elif num == 3:
		word1 = n.get_child(0)
		word2 = n.get_child(1)
		then_node = n.get_child(2)
		else_node = None
	else:
		n = taggedtext.make_error_node(
					n.filename(),
					n.lineno(),
					n.column(),
					"IFEQUAL{} tag wrong numbers of arguments, must have 3 or 4 children" )
		return [n]

	if not word1.is_word():
		n = taggedtext.make_error_node(
					word1.filename(),
					word1.lineno(),
					word1.column(),
					"IFEQUAL{} tag 1st child must be 'word node' but got %s" % word1.node_type_string() )
		return [n]

	if not word2.is_word():
		n = taggedtext.make_error_node(
					word2.filename(),
					word2.lineno(),
					word2.column(),
					"IFEQUAL{} tag 2nd child must be 'word node' but got %s" % word2.node_type_string() )
		return [n]

	if not then_node.is_tag_named("THEN"):
		n = taggedtext.make_error_node(
					then_node.filename(),
					then_node.lineno(),
					then_node.column(),
					"IFEQUAL{} tag 3rd child must be 'THEN{} tag' but got %s" % then_node.node_type_string() )
		return [n]

	if else_node != None and not else_node.is_tag_named("ELSE"):
		n = taggedtext.make_error_node(
					else_node.filename(),
					else_node.lineno(),
					else_node.column(),
					"IFEQUAL{} tag 4th child must be 'ELSE{} tag' but got %s" % else_node.node_type_string() )
		return [n]

	if word1.word() == word2.word():
		return list(then_node.children())
	elif else_node != None:
		return list(else_node.children())
	else:
		return []

def run(root):
	eval_functions = {
		'IFEQUAL':	process_ifequal,
	}

	root.eval(eval_functions)

######################################################################
#
# conditional main() - if called as a command, then run main()
#
def main():
	taggedtext.command(run)

if __name__ == "__main__":
	main()
