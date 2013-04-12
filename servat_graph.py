import requests
import networkx as nx

from lxml import html
from urlparse import urljoin


def get_volumes():
    base = 'http://www.servat.unibe.ch/dfr/dfr_bvbd120.html'
    doc = html.parse(base)
    for ref in doc.findall('//a'):
        link = ref.get('href')
        if link and 'dfr_bvbd' in link:
            yield urljoin(base, link)

def get_verdicts():
    for volume in get_volumes():
        doc = html.parse(volume)
        for ref in doc.findall('.//li//a'):
            if 'http://' in ref.get('href'):
                continue
            yield urljoin(volume, ref.get('href'))

def get_connections():
    for verdict in get_verdicts():
        doc = html.parse(verdict)
        verdict_title = doc.find('//td/font/b').text
        for b in doc.findall('//table//table//b'):
            if 'Zitiert durch' in b.text:
                for link in b.getnext().getnext().findall('a'):
                    if not 'BVerfGE' in link.text:
                        continue
                    title = link.text + link.tail
                    yield (title, link.get('href'), verdict_title, verdict)

            if 'Zitiert selbst' in b.text:
                for link in b.getnext().getnext().findall('a'):
                    if not 'BVerfGE' in link.text:
                        continue
                    title = link.text + link.tail
                    yield (verdict_title, verdict, title, link.get('href'))


def make_graph():
    G = nx.DiGraph()
    #print dir(G)
    for (from_title, from_url, to_title, to_url) in get_connections():
        print from_url
        if not G.has_node(from_url):
            cit, label = from_title.split('-', 1)
            G.add_node(from_url, label=label, citation=cit)
        if not G.has_node(to_url):
            cit, label = to_title.split('-', 1)
            G.add_node(to_url, label=label, citation=cit)
        if not G.has_edge(from_url, to_url):
            G.add_edge(from_url, to_url)
        #print G.size()
        #break
    nx.write_gexf(G, 'servat_bverfge_only_notag.gexf')

make_graph()

