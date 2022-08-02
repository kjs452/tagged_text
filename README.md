# tagged_text
Agnostic Markdown Tagged{Text} and static site generator


```
P{
This is a I{simple} example of B{Tagged{Text}}. Here is a program:

  Code<<_EOF_
  main()
  {
	  printf("Hello, World!\n");
  }
  _EOF_

}

P{Click LINK{here URL{http://wwww.url.com?abc90} to visit site.}
P{Escape chars: '\{' and '\}' and '\\'}
```

This example demonstrates every feature of Tagged{Text}. A Tagged{Text} document is broken down into the following constructs:

## Tags:
These are introduced via the use of curly braces, preceeded by a tag name.

## Heredocs:
There is one Heredoc in this example, with its own tag name Code. Heredocs allow blocks of text to be introduced which will not be interpreted.

## Words:
Words are any whitespace seperated text that is not a Tag or a Heredoc.

## Escape Characters:
The escape character is the backslash \. It may only preceed the characters {, }, < and \.

## White-space:
White-space is used to delimit words and the beginning of tags and heredocs. Whitespace conists of space, tab and newline characters. Except for delimiting constructs whitespace is stripped from the Tagged{Text} tree. Only in heredocs is whitespace preserved.


Tagged{ Text} is a file format for tagging and organizing text with tags. These tags can be whatever the author wishes them to be. For example the I{...} tag used in the example above could mean "italics".

This diagram shows how the tagged{text} example above was parsed into a tree:

!["TaggedText Tree"](https://github.com/kjs452/tagged_text/blob/main/doc/tt_tree10.png "TaggedText Tree")


