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

__all__ = ('convertMarkdownToRst', 'ConvertLines', 'ConvertLineData' )

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

        newLine = ConvertLineData.doConvertLineData(line, lines, i)

        convertedLines = ConvertLines.doConvertLine(newLine, lines, i)

        newLines += convertedLines

    return '\n'.join(newLines)


class ConvertLines(object):
    '''
        ConvertLines - Methods which take in a single line, and return a list of 0 or more equivalent lines

          Public Methods:

            doConvertLine - @see ConvertLines.doConvertLine

    '''

    @classmethod
    def doConvertLine(cls, line, lines, curIdx):
        '''
            doConvertLine - Take a line of markdown, and return the converted RST lines

                @param line <str> - A line from the markdown file

                @param lines list<str> - The list of all lines in the markdown file

                @param curIdx <int> - The index of "line" in "lines"


                @return list<str> - A list of converted lines
        '''
        if cls._isTabbedLine(line):
            return cls._convertTabbedLine(line)
        elif cls._isHashTitleLine(line):
            return cls._convertHashTitle(line)
        elif cls._isLineBreak(line, lines, curIdx):
            return cls._addLineBreak(line)
        else:
            return [line]


    @classmethod
    def _isTabbedLine(cls, line):
        '''
            _isTabbedLine - Check if line begins with a tab
        '''
        return line.startswith('\t')

    @classmethod
    def _convertTabbedLine(cls, line):
        '''
            _convertTabbedLine - Convert an indented line (starts with tab) to RST.

                Will prepend an empty line, to ensure breaking occurs as it did in the markdown.
        '''
        return ['', line]


    # HASH_TITLE_LINE_RE - Regular Expression object to match a line defining a "hash" title (the largest header in markdown).
    HASH_TITLE_LINE_RE = re.compile('^[  \\t]*[#][ \\t]*')

    @classmethod
    def _isHashTitleLine(cls, line):
        '''
            _isHashTitleLine - Check if line defines a "hash" title (the largest header in markdown).

              This looks like:

                #MyProject
        '''
        return bool( cls.HASH_TITLE_LINE_RE.match(line) )

    @classmethod
    def _convertHashTitle(cls, line):
        '''
            _convertHashTitle - Convert a hashed title ( like #MyProject ) to an '=' underlined title.

              This looks like:

                #MyProject

              And will be converted to:

                MyProject
                =========
        '''
        ret = []

        unhashedLine = cls.HASH_TITLE_LINE_RE.sub('', line)
        unhashedLine = unhashedLine.rstrip()

        ret.append( unhashedLine )
        ret.append( '=' * len(unhashedLine) )

        return ret

    # LEADING_WHITESPACE_RE - Regular expression object capable of matching and extracting
    #   leading whitespace on a line. If it does not match, there is no leading whitespace.
    LEADING_WHITESPACE_RE = re.compile('(?P<leading_whitespace>^[ \\t]+)')

    @classmethod
    def _getLeadingWhitespace(cls, line):
        '''
            _getLeadingWhitespace - Extract the leading whitespace (spaces or tabs at start of line)

              @param line <str> - The line

              @return <str> - The leading whitespace on this line. If the line does not begin with whitespace,
                empty string is returned.
        '''
        matchObj = cls.LEADING_WHITESPACE_RE.match(line)
        if not matchObj:
            return ''
        
        return matchObj.groupdict()['leading_whitespace']

    @classmethod
    def _isLineBreak(cls, line, lines, lineIdx):
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

        curWhitespace = cls._getLeadingWhitespace(line)
        prevWhitespace = cls._getLeadingWhitespace(prevLine)

        if curWhitespace == prevWhitespace:
            return True

        return False

    @classmethod
    def _addLineBreak(cls, line):
        '''
            _addLineBreak - Adds a line break before "line"
        '''
        return ['', line]


