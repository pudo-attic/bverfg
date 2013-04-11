import requests
import os
import json
from urlparse import urljoin
from lxml import html

def indexes():
    base = 'http://www.bundesverfassungsgericht.de/entscheidungen/%s/%s'
    for year in range(1998, 2014):
        for month in range(1, 13):
            yield base % (year, month)

def read_index(url):
    doc = html.parse(url)
    for az in doc.findall('//div[@class="entscheidung"]/div[@class="aktenzeichen"]/a'):
        yield urljoin(url, az.get('href'))

def store(url):
    path = os.path.join('entscheidungen', url.rsplit('/', 1)[-1])
    res = requests.get(url)
    fh = open(path, 'wb')
    fh.write(res.content)
    fh.close()

if __name__ == '__main__':
    for url in indexes():
        for verdict in read_index(url):
            print verdict
            store(verdict)
