#
# LINK{Apple Corp. URL{http://www.apple.com}}
#
# REF{bob}
#
# LINK{Bob's Resume URL{#bob}}
#
import taggedtext

#
# Process links
#
def run_link(root):
	#
	# Functor. Returns True if 'n' is the url node
	# Used to remove the URL node from the LINK{} children.
	#
	def del_url(n):
		return n.node is url.node

	if root.is_tag_named("LINK"):
		url = None
		for child in root.children():
			if child.is_tag_named("URL"):
				if url != None:
					n = taggedtext.make_error_node(
								child.filename(),
								child.lineno(),
								child.column(),
								"multiple URL{} tags not allowed inside of LINK{}")
					n.take_children(root)
					root.morph(n)
					return
				url = child

		if url == None:
			n = taggedtext.make_error_node(
						root.filename(),
						root.lineno(),
						root.column(),
						"missing URL{} tag inside of LINK{}")
			n.take_children(root)
			root.morph(n)
			return

		if url.num_children() != 1:
			n = taggedtext.make_error_node(
						url.filename(),
						url.lineno(),
						url.column(),
						"URL{} tag can only have a single word argument")
			n.take_children(url)
			url.morph(n)
			return

		w = url.get_child(0)
		if not w.is_word():
			n = taggedtext.make_error_node(
						url.filename(),
						url.lineno(),
						url.column(),
						"URL{} tag can only have a single word argument")
			n.take_children(url)
			url.morph(n)
			return

		root.delete_children_if(del_url)

		#
		# As a special service to the LINK{} users
		# if there was no other data besides the URL{}
		# then make the URL the text
		#
		if root.num_children() == 0:
			w = taggedtext.make_word_node(
						url.filename(),
						url.lineno(),
						url.column(),
						w.word())
			root.add_child_back(w)

		url_string = w.word()

		n = taggedtext.make_translated_node(
					root.filename(),
					root.lineno(),
					root.column(),
					'<A HREF="%s">' % ( url_string ),
					'</A>' )
		n.take_children(root)
		root.morph(n)
		return

	for child in root.children():
		run_link(child)

#
# Produces this HTML: <A NAME="thing"></A>
#
def run_ref(root):
	if root.is_tag_named("REF"):
		if root.num_children() != 1:
			n = taggedtext.make_error_node(
				root.filename(),
				root.lineno(),
				root.column(),
				"REF{} tag should only have a single argument" )
			n.take_children(root)
			root.morph(n)
			return

		ref = root.get_child(0)

		if not ref.is_word():
			n = taggedtext.make_error_node(
				root.filename(),
				root.lineno(),
				root.column(),
				"REF{} argument must be a single word" )
			n.take_children(root)
			root.morph(n)
			return

		ref_string = ref.word()

		n = taggedtext.make_translated_node(
					root.filename(),
					root.lineno(),
					root.column(),
					'<A NAME="%s">' % ( ref_string ),
					'</A>' )

		root.morph(n)

	for child in root.children():
		run_ref(child)

def run(root):
	run_link(root)
	run_ref(root)
