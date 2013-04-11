import networkx as nx

import decisions
import re

DECISION_RE = re.compile('[\(;].{0,15}(BVerfG[EK] [^<);.]*)')

def find_citations(doc):
    text = decisions.text_body(doc)
    signature = decisions.text_signature(doc)
    for match in DECISION_RE.findall(text):
        if match is None:
            continue
        match = match.strip()
        yield [signature, match]

def to_graph():
    G=nx.Graph()
    for doc in decisions.docs():
        for (src, dst) in find_citations(doc):
            G.add_edge(src, dst)

if __name__ == '__main__':
    to_graph('citations.gexf')

