#!/bin/sh
#
# rebuild static site and blog posts
#
# Run this script from 'bin'.
#

# to access python library code
export PYTHONPATH=${PYTHONPATH}:../python

# change directory to input because 'render' and 'blog_maker' look in "." for includes
cd ../input

../bin/render mysite.tmpl ../output *.tt

../bin/blog_maker blog_index.tmpl blog_each.tmpl common.tt blog/*.tt ../output
