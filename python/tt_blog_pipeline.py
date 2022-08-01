#!/usr/bin/python
#
# This is the pipeline used for processing the BLOG files.
#
# run_pass1() must be applied to the whole tagged text tree document, it
# handles normal stuff, like macros, includes, etc..
#
# run_pass2() does the HTML / word processing. it can be applied
# to individual pieces of the tagged text files
#
import taggedtext
import tt_randomtext
import tt_include
import tt_code
import tt_hdbar
import tt_macros
import tt_words
import tt_datetime
import tt_simple_tags
import tt_links
import tt_taggedtext_logo
import tt_image
import tt_calculate
import tt_lists
import tt_ifthenelse

def run_pass1(root):
	#
	# Early processing:
	# These general things should happen first
	#
	tt_include.run(root, ["."])
	tt_macros.run(root)
	tt_randomtext.run(root)

	#
	# Middle processing
	#
	tt_datetime.run(root)
	tt_calculate.run(root)

	#
	# Late Processing
	#
	tt_ifthenelse.run(root)

def run_pass2(root):
	#
	# These filters happen at the end
	#
	tt_hdbar.run(root)
	tt_simple_tags.run(root)
	tt_code.run(root)
	tt_links.run(root)
	tt_taggedtext_logo.run(root)
	tt_image.run(root)
	tt_lists.run(root)

	#
	# word processing should probably happen at the end
	#
	tt_words.run(root)

def run(root):
	tt_simple_tags.clear_toc()
	run_pass1(root)
	run_pass2(root)

######################################################################
#
# conditional main() - if called as a command, then run main()
#
def main():
	taggedtext.command(run)

if __name__ == "__main__":
	main()
