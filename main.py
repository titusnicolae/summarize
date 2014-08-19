#!/usr/bin/python
import requests
from lxml import etree
import base64
import os
from collections import defaultdict
from pprint import pprint


class Counter(object):
    counter = 0

    def __call__(self, *args, **kwargs):
        self.counter += 1


def dfs(node, fun, depth=0):
    for child in node.getchildren():
        fun(child, depth, node)
        dfs(child, fun, depth + 1)


class Printer(object):
    nodes = []

    def __call__(self, element, depth, *args, **kwargs):
        text = element.text or ""
        text = (text.encode('ascii', 'ignore').replace("\n", "")
                .replace("\r", "").strip(" "))
        tag = str(element.tag).replace("\n", "").replace("\r", "")
        items = str(element.items()).replace("\n", "").replace("\r", "")

        ss = "%s%s %s %s" % (depth * "\t", text, tag, items)
        print ss
#        import ipdb; ipdb.set_trace()
        self.nodes.append(ss)

    def result(self):
        self.nodes.append("")
        return "\n".join(self.nodes)


class ItemFetcher(object):
    items = []

    def __call__(self, element, *args, **kwargs):
        if str(element.tag) == "tag":
            items.append(element)


class TestItem(object):
    has_item = False

    def __call__(self, element, *args, **kwargs):
        if str(element.tag) in ["item", "entry", "airlist"]:
            self.has_item = True


class Proxy(object):
    @staticmethod
    def get(url):
        folder = "proxy/"
        filename = folder + base64.urlsafe_b64encode(str(hash(url)))

        if os.path.isfile(filename):
            with open(filename, "r") as f:
                return f.read()

        else:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0"}

            response = requests.get(url, verify=False, headers=headers)
            with open(filename, "w") as f:
                f.write(response.content)
            return response.content


#caching
def has_url(element):
    if "http" in str(element.tag):
        return True
    if element.text and "http" in str(element.text.encode('ascii', 'ignore')):
        return True
    for child in element.getchildren():
        if has_url(child):
            return True
    return False


class ASD2(object):

    def __init__(self):
        self.parents = {}

    def __call__(self, element, depth, parent):
        if has_url(element):
            if parent not in self.parents:
                self.parents[parent] = defaultdict(int)
            self.parents[parent][str(element.tag)] += 1

    def result(self):
        partial = []
        for parent, children in self.parents.iteritems():
            if children:
                max_child = max(children.iteritems(), key=lambda x: x[1])
                partial.append((parent, max_child))

        if partial:
            maximum = max(partial, key=lambda x: x[1][1])
            return maximum
        return None


class Debug(object):
    def __init__(self):
        self.parents = {}

    def __call__(self, element, depth, parent):
        if str(element.tag) == "link":
            import ipdb; ipdb.set_trace()


def clean(content):
    return content.strip(" \r\n").replace("&", "&amp;")


def get_link(element):
    if "http" in str(element.tag):
        return str(element.tag)
    if element.text and "http" in str(element.text.encode('ascii', 'ignore')):
        return str(element.text.encode('ascii', 'ignore'))

    for child in element.getchildren():
        ret = get_link(child)
        if ret:
            return ret
    return None


def children(element, tag):
    ret = []
    for child in element.getchildren():
        if str(child.tag) == tag:
            link = get_link(child)
            if link:
                ret.append(link)

    return '\t' + '\n\t'.join(ret) + '\n'


def main():
    with open("urls", "r") as f:
        urls = [x.strip("\n") for x in f.readlines()]

    proxy = Proxy()
    with open("output", "w") as f:
            for url in urls:
                content = clean(proxy.get(url))
                #root = html.document_fromstring(content)
                try:
                    root = etree.fromstring(content)
                except Exception as e:
                    pass

                printer = Printer()
                dfs(root, printer)
                f.write(printer.result() + "\n")

                asd = ASD2()
                dfs(root, asd)
                result = asd.result()
                if result:
                    line = "%s %s\n" % (str(result), url)
                    f.write(line)
                    f.write(children(result[0], result[1][0]))
                    return


if __name__ == "__main__":
    main()
    print "done"
