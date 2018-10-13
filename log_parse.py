# -*- encoding: utf-8 -*-
from urllib.parse import urlparse 
import re
from datetime import datetime
from collections import Counter

def get_url(line):
    url = re.search(' [^\[\]\s"]+ ', line)[0].strip()
    url_parser = urlparse(url)            
    return "{}{}".format(url_parser.netloc, url_parser.path)
    

def without_www(ignore_www, url):
    if ignore_www:
        if url.startswith('www.'):
            return url[4:]
    return url

def isStart(start_at, line):
    if start_at:
        data = datetime.strptime(line[1:line.index(']')], '%d/%b/%Y %X')
        if data < start_at:
            return True
    return False

def isStop(stop_at, line):
    if stop_at:
        data = datetime.strptime(line[1:line.index(']')], '%d/%b/%Y %X')
        if data > stop_at:
            return True
    return False

def isIgnore_files(ignore_files, URL):
    if ignore_files and URL[-1] != '/' and re.search('\..{2,4}',URL[-5:]):
        return True
    return False

def isRequest_type(request_type, line):
    line = re.search("[A-Z]{3,4}", line)[0]
    
    if request_type == line:
        return False
    return True

def isIgnore_urls(ignore_urls, URL):
    ignore_set = set(ignore_urls)
    if URL in ignore_set:
        return True
    return False
    
def log(line):
    if re.fullmatch('\[\d{2}/[a-zA-Z]{3}/\d{4} \d{2}\:\d{2}\:\d{2}\] "[A-Z]{3,4} [^\[\]\s"]+ .+" \d* \d*\n', line):
        return True
    return False


def  top_slow(d, line, URL):
    time = int(line[line.rfind(" ")+1:])
    if d.get(URL):
        d[URL][0] += 1
        d[URL][1] += time
    else:
        d[URL] = [1, time]

def parse(
    ignore_files=False,
    ignore_urls=[],
    start_at=None,
    stop_at=None,
    request_type=None,
    ignore_www=False,
    slow_queries=False
):
    slow_dict = {}
    counter = Counter()
    f = open('log.log')
    
    for line in f:
        
        if log(line):

            if isRequest_type(request_type, line):
                continue

            if isStart(start_at, line):
                continue

            if isStop(stop_at, line):
                break

            URL = get_url(line)

            if isIgnore_files(ignore_files, URL):
                continue

            if isIgnore_urls(ignore_urls, URL):
                continue
                
            URL = without_www(ignore_www, URL)

            if slow_queries:
                top_slow(slow_dict, line, URL)
            else:
                counter[URL] += 1

    if slow_queries:
        new_list = [value[1]//value[0] for value in slow_dict.values()]
        sorted_list = sorted(new_list, reverse = True)
        if len(sorted_list) >= 5:
            return [sorted_list[i] for i in range(5)]
        else:
            return [sorted_list[i] for i in range(len(sorted_list))]
    else:
        return [item[1] for item in counter.most_common(5)]

        
def main():
    print(parse(slow_queries=False, request_type = 'GET'))

if __name__ == '__main__':
    main()
