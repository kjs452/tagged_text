#!/usr/bin/python
#
# This is a little calculator using integers and real numbers.
#
# Use 3.0 instead of 3 to use real numbers.
#
# Calculate{2+2}
#
# I am Calculate{ CurrentYear{} - BirthYear{} } years old.
#
# You can nest Calculate{}:
#
# A dozen is Calculate{ Calculate{2+2} * Calculate{3} } items.
#
# You can control the precision with:
#		Calculate{ 567/(45*2) Prec{3} }
#
# This uses 3 decimals. The default it 0 decimals.
#
import taggedtext

def collect_expression(properties, words, root):
	for child in root.children():
		if child.is_word():
			words.append( child.word() )

		elif child.is_tag_named("Prec"):
			if child.num_children() == 1 and child.get_child(0).is_word():
					try:
						properties['Prec'] = int(child.get_child(0).word())
						if properties['Prec'] < 0:
							raise ValueError
					except ValueError:
						properties['Prec'] = 0

						n = taggedtext.make_error_node(
							child.filename(),
							child.lineno(),
							child.column(),
							"Prec{} precision must be an integer")

						properties['Errors'].append(n)
			else:
				n = taggedtext.make_error_node(
					child.filename(),
					child.lineno(),
					child.column(),
					"Invalid Prec{} specification, should be an integer")
				properties['Errors'].append(n)

		else:
			n = taggedtext.make_error_node(
					child.filename(),
					child.lineno(),
					child.column(),
					"invalid tag inside of Calculate{} tag")
			properties['Errors'].append(n)
			return

def process_calculate_tag(root):
	words = []
	properties = { 'Prec': 0, 'Errors': [] }

	collect_expression(properties, words, root)

	if len(properties['Errors']) > 0:
		result = []
		for child in properties['Errors']:
			result.append(child)
		return result

	expression = ' '.join(words)

	try:
		ns =  {'__builtins__': None}
		result = "%.*f" % ( properties['Prec'], eval(expression, ns) )
	except SyntaxError, e:
		n = taggedtext.make_error_node(
				root.filename(),
				root.lineno(),
				root.column(),
				"expression: '" + expression + "', error: " + str(e) )
		return [n]

	n = taggedtext.make_word_node(
			root.filename(),
			root.lineno(),
			root.column(),
			result)

	return [n]

def run(root):
	eval_functions = { 'Calculate': process_calculate_tag }
	root.eval(eval_functions)

######################################################################
#
# conditional main() - if called as a command, then run main()
#
def main():
	taggedtext.command(run)

if __name__ == "__main__":
	main()
