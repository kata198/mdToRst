mdToRst
=======

Tool and library to convert markdown to restructed text (md to rst).


This tool performs some basic conversions to attempt to generate a restructed text document (RST) which renders the same, or as close as possible to a provided markdown (md).

This tool is not perfect, and may require that you write your markdown in a certain way that is apt toward conversion, but it does save a lot of time and prevent error.


Usage
=====


	Usage: mdToRst [filename]

		Converts a provided markdown file (.md) to restructed text (.rst)


	If "filename" is provided as "--", the markdown will be read from stdin.


	Example Usage:


		mdToRst README.md | tee README.rst  # Read in README.md, convert to rst, 

											#  and output both to stdout and "README.rst"



		cat README.md | mdToRst         # Pipe in the contents of "README.md", and

										#  output the converted document to stdout


