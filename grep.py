import argparse
import sys
import re


def output(line):
    print(line)

def condition(line, params):

    if params.ignore_case and params.invert:
        return not(re.search(str.casefold(params.pattern), str.casefold(line)))    
    elif params.invert:
        return not(re.search(params.pattern, line))
    elif params.ignore_case:
        return re.search(str.casefold(params.pattern), str.casefold(line))
    else:
        return re.search(params.pattern, line)


def context(params, lines, B, A, k):
    L = []
    Flag = 0
    n = 1
    for line in lines:   
        line = line.rstrip()
        L.append(line)

        if len(L) > B + 1:
            del L[0]
            
        if condition(line, params):
            if Flag <= 0: # НЕ в области контекста
                i = len(L) - 1
                for line_ in L:
                    c_n_r(params, line_, k, n - i) # выводим все из буфера
                    i -= 1
                L.clear()
                Flag = A
            else: # В области контекста
                L.clear()
                c_n_r(params, line, k, n)
                Flag = A
        elif Flag > 0: 
            L.clear() # идем в области контекста, буфер не нужен
            c_n_r(params, line, k, n)
            Flag -= 1
        n += 1
    
    if params.count:
            output(str(k[0]))
            

def c_n_r(params, line, k, n):
    if params.count:
        k[0] += 1
    elif params.line_number:
        if condition(line, params):
            output('{}:{}'.format(n, line))
        else:
            output('{}-{}'.format(n, line))
    else:
        output(line)

def grep(lines, params):

    params.pattern = re.sub('\?', '.', params.pattern)
    params.pattern = re.sub('\*{1,}', '.*', params.pattern)

    k = [0]
    
    if params.context != 0:
        context(params, lines, params.context, params.context, k)
   
    elif params.after_context != 0 and params.before_context != 0:
        context(params, lines, params.before_context, params.after_context, k)
    
    elif params.before_context != 0:
        context(params, lines, params.before_context, 0, k)
      
    elif params.after_context != 0:
        context(params, lines, 0, params.after_context, k)           
                
    else:
        n = 1
        for line in lines:
            if condition(line, params):
                line = line.rstrip()
                c_n_r(params, line, k, n)
            n += 1
        if params.count:
            output(str(k[0]))
    


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
