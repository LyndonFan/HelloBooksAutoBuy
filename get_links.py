from bs4 import BeautifulSoup
import json
import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))


def find_links(filename):
    with open(filename, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    elements = soup.find_all('a')
    links = [e['href'] for e in elements]
    links = set(l for l in links if 'geni.us/' in l)
    return links


def get_all_links():
    dirs = os.listdir(CWD)
    links = set()
    for d in dirs:
        if 'Hello_Books__' in d:
            fname = os.path.join(CWD, d, 'index.html')
            links.update(find_links(fname))
    return links


if __name__ == '__main__':
    links = get_all_links()
    with open('links.txt', 'w+') as f:
        f.write('\n'.join(links))
