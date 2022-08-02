#
# This module collects MySite.* parameters
#
# These are the highest level tags that compose the www.MySite.com website
#
# Current clients are: render and blog_maker
#
import os
import sys
import re
import taggedtext
import tt_html
import StringIO

######################################################################
#
# process a tag of this form:
#	Item{B URL{bbbb}}
#
# Return None on error (and print error to stderr)
# Return an object like this on success:
#	{ 'text': "B", 'url': "bbbb" },
#
def process_top_tag_item(root):
	url = None
	text = None

	for child in root.children():
		if child.is_tag() and child.tag() == "URL":
			if url != None:
				sys.stderr.write("%s multiple URL{} tags encountered.\n"
									% (child.location_string()) )
				return None

			ss = StringIO.StringIO()
			child.write_translated(ss)
			url = ss.getvalue().strip()
		else:
			ss = StringIO.StringIO()
			child.write_translated(ss)
			if text == None:
				text = ""
			text += ss.getvalue().strip() + " "

	if url == None:
		sys.stderr.write("%s missing URL{} tag inside of Item{} tag.\n"
							% (root.location_string()) )
		return None

	if text == None:
		sys.stderr.write("%s missing words inside of Item{} tag.\n"
							% (root.location_string()) )
		return None

	text = text.strip()

	return { 'text': text, 'url': url }

######################################################################
#
# Parse this structure:
#
# MySite.top{
#	Item{A URL{word}}
#	Item{B URL{bbbb}}
#	Item{C URL{cccc}}
#	Item{About Name{} URL{about}}
# }
#
# Returns a an array of these objects:
#
# [
#	{ 'text': "A", 'url': "word" },
#	{ 'text': "B", 'url': "bbbb" },
#	...
# ]
#
# The 'text' is left and right trimmed. same with the 'url' text.
#
# Returns None when an error is detected and an error message
# will have been written to stderr.
#
def process_top_tag(root):
	result = []
	for child in root.children():
		if child.is_tag() and child.tag() == "Item":
			v = process_top_tag_item(child)
			if v == None:
				return

			result.append(v)
		else:
			sys.stderr.write("%s unexpected child node in MySite.top{}. Expecting Item{} tags only.\n"
								% (child.location_string()) )
			return None

	return result

######################################################################
#
# Process a node of this form (we already know that 'root' is
# a Link tag)
#
# Link{Link 1 Text		URL{nycphoto.html}}
#
# Return a structure of this form:
#
# {
#	'text': "Link 1 Text", 'url': "nycphoto.html"
# }
#
# Returns None on error and the error message written to stderr.
#
def process_link_tag(root):
	url_children = []
	other_children = []

	#
	# Sort children into two ordered lists, Link's and everything else.
	#
	for child in root.children():
		if child.is_tag() and child.tag() == "URL":
			url_children.append(child)
		else:
			other_children.append(child)

	#
	# Process the URL component
	#
	if len(url_children) == 0:
		sys.stderr.write("%s: Link{} tag has no URL{} tag. Please provide one.\n"
							% (root.location_string()) )
		return None

	if len(url_children) > 1:
		sys.stderr.write("%s: Link{} tag has too many URL{} tags. Just one please.\n"
							% (root.location_string()) )
		return None

	ss = StringIO.StringIO()
	url_children[0].write_translated(ss)
	url = ss.getvalue().strip()

	#
	# Process the other nodes and get into a single string
	#
	n = taggedtext.make_root_node()
	n.set_children(other_children)

	ss = StringIO.StringIO()
	n.write_translated(ss)
	text = ss.getvalue().strip()

	return { 'text': text, 'url': url }

