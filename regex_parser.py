"""
Parser module
Takes a W3C formated log-line and stores relevant information
NB: a W3C formated log-line should look like this:
127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /test/image.jpg HTTP/1.0" 200 2326
"""
import re

W3C_REGEX = re.compile(r'\A\S+ \S+ (?P<userid>\S+) \S+ \S+ "(?P<method>\S+) '
                       r'(?P<request>/(?P<section>[^/]*)(?:/\S*)?) \S+" (?P<status>\d{3}) (?P<size>\d+)')
STRING_FIELD_LIST = ["userid", "method", "request", "section", "status"]


def parse(log_line):
    parsed_line = dict()
    try:
        match = W3C_REGEX.match(log_line)
        if not match:
            raise ValueError
    except ValueError:
        print("Request not W3C formated")
    else:
        parsed_line["size"] = int(match.group("size")) # we need to cast it to use it as an (int)
        for field in STRING_FIELD_LIST:
            parsed_line[field] = match.group(field)
        return parsed_line


if __name__ == '__main__':
    string = '127.0.0.1 user-identifier frank [10/Oct/2000:13:55:36 -0700] "GET /test/image.jpg HTTP/1.0" 200 2326'
    parsed = parse(string)
    for field in parsed.keys():
        print(field, ": ", parsed[field])
