from lxml import html
import os

CWD = os.path.dirname(os.path.abspath(__file__))


def find_links(filename):
    tree = html.parse(filename)
    XPATH = '//a[contains(text(),"GET THIS BOOK")]'
    elements = tree.xpath(XPATH)
    links = [e.get("href") for e in elements]
    return set(links)


def get_all_links():
    dirs = os.listdir(CWD)
    links = set()
    for d in dirs:
        if not os.path.isdir(os.path.join(CWD, d)):
            continue
        fname = os.path.join(CWD, d, "index.html")
        if not os.path.isfile(fname):
            continue
        links.update(find_links(fname))
    return links


if __name__ == "__main__":
    links = get_all_links()
    with open("links.txt", "w+") as f:
        f.write("\n".join(links))
