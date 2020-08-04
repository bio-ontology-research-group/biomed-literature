from biolit.esquery import termcounts
from biolit.npmi import scores
from biolit.sandbox.terms import read_terms
import json

def pairs(terms1, rnode1, terms2, rnode2, index='pmc'):
    r = list()
    for i in terms1[rnode1]['children']:
        cname = terms1[i]['name']
        cq = cname.replace(' ', ' AND ')
        xpm = termcounts(cq, index=index)
        for j in terms2[rnode2]['children']:
            dname = terms2[j]['name']
            dq = dname.replace(' ', ' AND ')
            s = scores(cq, dq, index=index, x=xpm)
            if s is not None:
                r.append({
                    'pair': (i, j),
                    'name': (cname, dname),
                    'score': s
                })
    return r


def test_do_pairs():
    do = read_terms("../../../ontrepository/doid.obo")
    assert len(do['DOID:874']['children']) == 6
    assert len(do['DOID:8469']['children']) == 2
    r = pairs(do, 'DOID:874', do, 'DOID:8469', index='pubmed')
    print(json.dumps(r, indent=4))
    assert len(r) == 8
    r = pairs(do, 'DOID:874', do, 'DOID:8469')
    print(json.dumps(r, indent=4))
    assert len(r) == 8
