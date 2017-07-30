# mdToRst
Tool and library to convert markdown to restructed text (md to rst).


This tool performs some basic conversions to attempt to generate a restructed text document (RST) which renders the same, or as close as possible to a provided markdown (md).

This tool is not perfect, and may require that you write your markdown in a certain way that is apt toward conversion, but it does save a lot of time and prevent error.


Why?
====

It does not make sense and is very error prone to manage two different copies of the same documentation.

I really like markdown, and I absolutely despise restructed text.
Unfortunately, github prefers markdown and pypi will only use RST, so all of my python projects need to have a distinct MD and RST.

The goal here is to simplify things to where you only have to write and maintain a markdown copy (README.md), and after changes you simply run README.md through mdToRst in order to output README.rst .

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



Modification
------------

If you have a usage scenario where mdToRst generates incorrect or suboptimal results, please submit an issue detailing:

* How to reproduce the issue

* What the expected result is

* Why this makes sense

* How to achieve the equivilant in RST


and optionally submit a patch as well.