class ConvertLineData(object):
    '''
        Encapsulated class of methods related to converting line data from MD to RST, where they are incompatible.

          This differs from #ConvertLines in the sense that ConvertLines returns zero or more lines of equivilant (mostly used for spacing/formatting), whereas this
            converts the actuald data where the two specs don't line up (like with links)
    '''

    @classmethod
    def doConvertLineData(cls, line, lines, curIdx):
        '''
            doConvertLineData - Take a line of markdown, and convert the data itself to RST where they are not compatible

                @param line <str> - A line from the markdown file

                @param lines list<str> - The list of all lines in the markdown file

                @param curIdx <int> - The index of "line" in "lines"


                @return <str> - The converted line
        '''
        line = cls._convertPointedBrackets(line)

        return line


    @staticmethod
    def _replaceSection(line, startStr, endStr, sectionRE, groupDictToReplacementFunc):
        '''
            _replaceSection - Common code to scan a line for a section that needs replacement,
                                and to apply said replacement zero or more times.

                @param line <str> - The line to process

                @param startStr <str> - The character(s) which begins said section

                @param endStr <str> - The character(s) which ends said section

                @param sectionRE <_sre.SRE_Pattern aka re.compile result> - The regular expression
                            to match a markdown section. Will be applied at each #startStr occurance

                @param groupDictToReplacementFunc <callable [lambda/function] >(dict) - If #sectionRE matches,
                            this function will be called with the group dict of the match, and should return
                            the equivilant section in RST format

                @return <str> - Updated line with all occurances of relevant section converted


                NOTE: If the section is matched, the #startStr and #endStr will NOT be automatically copied
                        into the result. If they need to be retained, #groupDictToReplacementFunc should return them
        '''

        if startStr not in line:
            return line

        remainingLine = line[:]
        ret = []

        # NOTE: This is a little ugly, but covers all kinda of corner cases I can imagine

        keepGoing = True

        while keepGoing is True:
            # Check if '<' is still present
            while startStr in remainingLine[:]:
                nextIdx = remainingLine.index(startStr)
                ret.append( remainingLine[ : nextIdx] )

                remainder2 = remainingLine[ nextIdx : ]

                matchObj = sectionRE.match( remainder2 )
                if not matchObj:
                    # Not a match, just #startStr

                    # Check if we have another occurance of #startStr, and if not, grab the rest of string.
                    #   otherwise, grab up to the next #startStr and reiterate
                    nextNextIdx = None
                    try:
                        nextNextIdx = remainder2[len(startStr):].index(startStr)
                    except:
                        pass

                    # If no more #startStr then grab the rest of string and abort
                    if not nextNextIdx:
                        keepGoing = False
                        ret.append(remainder2)
                        break

                    # Otherwise, grab up to the char before and reiterate (to process an additional potential match)
                    ret.append( remainder2[ : nextNextIdx ] )
                    remainingLine = remainder2 [ nextNextIdx : ]
                else:
                    # We matched the section, so call the provided convert/replace func with the match groupdict
                    newSection = groupDictToReplacementFunc( matchObj.groupdict() )

                    ret.append(newSection)

                    # Move position to one past the #endStr char
                    remainingLine = remainder2[ remainder2.index(endStr) + len(endStr) : ]

            else:
                # If no #startStr, grab the rest of the line and abort
                ret.append( remainingLine )
                keepGoing = False

        return ''.join(ret)
                
    POINTED_BRACKET_URL_RE = re.compile('[<](?P<url>(http|https|ftp|smb|file)[:][/][/][^>]+)[>]')

    @classmethod
    def _convertPointedBrackets(cls, line):
        '''
            _convertPointedBrackets - Converts any urls within provided line
                 like <http://www.example.com> to just http://www.example.com

              @param line <str> - The line

              @return <str> - The line with pointed brackets converted
        '''
        return ConvertLineData._replaceSection(line, '<', '>', 
                    cls.POINTED_BRACKET_URL_RE,
                    lambda groupDict : groupDict['url']
        )


    # oops... accidently did the labeled external hyperlinks from RST instead of frm markdown..
    #      I'll save this, commented-out, for in the future if we do RST -> MD
#    RST_LABELED_EXTERNAL_HYPERLINK_RE = re.compile("""[`](?P<label>(([\\][<])|[^<])+)[ \t]*[<](?P<url>[^(>`_)]+)([>][`][_])""")
#
#    @classmethod
#    def _convertLabeledExternalHyperlinkRST(cls, line):
#        '''
#            _convertLabeledExternalHyperlink - Convert an external hyperlink with a label from MD form to RST form
#
#                    Example: `Python <http://www.python.org/>`_
#
#                @param line <str> - The line
#
#                @return <str> - The line with external hyperlinks with labels converted
#        '''
#        return ConvertLineData._replaceSection(line, "`", ">`_",
#                    cls.LABELED_EXTERNAL_HYPERLINK_RE,
#                    lambda groupDict : "[%s](%s)" %( groupDict['label'].strip(), groupDict['url'])
#        )

        
# vim: set ts=4 sw=4 st=4 expandtab 
