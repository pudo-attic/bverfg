
# Library, die in Auswertungsskripte rein kommt
from glob import glob
from lxml import html

def files():
    for entry in glob('entscheidungen/*'):
        if entry.endswith('.html'):
            yield entry

def docs():
    for entry in files():
        fh = open(entry, 'rb')
        content = fh.read()
        fh.close()
        doc = html.fromstring(content)
        doc.filename = entry
        yield doc

def text_body(doc):
    paras = doc.cssselect('.absatz .std')
    paras = [p.xpath('string()') for p in paras]
    return '\n\n'.join(paras)

def text_signature(doc):
    zit = doc.cssselect('p.zitierung')
    az = None
    if len(zit) and zit[0].text:
        az = zit[0].text.split('BVerfG,', 1)[-1].split('vom', 1)[0]
    if az is None:
        azs = doc.cssselect('p.az2')
        if len(azs):
            az = azs.pop().text
    if az is None:
        azs = doc.cssselect('p.lsz')
        if len(azs):
            az = azs.pop().text
    if az is None:
        return None
    return az.strip().strip('-').strip()

if __name__ == '__main__':
    for doc in docs():
        print [doc.find('.//title').text]



