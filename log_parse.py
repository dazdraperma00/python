# -*- encoding: utf-8 -*-
from urllib.parse import urlparse 
import operator
import re
from datetime import datetime

def whereURL(line):
    try:
        k1 = line.index('"')
        k1 = line.index(" ", k1)
        k2 = line.index(" ", k1 + 1)
        line = line[k1 + 1: k2]
    except ValueError:
        return False
    return urlparse(line)

def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    d = {}
    f = open('log.log')
    for line in f:
        
        if line[0] == "[":
            
            url_parser = whereURL(line)
            
            if not url_parser:
                continue

            URL = "{}{}".format(url_parser.netloc, url_parser.path)

            if request_type:
                k = line.index('"')
                if request_type != line[k + 1 : k + 4]:
                    continue

            if start_at:
                data = datetime.strptime(line[1:line.index(']')], '%d/%b/%Y %X')
                if data < start_at:
                    continue

            if stop_at:
                data = datetime.strptime(line[1:line.index(']')], '%d/%b/%Y %X')
                if data > stop_at:
                    break

            
            if ignore_files:
                if URL[-1] == '/' and re.search('\..{3,4}',URL[-5:]):
                    continue

            if ignore_urls:
                Flag = False
                for i_url in ignore_urls:
                    if URL == i_url:
                        Flag = True
                if Flag:
                    continue
            
            if ignore_www:
                if URL.startswith('www'):
                    URL = URL[4:]


            if slow_queries:
                time = int(line[line.rfind(" ")+1:])
                if d.get(URL):
                    d[URL][0] += 1
                    d[URL][1] += time
                else:
                    d[URL] = [1, time]
            else:
                if d.get(URL):
                    d[URL] += 1
                else:
                    d[URL] = 1

    if slow_queries:
        if len(d) == 0:
            return []
        new_list = []
        for value in d.values():
            new_list.append(value[1]//value[0])
            
        new_list = sorted(new_list, reverse = True)
        
        return [new_list[i] for i in range(5)]

    else:
        if len(d) == 0:
            return []
        sorted_d = sorted(d.items(), reverse = True, key = operator.itemgetter(1))
    
        return [sorted_d[i][1] for i in range(5)]
                 
"""
    sorted_d = sorted(d.values(), reverse = True)
    
    for i in range(5):
        new_list.append(sorted_d[i])
    return new_list
"""

def main():
    print(parse())

if __name__ == '__main__':
    main()
