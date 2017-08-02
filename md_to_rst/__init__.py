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
import sys
import traceback

__all__ = ('convertMarkdownToRst', 'ConvertLines', 'ConvertLineData' )

__version__ = '0.2.0'
__version_tuple__ = (0, 2, 0)


# NUM_SPACES_PER_TAB - The number of "space" characters which are considered the same as a tab
NUM_SPACES_PER_TAB = 4


# IS_DEVELOPER_DEBUG - Set to True to get developer debug messages
IS_DEVELOPER_DEBUG = False

if IS_DEVELOPER_DEBUG is False:
    def debugmsg(msg, msgTupleLambda=None):
        '''
            debugmsg - shunt
        '''
        pass
else:
    def debugmsg(msg, msgTupleLambda=None):
        '''
            debugmsg - If #IS_DEVELOPER_DEBUG is changed to True (in the code, changing it after import has no affect ) this will print a debug message

                        to stderr prefixed with "DEBUG: " and suffixed with a newline.

                       Don't create your message like:

                           debugmsg( "Order(id=%s) has %d pepperoni pizzas" %( myOrder.id, len( [ topping for pizza in getPizzas() for topping in pizza.toppings() if 'pepperoni' in topping ] ) ) )

                       Which would evaluate that comprehension whether or not debug mode is on,

                         Instead, use a lambda to return that same tuple, so that code is only evaluated in the #debugmsg function calls your lambda:

                           debugmsg( "Order(id=%s) has %d pepperoni pizzas", lambda : ( myOrder.id, len( [ topping for pizza in getPizzas() for topping in pizza.toppings() if 'pepperoni' in topping ] ) ) )
        '''

        if issubclass(msgTupleLambda.__class__, (tuple, list)):
            sys.stderr.write('''WARNING: debugmsg called with a tuple/list for msgTupleLambda.\n\tShould be a lambda that returns the tuple, so when IS_DEVELOPER_DEBUG=False it is not evaluated. \n\n''' + ''.join(traceback.format_stack()[:-1]) + "\n\n" )

            msgTuple = msgTupleLambda
        else:
            msgTuple = msgTupleLambda()

        sys.stderr.write('DEBUG: %s\n' % msgTuple )



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

        line = cls._replaceLeadingWhitespace(line)


        if cls._isTabbedLine(line):
            return cls._convertTabbedLine(line, lines, curIdx)
        elif cls._isHashTitleLine(line):
            return cls._convertHashTitle(line)
        elif cls._isNeedingLineBreak(line, lines, curIdx):
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
    def _convertTabbedLine(cls, line, lines, curIdx):
        '''
            _convertTabbedLine - Convert an indented line (starts with tab) to RST.

                Will prepend an empty line, to ensure breaking occurs as it did in the markdown.
        '''
        if curIdx == 0:
            return [line]
        if not line.strip():
            return [line]

        prevLine = lines[curIdx - 1]

        if not prevLine.strip() or not line.strip():
            return [line]

        return ['', line]


    UNORDERED_LIST_RE = re.compile('[\s]{0,%d[ ][ \\t]+' %( NUM_SPACES_PER_TAB, ))

    @classmethod
    def _isUnorderedListLine(cls, line):
        '''
            _isUnorderedListLine - Detect if line is to be rendered as an unordered list.

              An unordered list begins with 0 to ( NUM_SPACES_PER_TAB - 1 ) spaces, followed by an astrick '*', followed by a (space or tab)

        '''

        # Check the format
        return bool( cls.UNORDERED_LIST_RE.match(line) )


    # HASH_TITLE_LINE_RE - Regular Expression object to match a line defining a "hash" title (the largest header in markdown).
    HASH_TITLE_LINE_RE = re.compile('^[#][ \\t]*')

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
    LEADING_WHITESPACE_RE = re.compile('^(?P<leading_whitespace>[ \\t]+)')

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
    def _convertLeadingWhitespaceToIndentLevel(cls, leadingWhitespace):
        '''
            _convertLeadingWhitespaceToIndentLevel - Count the number of "units" (indent levels) based on leading whitespace.

                Each tab counts as 1, each #NUM_SPACES_PER_TAB consecutive count as one.

                @param leadingWhitespace <str> - The leading whitespace on a line

                @return <int> - Number of indent "units"
        '''
        # The spaces must be consecutive
        return leadingWhitespace.count('\t') + leadingWhitespace.count(' ' * NUM_SPACES_PER_TAB)

    @classmethod
    def _getIndentLevel(cls, line):
        '''
            _getIndentLevel - Gets the indent level of this line

        '''

        leadingWhitespace = cls._getLeadingWhitespace(line)

        if not leadingWhitespace:
            return 0

        return cls._convertLeadingWhitespaceToIndentLevel(leadingWhitespace)

    # REPLACE_LEADING_WHITESPACE_RE - For replacing leading whitespace
    REPLACE_LEADING_WHITESPACE_RE = re.compile('^(?P<leading_whitespace>[ \\t]+)(?P<content>.*)$')


    SPACES_EQUIV_TAB_RE = re.compile('[ ]{' + str(NUM_SPACES_PER_TAB) + '}')

    @classmethod
    def _replaceLeadingWhitespace(cls, line):
        '''
            _replaceLeadingWhitespace - Replace leading whitespace which could be a combination of tabs and spaces,
                
                into the indent level * tabs followed by any additional spaces. This greatly simplifies logic and patterns

                and should be done first.

        '''
        matchObj = cls.REPLACE_LEADING_WHITESPACE_RE.match(line)
        if not matchObj:
            # Minor optimization, we use a "+" instead of "*" because if we don't match at least one whitespace char,
            #   we don't need to process the rest of this function. just return as-is
            return line

        groupDict = matchObj.groupdict()

        leadingWhitespace = groupDict['leading_whitespace']
        leadingWhitespace = cls.SPACES_EQUIV_TAB_RE.sub('\t', leadingWhitespace)

        return leadingWhitespace + groupDict['content']

    @classmethod
    def _isNeedingLineBreak(cls, line, lines, lineIdx):
        '''
            _isNeedingLineBreak - Check if the provided line would normally trigger a "break" (new line)
              in markdown, but does not in RST.

              @param line <str> - The line to check
              @param lines list<str> - List of all the lines
              @param lineIdx <int> - The index of "line" within "lines"

            If either line is blank (empty or only whitespace), a line break is NOT added.

            Otherwise, if the given line and previous line share the same leading whitespace,
              a line break is force-inserted such that MD and RST render the same
        '''
        # If first line, don't worry about prior spacing
        if lineIdx == 0:
            return False

        # If empty line, don't add extra spacing
        if not line.strip():
            return False

        # If previous line is empty, we treat line breaks the same
        prevLine = lines[lineIdx - 1]
        if not prevLine.strip():
            return False

        # If previous line is the underline of a title, or this line is the underline,
        #   do not add spacing.
        if prevLine.startswith( ('-', '=') ) or  line.startswith( ('-', '=') ):
            return False


        curWhitespace = cls._getLeadingWhitespace(line)
        prevWhitespace = cls._getLeadingWhitespace(prevLine)

        curIndentLevel = cls._convertLeadingWhitespaceToIndentLevel(curWhitespace)
        prevIndentLevel = cls._convertLeadingWhitespaceToIndentLevel(prevWhitespace)


        # If an unordered list, there are special rules
        if cls._isUnorderedListLine(line):

            if curIndentLevel == 0 and prevIndentLevel == 0 and len(curWhitespace) >= len(prevWhitespace):
                # If we are on the first indent level,
                #  and have either the same number of prefixed space characters or less,
                #  markdown forces a linebreak and RST does not.
                return True

            # Otherwise, indent rules are the same
            return False

        # Sub list rules seem to be the same, so far as I've tested..

        if curIndentLevel < prevIndentLevel or ( curIndentLevel == prevIndentLevel and len(curWhitespace) >= len(prevWhitespace) ):
            # In MD, if we've went down a full indent level, or if we are at the same level but have more leading spaces than prev line,
            #   we add an implicit line break.
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

        # TODO: Maybe refactor so we aren't calling across worker classes here?
        line = ConvertLines._replaceLeadingWhitespace(line)

        # For now, omit the following on preformatted text.
        if not line.startswith('\t'):
            line = cls._convertPointedBrackets(line)
            line = cls._convertLabeledExternalHyperlink(line)
            line = cls._convertUnderscoreDecorations(line)
        else:
            # RST does not know what "preformatted" means and allows unescaped stuff..
            #   So escape everything so MD == RST in representation
            line = cls._convertEscapes(line)

        return line


    @staticmethod
    def _replaceSection(line, startStr, endStr, sectionRE, groupDictToReplacementFunc, omitEscapedStart=True):
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

                @param omitEscapedStart <bool> default True, If True, will not count "startStr" that is preceded directly by an escape ( '\' )

                   For example, if #startStr is "__" and the string contains "\__Hello__", if omitEscapedStart=True this will not match.

                @return <str> - Updated line with all occurances of relevant section converted


                NOTE: If the section is matched, the #startStr and #endStr will NOT be automatically copied
                        into the result. If they need to be retained, #groupDictToReplacementFunc should return them
        '''
        if startStr not in line:
            return line

        remainingLine = line[:]
        ret = []

        # NOTE: This is a little ugly, but covers all kinda of corner cases I can imagine

        if omitEscapedStart:
            
            # For the following, we prefix the "haystack" with a dummy character.
            #   This is because our RE search scans 1 character BEFORE the search string,
            #    to omit escapes.
            #
            #  Prefixing the string both allows us to match on the first character in a line,
            #    and causes the returned index (which will point to the char before) to line up
            #    in the right place, by offsetting the whole line right 1.
            startOrNone = lambda searchResult : searchResult is not None and searchResult.start() or None

            startStrRE = re.compile('[^\\\\]' + re.escape(startStr) )
            findNextIdxStart = lambda haystack : startOrNone( startStrRE.search( '^' + haystack ) )

            endStrRE = re.compile('[^\\\\]' + re.escape(endStr) )
            findNextIdxEnd = lambda haystack : startOrNone( endStrRE.search( '^' + haystack ) )

        else:
            def findNextIdxStart(haystack):
                try:
                    return haystack.index(startStr)
                except:
                    return None

            def findNextIdxEnd(haystack):
                try:
                    return haystack.index(endStr)
                except:
                    return None

        # Since we cannot do an assignment in a conditional, like in C could do:
        #
        #           while ( (nextIdx = findNextIdxStart(remainingLine) ) != None ) )
        #
        #    to prevent double-searches, we have to use a "while True", 
        #     and at the start perform the conditional, optionally breaking.
        #    We will also break at the end of the loop.


        nextIdx = findNextIdxStart(remainingLine)

        while nextIdx is not None:

            # Append to result the current head to one character prior to the next occurance of #startStr
            ret.append( remainingLine[ : nextIdx] )

            # Put remainder of line starting at #startStr into #nextRemainingLine
            nextRemainingLine = remainingLine[ nextIdx : ]

            # See if the section beginning with #startStr is a match
            matchObj = sectionRE.match( nextRemainingLine )

            if not matchObj:
                # Not a match, so move the head up to the next start, or end the loop.

                remainingLine = nextRemainingLine


                # Find next occurance of startStr, skipping over the length of startStr (since it is currently at head)
                nextIdx = findNextIdxStart( nextRemainingLine[len(startStr) : ])

                # If we have a match, extend the index past what we skipped
                if nextIdx is not None:
                    nextIdx += len(startStr)

#                if nextIdx is None:
#                    # No more occurances, break out of loop (which will append the remainder of data)
#                    break

            else:
                # We matched the section, so call the provided convert/replace func with the match groupdict
                newSection = groupDictToReplacementFunc( matchObj.groupdict() )

                # Append the converted section
                ret.append(newSection)

                # Move past the start so we can find the end (incase startStr and endStr are the same)
                nextRemainingLine = nextRemainingLine[len(startStr) : ]

                # Scan for the #endStr instead of using the span on the #matchObj, 
                #   because the regex could match past the endStr if the pattern requires
                pastEndIdx = findNextIdxEnd ( nextRemainingLine )

                # remainingLine will now move past the end of the converted section (past the #endStr)
                remainingLine = nextRemainingLine[ pastEndIdx + len(endStr) : ]

                # Find next occurance of startStr
                nextIdx = findNextIdxStart( remainingLine )

        # No more matches, append rest of string
        ret.append( remainingLine )

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

    LABELED_EXTERNAL_HYPERLINK_RE = re.compile("""[\[](?P<label>(([\\][\]])|[^\]])+)[\]][ \t]*[\(][ \t]*(?P<url>[^( \t*")\)]+)[ \t]*(["].+["]){0,1}[\)]""")

    @classmethod
    def _convertLabeledExternalHyperlink(cls, line):
        '''
            _convertLabeledExternalHyperlink - Convert an external hyperlink with a label from MD to RST form

                    Example: [Cool Search Site](https://www.duckduckgo.com)

                @param line <str> - The line

                @return <str> - The line with external hyperlinks with labels converted

                NOTE: If the markdown link has a title (hover text), the hover text is dropped as RST does not support it.
                        Example:   [Cool Search Site](https://www.duckduckgo.com "Quack Quack")
        '''
        return ConvertLineData._replaceSection(line, '[', ')', 
                    cls.LABELED_EXTERNAL_HYPERLINK_RE,
                    lambda groupDict : "`%s <%s>`_" %(groupDict['label'].strip(), groupDict['url'].strip())
        )


    UNDERSCORE_BOLD_RE = re.compile('''(?<![\\\\])(?:[\\\\]{2})*__(?P<text>(?:(?<![\\\\])(?:[\\\\]{2})*[\\\\]_|[^_])+(?<![\\\\])(?:[\\\\]{2})*)__''')

    UNDERSCORE_EM_RE = re.compile('''(?<![\\\\])(?:[\\\\]{2})*_(?P<text>(?:(?<![\\\\])(?:[\\\\]{2})*[\\\\]_|[^_])+(?<![\\\\])(?:[\\\\]{2})*)_''')


    @classmethod
    def _convertUnderscoreDecorations(cls, line):
        line = ConvertLineData._replaceSection(line, '__', '__',
                    cls.UNDERSCORE_BOLD_RE,
                    lambda groupDict : "**%s**" %(groupDict['text'], )
        )

        line = ConvertLineData._replaceSection(line, '_', '_',
                    cls.UNDERSCORE_EM_RE,
                    lambda groupDict : "*%s*" %(groupDict['text'], )
        )

        return line

    BACKSLASH_RE = re.compile('[\\\\]')

    STAR_RE = re.compile('[\*]')

    DASH_RE = re.compile('[\-]')

    UNDERSCORE_RE = re.compile('[_]')

    PREFORMAT_ESCAPE_RES = ( 
        (BACKSLASH_RE, '\\\\\\\\'), 
        (STAR_RE, '\\*'),
        (DASH_RE, '\\-'),
        (UNDERSCORE_RE, '\\_'),
    )

    @classmethod
    def _convertEscapes(cls, line):
        '''
            _convertEscapes - Escape all special characters, for use within preformatted text.

                These characters do not require escaping in MD (which actually assumes the text is preformatted!),
                  but they do in RST.

        '''
        for matchRE, replaceWith in cls.PREFORMAT_ESCAPE_RES:
            line = matchRE.sub(replaceWith, line)

        return line
        

    # oops... accidently did the labeled external hyperlinks from RST instead of frm markdown..
    #      I'll save this, commented-out, for in the future if we do RST -> MD
#    RST_LABELED_EXTERNAL_HYPERLINK_RE = re.compile("""[`](?P<label>(([\\][<])|[^<])+)[ \t]*[<](?P<url>[^(>`_)]+)([>][`][_])""")
#
#    @classmethod
#    def _convertLabeledExternalHyperlinkRST(cls, line):
#        '''
#            _convertLabeledExternalHyperlinkRST - Convert an external hyperlink with a label from RST to MD form
#
#                    Example: `Python <http://www.python.org/>`_
#
#                @param line <str> - The line
#
#                @return <str> - The line with external hyperlinks with labels converted
#        '''
#        return ConvertLineData._replaceSection(line, "`", ">`_",
#                    cls.RST_LABELED_EXTERNAL_HYPERLINK_RE,
#                    lambda groupDict : "[%s](%s)" %( groupDict['label'].strip(), groupDict['url'])
#        )

        
# vim: set ts=4 sw=4 st=4 expandtab 
