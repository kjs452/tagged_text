#
# IMG{photo/logo.jpg}		left aligned image
#
# Creates an HTML image tag
#
#
import taggedtext

def process_img_tag(root, tag, style):
	nc = root.num_children()
	if nc != 1:
		n = taggedtext.make_error_node(
			root.filename(),
			root.lineno(),
			root.column(),
			"%s{} tag must have one child not %d" % (tag, nc) )

		n.take_children(root)
		root.morph(n)
		return

	c = root.get_child(0)
	if not c.is_word():
		n = taggedtext.make_error_node(
			root.filename(),
			root.lineno(),
			root.column(),
			"%s{} tag argument not a word" % (tag))

		n.take_children(root)
		root.morph(n)
		return

	image_file = c.word()

	n = taggedtext.make_translated_node(
			root.filename(),
			root.lineno(),
			root.column(),
			'<IMG class="%s" SRC="%s">' % (style, image_file),
			'')
	root.morph(n)

def run(root):
	if root.is_tag_named("IMG"):
		process_img_tag(root, "IMG", "ImgLeft")

	elif root.is_tag_named("IMGR"):
		process_img_tag(root, "IMGR", "ImgRight")

	elif root.is_tag_named("IMGC"):
		process_img_tag(root, "IMGC", "ImgCenter")

	for child in root.children():
		run(child)
