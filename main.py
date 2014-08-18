import requests
from lxml import html
import base64
import os
from collections import defaultdict

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
        ret = ""
        if str(element.tag) == "link":
            try:
                ret = element.attrib['href']
            except:
                ret=""
        else:
            try:
                ret = element.text
                ret = shit.encode('ascii', 'ignore')
            except:
                ret = ""
            
        self.nodes.append(depth * "\t" + str(element.tag) + " " + ret)

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

# level with maximum number of elements
class ASD(object): 
    def __init__(self):
        self.parents = {}
    def __call__(self, element, depth, parent):
        if parent not in self.parents:
            self.parents[parent]=defaultdict(int)
        if len(element.getchildren()) > 0:
            self.parents[parent][str(element.tag)]+=1

    def result(self):
        partial = []
        for parent in self.parents.values():
            if parent:
                partial.append(max(parent.iteritems(), key=lambda x:x[1]))
        maximum = max(partial, key = lambda x:x[1]) 
        return maximum


def main(): 
    with open("urls", "r") as f:
        urls = [x.strip("\n") for x in f.readlines()]

    proxy = Proxy()
    with open("output", "w") as f:
        for url in urls:
            print url
            content = proxy.get(url)
            root = html.document_fromstring(content)
            asd = ASD()
            dfs(root, asd)

            line = "%s %s\n"%(str(asd.result()), url)

            print line
            f.write(line)

#            printer = Printer() 
#            dfs(root, printer)
#            f.write(printer.result())


if __name__ == "__main__":
    main()
