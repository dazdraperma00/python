import argparse
import sys
import re

def output(line):
    print(line)

def condition(line, pattern):
    pattern = re.sub('\?', '.', pattern)
    pattern = re.sub('\*{1,}', '.*', pattern)
    result = re.search(pattern, line)
    if result == None:
        return False
    else:
        return True

def grep(lines, params):
    # обработка нашего списка
    for i in range(len(lines)):
        lines[i] = lines[i].rstrip()
    
    if params.ignore_case and params.invert:
        for i in range(len(lines)):
            if not(condition(str.casefold(lines[i]), str.casefold(params.pattern))):
                lines[i] = lines[i] + '\n' # помечаем нужные нам строки, чтобы потом их найти    
    elif params.invert:
        for i in range(len(lines)):
            if not(condition(lines[i], params.pattern)):
                lines[i] = lines[i] + '\n' # помечаем нужные нам строки, чтобы потом их найти
    elif params.ignore_case:
        for i in range(len(lines)):
            if condition(str.casefold(lines[i]), str.casefold(params.pattern)):
                lines[i] = lines[i] + '\n' # помечаем нужные нам строки, чтобы потом их найти
    else:
        for i in range(len(lines)):
            if condition(lines[i], params.pattern):
                lines[i] = lines[i] + '\n' # помечаем нужные нам строки, чтобы потом их найти
    
    # проверяем на наличие контекстов
    if params.context != 0:
        for i in range(len(lines)):
            if lines[i][-1] == '\n':
                if i - params.context >= 0:
                    for j in range(i - params.context, i):
                        if lines[j][-1] == '\n':
                            continue
                        lines[j] = '\n' + lines[j] # контекстные помечаем по другому
                else:
                    for j in range(0, i):
                        if lines[j][-1] == '\n':
                            continue
                        lines[j] = '\n' + lines[j] # контекстные помечаем по другому
                        
                if i + params.context < len(lines):
                    for j in range(i + 1, i + 1 + params.context):
                        if lines[j][-1] == '\n':
                            continue
                        lines[j] = '\n' + lines[j] # контекстные помечаем по другому
                else:
                    for j in range(i + 1, len(lines)):
                        if lines[j][-1] == '\n':
                            continue
                        lines[j] = '\n' + lines[j] # контекстные помечаем по другому
                        
    if params.after_context != 0:
        for i in range(len(lines)):
            if lines[i][-1] == '\n':
                if i + params.after_context < len(lines):
                    for j in range(i + 1, i + 1 + params.after_context):
                        if lines[j][-1] == '\n':
                            continue
                        lines[j] = '\n' + lines[j] # контекстные помечаем по другому
                else:
                    for j in range(i + 1, len(lines)):
                        if lines[j][-1] == '\n':
                            continue
                        lines[j] = '\n' + lines[j] # контекстные помечаем по другому
                        
    if params.before_context != 0:
        for i in range(len(lines)):
            if lines[i][-1] == '\n':
                if i - params.before_context >= 0:
                    for j in range(i - params.before_context, i):
                        if lines[j][-1] == '\n':
                            continue
                        lines[j] = '\n' + lines[j] # контекстные помечаем по другому
                else:
                    for j in range(0, i):
                        if lines[j][-1] == '\n':
                            continue
                        lines[j] = '\n' + lines[j] # контекстные помечаем по другому
    
    # ну а теперь сам вывод
    if params.count:
        k = 0
        for i in range(len(lines)):
            if lines[i][-1] == '\n' or lines[i][0] == '\n':
                lines[i] = lines[i].strip()
                k += 1
        output(str(k))
    elif params.line_number:
        for i in range(len(lines)):
            if lines[i][-1] == '\n':
                lines[i] = lines[i].rstrip()
                s = str(i + 1) + ':' + lines[i]
                output(s)
            if lines[i][0] == '\n':
                lines[i] = lines[i].lstrip()
                s = str(i + 1) + "-" + lines[i]
                output(s)
    else:
        for i in range(len(lines)):
            if lines[i][-1] == '\n' or lines[i][0] == '\n':
                lines[i] = lines[i].strip()
                output(lines[i])

        
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

