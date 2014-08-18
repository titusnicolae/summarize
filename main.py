import requests
from lxml import html


class Counter(object):
    counter = 0

    def __call__(self, *args, **kwargs):
        self.counter += 1


def dfs(node, fun, depth=0):
    for child in node.getchildren():
        fun(child, depth)
        dfs(child, fun, depth + 1)


class Printer(object):
    nodes = []

    def __call__(self, element, depth):
        self.nodes.append(depth * "\t" + element.tag)

    def result(self):
        return "\n".join(self.nodes)


def main():
    with open("urls", "r") as f:
        urls = [x.strip("\n") for x in f.readlines()]

    response = requests.get(urls[0])
    content = response.content
    root = html.document_fromstring(content)

    #count number of nodes
    counter = Counter()
    dfs(root, counter)
    print counter.counter, "nodes"

    #output tree to file
    printer = Printer()
    dfs(root, printer)

    with open("output", "w") as f:
        f.write(printer.result())


if __name__ == "__main__":
    main()
