# tagged_text
Agnostic Markdown Tagged{Text} and static site generator. I wrote this in 2016 for my personal website. [http://www.etcutmp.com]

# Introduction
The Tagged{Text} markdown format is described here. The python code to process such files is in taggedtext.py.
The static site generator uses tagged{text} for the web content (see 'input' directory). The generated html files are produced
in the 'output' directory'.


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

## LaTeX vs Tagged{Text}

Here is a LaTeX document with comments:
```
% This is a simple sample document.  For more 
documents take a look in the exercise tab. Note that everything that
comes after a % symbol is treated as comment and ignored when the
code is compiled.

\documentclass{article}

\usepackage{amsmath}

\title{Simple Sample}
\author{My Name}
\date{\today}

% The preamble ends with the command \begin{document}
\begin{document}
\maketitle
    
\section{Hello World!}
    
\textbf{Hello World!} Today I am learning \LaTeX.
\LaTeX{} is a great program for writing math. I can write in
line math such as $a^2+b^2=c^2$ %$ tells LaTexX to compile as math.
I can also give equations their own space: 

\begin{equation}
        \gamma^2+\theta^2=\omega^2
\end{equation}

If I do not leave any blank lines \LaTeX{} will continue  this
text without making it into a new paragraph.  Notice how there
was no indentation in the text after equation (1).  
Also notice how even though I hit enter after that sentence and
here $\downarrow$
\LaTeX{} formats the sentence without any break.  Also   look
how      it   doesn't     matter          how    many  spaces     I
put     between       my    words.
For a new paragraph I can leave a blank space in my code. 

\end{document}
```

I always liked the appearance of TeX and LaTeX while editing them, so
Tagged{Text} was made to look similar:

```
%{ This is a simple sample document.  For more 
documents take a look in the exercise tab. Note that everything that
comes after a % symbol is treated as comment and ignored when the
code is compiled. }

documentclass{article}

usepackage{amsmath}

title{Simple Sample}
author{My Name}
date{today{}}

%{ The preamble ends with the command begin{document} }
begin{document}
maketitle{}
    
section{Hello World!}
    
textbf{Hello World!} Today I am learning LaTeX{}.
LaTeX{} is a great program for writing math. I can write in
line math such as $${a^2+b^2=c^2} %{ tells LaTeX to compile as math.}
I can also give equations their own space: 

equation<<END
    gamma^2+theta^2=omega^2
END

If I do not leave any blank lines LaTeX{} will continue  this
text without making it into a new paragraph.  Notice how there
was no indentation in the text after equation (1).  
Also notice how even though I hit enter after that sentence and
here $${downarrow}
LaTeX{} formats the sentence without any break.  Also   look
how      it   doesn't     matter          how    many  spaces     I
put     between       my    words.
For a new paragraph I can leave a blank space in my code. 

end{document}
```
