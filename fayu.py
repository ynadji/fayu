#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Given an Anki deck, generate (or grow, 发育) additional cards that will be
# easy for you to learn. For example, if you know the character 国 it would
# provide the character 玉 since it is a component character. Also, if you
# know 又 it would suggest 友. You can toggle which "direction" to go, and
# the number of additional strokes to consider.
#
# Author: Yacin Nadji <yacin@gatech.edu>
#

import sys
from optparse import OptionParser

from cjklib.cjknife import CharacterInfo
from cjklib.characterlookup import CharacterLookup

# Project lib imports
def projectpath(libdir, filedir=__file__):
    """Path's relative to location of the file. Makes it so your scripts don't
    break when run from directories other than the root."""
    import os.path as p
    return p.normpath(p.join(p.dirname(p.realpath(filedir)), libdir))

sys.path.append(projectpath('wulib'))
from wulib import flatten, unique

ci = CharacterInfo()
cl = CharacterLookup('C')

def components(c):
    """Get component characters of the 汉字 c. We ignore components that
    don't have standalone definitions.

    e.g.: 国 -> 囗玉"""
    return [x[0] for x in unique(flatten(cl.getDecompositionEntries(c))) if type(x) == tuple]

def bycomponents(c):
    """Get characters where the 汉字 c is a component.

    e.g.: 又 -> 又叉夂仅凤劝..."""
    return [x[0] for x in ci.getCharactersForComponents(c)]

def _all_hanzi_known(word, hanzi_set):
    s = set(word)
    return s == (s & hanzi_set)

def compounds(s):
    """Given a set of 汉字, s, determine ALL words that can be formed that
    do not exist in the set. For example, if s = (明, 星), the words 明星
    and 星星 would be returned."""
    newwords = set([])
    for word in s: # word could be multiple 汉字
        try:
            for res in ci.searchDictionary('%%%s%%' % word, 'GR'):
                headword = res.HeadwordSimplified
                if _all_hanzi_known(headword, s) and headword not in s:
                    newwords.add(res)
        except AttributeError as e:
            sys.stderr.write('%s: %s\n' % (str(e), word))

    return newwords

def main():
    """main function for standalone usage"""
    usage = "usage: %prog [options] hanzis"
    parser = OptionParser(usage=usage)
    parser.add_option('-b', '--by-components', default=False, action='store_true',
            help='Search for 汉字 that contain the argument(s) as components.'.decode('utf8'))
    parser.add_option('-c', '--compounds', default=False, action='store_true',
            help='Search for word compounds based on a set of known 汉字.'.decode('utf8'))

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return 2

    # do stuff
    if options.compounds:
        s = set(args[0].decode('utf8'))
        for res in compounds(s):
            print('%s\t%s\t%s' % (res.HeadwordSimplified, res.Reading, res.Translation))
    else:
        for c in args[0].decode('utf8'):
            if options.by_components:
                print(', '.join(bycomponents(c)))
            else:
                print(', '.join(components(c)))

if __name__ == '__main__':
    sys.exit(main())
