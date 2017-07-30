# vim: set ts=4 sw=4 st=4 expandtab 
'''
    md_to_rst - Module whose purpose is to convert markdown (md) to restructed text (rst)

    Copyright (c) 2017 Timothy Savannah, All Rights Reserved

    Licensed under terms of the GNU General Public License (GPL) Version 3.0

    You should have recieved a copy of this license as "LICENSE" with the source distribution,
      otherwise the current license can be found at https://github.com/kata198/mdToRst/blob/master/LICENSE


    md_to_rst/__init__.py - "Main" module entry point
'''

import re

__all__ = ('convertMarkdownToRst', )

__version__ = '0.1.0'
__version_tuple__ = (0, 1, 0)


def convertMarkdownToRst(contents):
    '''
        convertMarkdownToRst - Take provided markdown and output equivilant restructed text
    '''
    lines = contents.split('\n')
    numLines = len(lines)

    newLines = []

    for i in range(numLines):
        line = lines[i]

        convertedLines = _getConvertedLines(line, lines, i)

        newLines += convertedLines

    return '\n'.join(newLines)





def _getConvertedLines(line, lines, curIdx):
    '''
        _getConvertedLines - Take a line of markdown, and return the converted RST lines

            @param line <str> - A line from the markdown file

            @return list<str> - A list of converted lines
    '''
    if _isTabbedLine(line):
        return _convertTabbedLine(line)
    elif _isHashTitleLine(line):
        return _convertHashTitle(line)
    elif _isLineBreak(line, lines, curIdx):
        return _addLineBreak(line)
    else:
        return [line]
 

def _isTabbedLine(line):
    '''
        _isTabbedLine - Check if line begins with a tab
    '''
    return line.startswith('\t')

def _convertTabbedLine(line):
    '''
        _convertTabbedLine - Convert an indented line (starts with tab) to RST.

            Will prepend an empty line, to ensure breaking occurs as it did in the markdown.
    '''
    return ['', line]


# HASH_TITLE_LINE_RE - Regular Expression object to match a line defining a "hash" title (the largest header in markdown).
HASH_TITLE_LINE_RE = re.compile('^[  \\t]*[#][ \\t]*')

def _isHashTitleLine(line):
    '''
        _isHashTitleLine - Check if line defines a "hash" title (the largest header in markdown).

          This looks like:

            #MyProject
    '''
    return bool( HASH_TITLE_LINE_RE.match(line) )

def _convertHashTitle(line):
    '''
        _convertHashTitle - Convert a hashed title ( like #MyProject ) to an '=' underlined title.

          This looks like:

            #MyProject

          And will be converted to:

            MyProject
            =========
    '''
    ret = []

    unhashedLine = HASH_TITLE_LINE_RE.sub('', line)
    unhashedLine = unhashedLine.rstrip()

    ret.append( unhashedLine )
    ret.append( '=' * len(unhashedLine) )

    return ret

# LEADING_WHITESPACE_RE - Regular expression object capable of matching and extracting
#   leading whitespace on a line. If it does not match, there is no leading whitespace.
LEADING_WHITESPACE_RE = re.compile('(?P<leading_whitespace>^[ \\t]+)')

def _getLeadingWhitespace(line):
    '''
        _getLeadingWhitespace - Extract the leading whitespace (spaces or tabs at start of line)

          @param line <str> - The line

          @return <str> - The leading whitespace on this line. If the line does not begin with whitespace,
            empty string is returned.
    '''
    matchObj = LEADING_WHITESPACE_RE.match(line)
    if not matchObj:
        return ''
    
    return matchObj.groupdict()['leading_whitespace']

def _isLineBreak(line, lines, lineIdx):
    '''
        _isLineBreak - Check if the provided line would normally trigger a "break" (new line)
          in markdown, but does not in RST.

          @param line <str> - The line to check
          @param lines list<str> - List of all the lines
          @param lineIdx <int> - The index of "line" within "lines"

        If either line is blank (empty or only whitespace), a line break is NOT added.

        Otherwise, if the given line and previous line share the same leading whitespace,
          a line break is force-inserted such that MD and RST render the same
    '''
    if lineIdx == 0:
        return False

    prevLine = lines[lineIdx - 1]
    if not prevLine.strip() or not line.strip():
        return False

    if prevLine.startswith( ('-', '=') ) or  line.startswith( ('-', '=') ):
        return False

    curWhitespace = _getLeadingWhitespace(line)
    prevWhitespace = _getLeadingWhitespace(prevLine)

    if curWhitespace == prevWhitespace:
        return True

    return False

def _addLineBreak(line):
    '''
        _addLineBreak - Adds a line break before "line"
    '''
    return ['', line]

    
# vim: set ts=4 sw=4 st=4 expandtab 