######################################################################
#
# Process a node of this form (we already know that 'root' is
# a Heading tag)
#
#	Heading{
#		Heading One Nodes Go Here
#		Link{Link 1 Text		URL{nycphoto.html}}
#		Link{Link 2 Text		URL{link2html.html}}
#		Link{Link 3 Text		URL{foo.html}}
#	}
#
# Return a structure of this form:
#
#		{ 'heading': "Heading One Nodes Go Here",
#			'links': [
#				{ 'text': "Link 1 Text", 'url': "foobar.html" },
#				{ 'text': "Link 2 Text", 'url': "foobar.html" },
#			]
#		}
#
# Returns None on error and the error message written to stderr.
#
def process_heading_tag(root):
	link_children = []
	other_children = []

	#
	# Sort children into two ordered lists, Link's and everything else.
	#
	for child in root.children():
		if child.is_tag() and child.tag() == "Link":
			link_children.append(child)
		else:
			other_children.append(child)

	#
	# Process the links
	#
	links = []
	for link in link_children:
		v = process_link_tag(link)
		if v == None:
			return None
		links.append(v)

	if len(other_children) == 0:
		sys.stderr.write("%s: No text provided for Heading{} tag.\n"
								% (root.location_string()) )
		return None

	#
	# combine all the "other" children into a tmp node
	# and translate it to a string.
	#
	n = taggedtext.make_root_node()
	n.set_children(other_children)

	ss = StringIO.StringIO()
	n.write_translated(ss)
	heading = ss.getvalue().strip()

	return { 'heading': heading, 'links': links }

######################################################################
# Side tag processing.
# Process this structure:
#
# MySite.side{
#	Heading{
#		Heading One Nodes Go Here
#		Link{Link 1 Text		URL{nycphoto.html}}
#		Link{Link 2 Text		URL{link2html.html}}
#		Link{Link 3 Text		URL{foo.html}}
#	}
#
#	Heading{
#		Heading Two Nodes Go Here
#		Link{Link 1 Text		URL{bar.html}}
#		Link{Link 2 Text		URL{momstuff.html}}
#		Link{Link 3 Text		URL{suestrip.html}}
#	}
#
#	Heading{
#		Heading Three
#		Link{Link 1 Text		URL{blog11.html}}
#		Link{Link 2 Text		URL{blog22.html}}
#		Link{Link 3 Text		URL{nycphoto2.html}}
#	}
# }
#
# Returns this structure:
#
#	[
#		{ 'heading': "Heading One Nodes Go Here",
#			'links': [
#				{ 'text': "Link 1 Text", 'url': "foobar.html" },
#				{ 'text': "Link 2 Text", 'url': "foobar.html" },
#			]
#		}
#	]
#
# Returns None when an error is detected and an error message
# will have been written to stderr.
#
#
def process_side_tag(root):
	result = []
	for child in root.children():
		if child.is_tag() and child.tag() == "Heading":
			v = process_heading_tag(child)
			if v == None:
				return
			result.append(v)
		else:
			sys.stderr.write("%s unexpected child node in MySite.side{}. Expecting Heading{} tags only.\n"
								% (child.location_string()) )
			return None

	return result

######################################################################
# Process all MySite. tags.
# Look at the top level of root
# for all MySite.xxxxx tags
#
# These tags will form the basis
# for the substitution into the template file.
#
# Any MySite.<variable> tags become Jinja2 parameters, of name <variable>
#
# Special handling is provided for:
#		MySite.top{}
# and
#		MySite.side{}
#
def get_template_parameters(root):
	result = {}
	for child in root.children():
		if not child.is_tag():
			continue

		m = re.match(r'^MySite\.(.*)$', child.tag())
		if m == None:
			continue

		parm = m.group(1)

		if parm in result:
			sys.stderr.write("%s duplicate tag MySite.%s{}\n" % (child.location_string(), parm))
			return None

		if parm == "top":
			#
			# Special tag MySite.top{}
			#
			value = process_top_tag(child)
			if value == None:
				return None

			result[parm] = value

		elif parm == "side":
			#
			# Special tag MySite.side{}
			#
			value = process_side_tag(child)
			if value == None:
				return None

			result[parm] = value

		else:
			ss = StringIO.StringIO()
			child.write_translated(ss)
			result[parm] = ss.getvalue().strip()

	return result
