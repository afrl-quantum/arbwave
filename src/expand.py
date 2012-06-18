# This module was taken from the python mailing list
# Archive/python/python/769679
# author john.haxby@oracle 

import re

def expand_braces (string):
    pos = string.find('{')
    # simple, single element string
    if pos < 0:
            return [string]

    # find the left, middle comma-separated string and the right
    left = string[:pos]
    middle = []
    count = 1
    for i in range(pos+1,len(string)):
        if count == 1 and string[i] == ',':
            middle.append(string[pos+1:i])
            pos = i
        elif count == 1 and string[i] == '}':
            middle.append(string[pos+1:i])
            pos = i
            break
        elif string[i] == '{':
            count += 1
        elif string[i] == '}':
            count -= 1
    right = string[pos+1:]
    
    # just "{x..y}" is a special case
    if len(middle) == 1:
        r = re.match("^(-?\d+)\.\.(-?\d+)$", middle[0])
        if not r:
            r = re.match("^(.)\.\.(.)$", middle[0])
    else:
        r = None
    if r:
        middle = []
        start = r.group(1)
        end = r.group(2)
        if len(start) != 1 or len(end) != 1:
            mapper = str
            start = int(start)
            end = int(end)
        else:
            mapper = chr
            start = ord(start)
            end = ord(end)
        if start <= end:
            middle = map(mapper, range(start, end+1))
        else:
            middle = map(mapper, range(start, end-1, -1))

    # join all the bits together
    result = []
    right = expand_braces(right)
    for m in middle:
        for m1 in expand_braces(m):
            for r in right:
                result.append("".join((left, m1, r)))
    return result

        
if __name__ == "__main__":
    from pprint import pprint
    def e(s, r):
        res = " ".join(expand_braces(s))
        if res != r:
            print "*** FAILED: '%s'" % s
            print "  -EXPECTED '%s'" % r
            print "  ------GOT '%s'" % res
    e('hello', 'hello')
    e('{hello,world}', 'hello world')
    e('x{a,b}', 'xa xb')
    e('x{a,b,c}y', 'xay xby xcy')
    e('A{1,2,3}B-C{4,5,6}D', 'A1B-C4D A1B-C5D A1B-C6D A2B-C4D A2B-C5D A2B-C6D A3B-C4D A3B-C5D A3B-C6D')
    e('a{b,<{c,d}>}e', 'abe a<c>e a<d>e')
    e('{1..10x}', '1..10x')
    e('{x1..10}', 'x1..10')
    e('{1..10}', '1 2 3 4 5 6 7 8 9 10')
    e('a{1..10}b', 'a1b a2b a3b a4b a5b a6b a7b a8b a9b a10b')
    e('{a,b}1..10', 'a1..10 b1..10')
    e('{a,9..13,b}', 'a 9..13 b')
    e('<{a,{9..13},b}>', '<a> <9> <10> <11> <12> <13> <b>')
    e('electron_{n,{pt,eta,phi}[{1,2}]}', 'electron_n electron_pt[1] electron_pt[2] electron_eta[1] electron_eta[2] electron_phi[1] electron_phi[2]')
    e('Myfile{1,3..10}.root', 'Myfile1.root Myfile3..10.root')
    e('Myfile{1,{3..10}}.root', 'Myfile1.root Myfile3.root Myfile4.root Myfile5.root Myfile6.root Myfile7.root Myfile8.root Myfile9.root Myfile10.root')
    e('{pre,,post}amble', 'preamble amble postamble')
    e('amble{a,b,}}', 'amblea} ambleb} amble}')
    e('{1..10}', '1 2 3 4 5 6 7 8 9 10')
    e('{a..j}', 'a b c d e f g h i j')
    e('{10..1}', '10 9 8 7 6 5 4 3 2 1')
    e('{j..a}', 'j i h g f e d c b a')
    e('{10..-10}', '10 9 8 7 6 5 4 3 2 1 0 -1 -2 -3 -4 -5 -6 -7 -8 -9 -10')
